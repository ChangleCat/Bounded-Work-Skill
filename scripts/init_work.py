#!/usr/bin/env python3
"""Initialize a new bootstrap-only bounded-work control plane without overwriting files."""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

from _common import ControlError, load_yaml, utc_now, write_yaml_exclusive
from validate_work import validate_root


SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSET_ROOT = SKILL_ROOT / "assets"


def _render(template: Path, replacements: dict[str, str]) -> str:
    text = template.read_text(encoding="utf-8")
    for token, value in replacements.items():
        text = text.replace("{{" + token + "}}", value)
    unresolved = [part.split("}}", 1)[0] for part in text.split("{{")[1:] if "}}" in part]
    if unresolved:
        raise ControlError(f"unresolved template tokens in {template.name}: {unresolved}")
    return text


def initialize(
    root: Path,
    *,
    title: str,
    owner: str,
    authority_source: str,
    claim_statements: list[str],
    migration: bool,
) -> Path:
    root = root.expanduser().resolve(strict=False)
    if not title.strip() or not owner.strip() or not authority_source.strip():
        raise ControlError("title, owner, and authority source must be non-empty")
    if not claim_statements or any(not claim.strip() for claim in claim_statements):
        raise ControlError("at least one non-empty observable claim is required")
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise ControlError(f"refusing to overwrite non-empty work root: {root}")

    state_template = (
        ASSET_ROOT / "workflows/migration/migration-state.template.yaml"
        if migration
        else ASSET_ROOT / "work-control/work-state.template.yaml"
    )
    state_name = "migration-state.yaml" if migration else "work-state.yaml"
    item_id = "M0-001" if migration else "W0-001"
    stage = "baseline" if migration else "stage-0"

    state = load_yaml(state_template)
    state["work_title"] = title.strip()
    state["current_stage"] = stage
    state["next_items"] = [item_id]

    registry = load_yaml(ASSET_ROOT / "work-control/work-registry.template.yaml")
    item = registry["items"][0]
    item.update(
        {
            "id": item_id,
            "title": "Accept the work charter and claim coverage",
            "stage": stage,
            "owner": owner.strip(),
            "card": f"work-items/{stage}/{item_id}.md",
        }
    )

    claims = load_yaml(ASSET_ROOT / "work-control/claims.template.yaml")
    claims["items"] = [
        {
            "id": f"CLM-{index:03d}",
            "statement": statement.strip(),
            "status": "active",
            "owner": owner.strip(),
        }
        for index, statement in enumerate(claim_statements, start=1)
    ]

    authorization = load_yaml(ASSET_ROOT / "work-control/authorization.template.yaml")
    authorization.update(
        {
            "source": authority_source.strip(),
            "granted_by": owner.strip(),
            "granted_at": utc_now(),
        }
    )

    validate_command = " ".join(
        shlex.quote(part)
        for part in (
            sys.executable,
            str(SKILL_ROOT / "scripts/validate_work.py"),
            str(root),
        )
    )
    replacements = {
        "WORK_TITLE": title.strip(),
        "OUTCOME": title.strip(),
        "WORK_ROOT": str(root),
        "AUTHORITY_SOURCE": authority_source.strip(),
        "ITEM_ID": item_id,
        "STAGE": stage,
        "OWNER": owner.strip(),
        "VALIDATE_COMMAND": validate_command,
    }
    charter = _render(ASSET_ROOT / "work-control/work-charter.template.md", replacements)
    card = _render(ASSET_ROOT / "work-control/bootstrap-card.template.md", replacements)

    root.mkdir(parents=True, exist_ok=True)
    (root / "evidence").mkdir()
    card_directory = root / "work-items" / stage
    card_directory.mkdir(parents=True)
    write_yaml_exclusive(root / state_name, state)
    write_yaml_exclusive(root / "work-registry.yaml", registry)
    write_yaml_exclusive(root / "claims.yaml", claims)
    write_yaml_exclusive(root / "authorization.yaml", authorization)
    with (root / "work-charter.md").open("x", encoding="utf-8") as handle:
        handle.write(charter)
    with (card_directory / f"{item_id}.md").open("x", encoding="utf-8") as handle:
        handle.write(card)
    (root / "journal.jsonl").touch(exist_ok=False)

    diagnostics, _ = validate_root(root)
    errors = [diagnostic for diagnostic in diagnostics if diagnostic.level == "error"]
    if errors:
        details = "; ".join(f"{error.code}: {error.message}" for error in errors)
        raise ControlError(f"initialized files but deterministic validation failed: {details}")
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_root", type=Path)
    parser.add_argument("--title", required=True, help="Outcome-oriented work title")
    parser.add_argument("--owner", required=True, help="Owner of the bootstrap decision")
    parser.add_argument(
        "--authority-ref",
        required=True,
        help="Durable source of the user's Frame/Bootstrap authority",
    )
    parser.add_argument(
        "--claim",
        action="append",
        required=True,
        dest="claims",
        help="Observable success claim; repeat for multiple claims",
    )
    parser.add_argument("--migration", action="store_true", help="Use the migration specialization state")
    args = parser.parse_args()
    try:
        root = initialize(
            args.work_root,
            title=args.title,
            owner=args.owner,
            authority_source=args.authority_ref,
            claim_statements=args.claims,
            migration=args.migration,
        )
    except (ControlError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Initialized bootstrap-only bounded work at {root}")
    print("Execute authority was not granted. Review the charter and first eligible card before widening authority.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
