"""Shared, fail-closed helpers for the bounded-work reference tools."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


STATE_NAMES = ("work-state.yaml", "migration-state.yaml")


class ControlError(ValueError):
    """A malformed or ambiguous control plane."""


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ControlError(f"{field} must be a non-empty RFC3339 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ControlError(f"{field} is not a valid RFC3339 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ControlError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ControlError(f"missing required file: {path}") from exc
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ControlError(f"cannot safely read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ControlError(f"expected a YAML mapping in {path}")
    return value


def write_yaml_exclusive(path: Path, value: dict[str, Any]) -> None:
    with path.open("x", encoding="utf-8") as handle:
        yaml.safe_dump(value, handle, sort_keys=False, allow_unicode=True)


def normalize_relative(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ControlError(f"{field} must be a non-empty relative path")
    if "\\" in value:
        raise ControlError(f"{field} must use portable forward-slash separators: {value!r}")
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ControlError(f"{field} must stay inside the work root: {value!r}")
    normalized = candidate.as_posix()
    if normalized in ("", "/"):
        raise ControlError(f"{field} must name a path inside the work root")
    return normalized


def resolve_relative(
    root: Path,
    value: Any,
    field: str,
    *,
    must_exist: bool = True,
) -> Path:
    normalized = normalize_relative(value, field)
    resolved_root = root.resolve()
    candidate = (resolved_root / normalized).resolve(strict=False)
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ControlError(f"{field} escapes the work root through a symlink: {value!r}") from exc
    if must_exist and not candidate.exists():
        raise ControlError(f"{field} does not exist: {value!r}")
    return candidate


def find_state(root: Path) -> Path:
    resolved_root = root.resolve()
    matches: list[Path] = []
    for name in STATE_NAMES:
        candidate = root / name
        if not candidate.is_file():
            continue
        resolved = candidate.resolve()
        try:
            resolved.relative_to(resolved_root)
        except ValueError as exc:
            raise ControlError(f"state file escapes the work root through a symlink: {name}") from exc
        matches.append(resolved)
    if len(matches) != 1:
        names = ", ".join(path.name for path in matches) or "none"
        raise ControlError(
            f"expected exactly one state file ({', '.join(STATE_NAMES)}); found {names}"
        )
    return matches[0]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_card(path: Path) -> tuple[dict[str, Any], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ControlError(f"cannot read card {path}: {exc}") from exc
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ControlError(f"card is missing YAML frontmatter: {path}")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ControlError(f"card has unterminated YAML frontmatter: {path}") from exc
    try:
        frontmatter = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as exc:
        raise ControlError(f"cannot safely parse card frontmatter {path}: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise ControlError(f"card frontmatter must be a mapping: {path}")
    return frontmatter, text


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ControlError(f"missing required file: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ControlError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ControlError(f"expected a JSON object in {path}")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    if path.is_symlink():
        raise ControlError(f"refusing to replace a symlinked JSON control file: {path}")
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def scope_contains(allowed: str, requested: str) -> bool:
    allowed_path = PurePosixPath(normalize_relative(allowed, "allowed_scope"))
    requested_path = PurePosixPath(normalize_relative(requested, "write_scope"))
    if allowed_path.as_posix() == ".":
        return True
    return requested_path == allowed_path or allowed_path in requested_path.parents


def scopes_overlap(left: str, right: str) -> bool:
    left_path = PurePosixPath(normalize_relative(left, "write_scope"))
    right_path = PurePosixPath(normalize_relative(right, "write_scope"))
    return (
        left_path == right_path
        or left_path in right_path.parents
        or right_path in left_path.parents
    )
