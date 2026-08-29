#!/usr/bin/env python3
"""Create and verify SHA-256 attestations for stable bounded-work control artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _common import (
    ControlError,
    load_json,
    normalize_relative,
    resolve_relative,
    sha256_file,
    utc_now,
    write_json_atomic,
)


MANIFEST_NAME = ".bounded-work-attestations.json"


def _empty_manifest() -> dict[str, Any]:
    return {"schema_version": 1, "artifacts": {}}


def _load_manifest(root: Path, *, required: bool) -> dict[str, Any]:
    path = root / MANIFEST_NAME
    if path.is_symlink():
        raise ControlError(f"attestation manifest must not be a symlink: {path}")
    if not path.exists():
        if required:
            raise ControlError(f"missing attestation manifest: {path}")
        return _empty_manifest()
    manifest = load_json(path)
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("artifacts"), dict):
        raise ControlError(f"malformed attestation manifest: {path}")
    return manifest


def attest(root: Path, paths: list[str], actor: str, authority_ref: str) -> dict[str, Any]:
    if not actor.strip() or not authority_ref.strip():
        raise ControlError("actor and authority reference must be non-empty")
    manifest = _load_manifest(root, required=False)
    for value in paths:
        relative = normalize_relative(value, "artifact path")
        if relative == MANIFEST_NAME:
            raise ControlError("the attestation manifest cannot attest itself")
        path = resolve_relative(root, relative, "artifact path")
        if not path.is_file():
            raise ControlError(f"only regular files can be attested: {relative}")
        manifest["artifacts"][relative] = {
            "sha256": sha256_file(path),
            "attested_at": utc_now(),
            "actor": actor.strip(),
            "authority_ref": authority_ref.strip(),
        }
    write_json_atomic(root / MANIFEST_NAME, manifest)
    return manifest


def verify(root: Path, paths: list[str] | None) -> tuple[dict[str, Any], bool]:
    manifest = _load_manifest(root, required=True)
    requested = paths or sorted(manifest["artifacts"])
    results: list[dict[str, Any]] = []
    valid = True
    if not requested:
        raise ControlError("attestation manifest contains no artifacts")
    for value in requested:
        relative = normalize_relative(value, "artifact path")
        record = manifest["artifacts"].get(relative)
        if not isinstance(record, dict):
            results.append({"path": relative, "valid": False, "reason": "not attested"})
            valid = False
            continue
        try:
            path = resolve_relative(root, relative, "artifact path")
        except ControlError as exc:
            results.append({"path": relative, "valid": False, "reason": str(exc)})
            valid = False
            continue
        actual = sha256_file(path) if path.is_file() else None
        expected = record.get("sha256")
        digest_valid = isinstance(expected, str) and len(expected) == 64
        if digest_valid:
            try:
                int(expected, 16)
            except ValueError:
                digest_valid = False
        record_valid = all(
            isinstance(record.get(field), str) and record[field].strip()
            for field in ("actor", "authority_ref", "attested_at")
        )
        matches = digest_valid and record_valid and actual == expected.lower()
        results.append(
            {
                "path": relative,
                "valid": matches,
                "expected_sha256": record.get("sha256"),
                "actual_sha256": actual,
                "actor": record.get("actor"),
                "authority_ref": record.get("authority_ref"),
                "attested_at": record.get("attested_at"),
                "reason": None if matches else "digest mismatch",
            }
        )
        valid = valid and matches
    return {"valid": valid, "artifacts": results}, valid


def clear(root: Path, paths: list[str]) -> dict[str, Any]:
    manifest = _load_manifest(root, required=True)
    missing: list[str] = []
    removed: list[str] = []
    for value in paths:
        relative = normalize_relative(value, "artifact path")
        if relative not in manifest["artifacts"]:
            missing.append(relative)
            continue
        del manifest["artifacts"][relative]
        removed.append(relative)
    if missing:
        raise ControlError(f"cannot clear unattested paths: {', '.join(missing)}")
    write_json_atomic(root / MANIFEST_NAME, manifest)
    return {"removed": removed, "remaining": sorted(manifest["artifacts"])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_root", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    attest_parser = subparsers.add_parser("attest", help="Record current digests")
    attest_parser.add_argument("paths", nargs="+")
    attest_parser.add_argument("--actor", required=True)
    attest_parser.add_argument("--authority-ref", required=True)

    verify_parser = subparsers.add_parser("verify", help="Verify recorded digests")
    verify_parser.add_argument("paths", nargs="*")

    subparsers.add_parser("show", help="Show the manifest")

    clear_parser = subparsers.add_parser("clear", help="Remove only named attestation records")
    clear_parser.add_argument("paths", nargs="+")

    args = parser.parse_args()
    root = args.work_root.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: work root does not exist: {root}", file=sys.stderr)
        return 2
    try:
        if args.command == "attest":
            payload = attest(root, args.paths, args.actor, args.authority_ref)
            valid = True
        elif args.command == "verify":
            payload, valid = verify(root, args.paths or None)
        elif args.command == "show":
            payload = _load_manifest(root, required=True)
            valid = True
        else:
            payload = clear(root, args.paths)
            valid = True
    except (ControlError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.command == "verify":
        for artifact in payload["artifacts"]:
            print(f"{'PASS' if artifact['valid'] else 'FAIL'}: {artifact['path']}")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
