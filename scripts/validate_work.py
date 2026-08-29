#!/usr/bin/env python3
"""Read-only, fail-closed validation for a bounded-work control plane."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from _common import (
    ControlError,
    find_state,
    load_json,
    load_yaml,
    normalize_relative,
    parse_card,
    parse_time,
    resolve_relative,
    scope_contains,
    scopes_overlap,
    sha256_file,
)


ITEM_STATUSES = {
    "planned",
    "ready",
    "in_progress",
    "completed",
    "blocked",
    "canceled",
    "superseded",
}
TERMINAL_WORK_STATUSES = {"completed", "canceled", "superseded"}
MODES = {"frame", "bootstrap", "execute", "audit"}
SUSPICIOUS_CONTROL_PHRASES = (
    "ignore previous instructions",
    "ignore all previous",
    "override the system prompt",
    "reveal your system prompt",
)


@dataclass(frozen=True)
class Diagnostic:
    level: str
    code: str
    message: str
    path: str | None = None


class Validator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.diagnostics: list[Diagnostic] = []

    def error(self, code: str, message: str, path: Path | str | None = None) -> None:
        self.diagnostics.append(Diagnostic("error", code, message, self._display(path)))

    def warn(self, code: str, message: str, path: Path | str | None = None) -> None:
        self.diagnostics.append(Diagnostic("warning", code, message, self._display(path)))

    def _display(self, path: Path | str | None) -> str | None:
        if path is None:
            return None
        candidate = Path(path)
        try:
            return candidate.resolve(strict=False).relative_to(self.root).as_posix()
        except (OSError, ValueError):
            return str(path)

    def guarded(self, code: str, callback: Any, path: Path | str | None = None) -> Any:
        try:
            return callback()
        except ControlError as exc:
            self.error(code, str(exc), path)
            return None


def _as_string_list(value: Any, field: str, validator: Validator, path: Path) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        validator.error("invalid-list", f"{field} must be a list of strings", path)
        return []
    if len(value) != len(set(value)):
        validator.error("duplicate-list-entry", f"{field} contains duplicate entries", path)
    return value


def _validate_authorization(
    validator: Validator,
    path: Path,
) -> dict[str, Any] | None:
    auth = validator.guarded("authorization-read", lambda: load_yaml(path), path)
    if auth is None:
        return None
    if auth.get("schema_version") != 1:
        validator.error("authorization-schema", "authorization schema_version must be 1", path)
    if auth.get("status") != "active":
        validator.error("authorization-inactive", "authorization status must be active", path)
    for field in ("source", "granted_by"):
        value = auth.get(field)
        if not isinstance(value, str) or not value.strip() or value.startswith("<"):
            validator.error("authorization-field", f"authorization {field} is missing", path)
    validator.guarded(
        "authorization-time",
        lambda: parse_time(auth.get("granted_at"), "granted_at"),
        path,
    )
    modes = _as_string_list(auth.get("allowed_modes"), "allowed_modes", validator, path)
    unknown_modes = sorted(set(modes) - MODES)
    if unknown_modes:
        validator.error("authorization-mode", f"unknown allowed modes: {unknown_modes}", path)
    scopes = _as_string_list(auth.get("allowed_scope"), "allowed_scope", validator, path)
    if not scopes:
        validator.error("authorization-scope", "authorization must declare allowed_scope", path)
    for index, scope in enumerate(scopes):
        validator.guarded(
            "authorization-scope",
            lambda scope=scope, index=index: normalize_relative(scope, f"allowed_scope[{index}]"),
            path,
        )
    environments = _as_string_list(auth.get("environments"), "environments", validator, path)
    if not environments:
        validator.error("authorization-environment", "authorization must name an environment", path)
    if auth.get("revoked_at") is not None:
        validator.error("authorization-revoked", "authorization has been revoked", path)
    if auth.get("expires_at") is not None:
        expiry = validator.guarded(
            "authorization-expiry",
            lambda: parse_time(auth.get("expires_at"), "expires_at"),
            path,
        )
        if expiry is not None and expiry <= datetime.now(UTC):
            validator.error("authorization-expired", "authorization has expired", path)
    return auth


def _validate_evidence(
    validator: Validator,
    path: Path,
    known_claims: set[str],
    *,
    require_passing: bool,
) -> dict[str, Any] | None:
    evidence = validator.guarded("evidence-read", lambda: load_yaml(path), path)
    if evidence is None:
        return None
    if evidence.get("schema_version") != 1:
        validator.error("evidence-schema", "evidence schema_version must be 1", path)
    claims = _as_string_list(evidence.get("claims"), "claims", validator, path)
    unknown_claims = sorted(set(claims) - known_claims)
    if unknown_claims:
        validator.error("evidence-claims", f"evidence references unknown claims: {unknown_claims}", path)
    result = evidence.get("result")
    validity = evidence.get("validity")
    if result not in {"pass", "fail", "not_run"}:
        validator.error("evidence-result", f"unknown evidence result: {result!r}", path)
    if validity not in {"valid", "stale", "superseded"}:
        validator.error("evidence-validity", f"unknown evidence validity: {validity!r}", path)
    if require_passing and result != "pass":
        validator.error("evidence-result", "completion evidence result must be pass", path)
    if require_passing and validity != "valid":
        validator.error("evidence-stale", "completion evidence validity must be valid", path)
    validator.guarded(
        "evidence-time",
        lambda: parse_time(evidence.get("produced_at"), "produced_at"),
        path,
    )
    if evidence.get("valid_until") is not None:
        expiry = validator.guarded(
            "evidence-expiry",
            lambda: parse_time(evidence.get("valid_until"), "valid_until"),
            path,
        )
        if expiry is not None and expiry <= datetime.now(UTC):
            validator.error("evidence-expired", "evidence validity window has expired", path)
    based_on = evidence.get("based_on")
    if not isinstance(based_on, list):
        validator.error("evidence-bindings", "evidence based_on must be a list", path)
        based_on = []
    if result == "pass" and not based_on:
        validator.warn("evidence-unbound", "passing evidence has no source digest bindings", path)
    for index, binding in enumerate(based_on):
        if not isinstance(binding, dict):
            validator.error("evidence-binding", f"based_on[{index}] must be a mapping", path)
            continue
        source = validator.guarded(
            "evidence-path",
            lambda binding=binding, index=index: resolve_relative(
                validator.root,
                binding.get("path"),
                f"based_on[{index}].path",
            ),
            path,
        )
        expected = binding.get("sha256")
        digest_valid = isinstance(expected, str) and len(expected) == 64
        if digest_valid:
            try:
                int(expected, 16)
            except ValueError:
                digest_valid = False
        if not digest_valid:
            validator.error("evidence-digest", f"based_on[{index}].sha256 is invalid", path)
        elif source is not None and not source.is_file():
            validator.error("evidence-source", f"evidence source is not a regular file: {binding.get('path')}", path)
        elif source is not None and sha256_file(source) != expected.lower() and validity == "valid":
            validator.error(
                "evidence-digest-mismatch",
                f"evidence source changed: {binding.get('path')}",
                path,
            )
    return evidence


def _validate_journal(validator: Validator, path: Path, known_items: set[str]) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        validator.error("journal-read", f"cannot read journal: {exc}", path)
        return
    required = {"at", "actor", "item", "kind", "summary", "evidence"}
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            validator.error("journal-json", f"line {line_number} is invalid JSON: {exc}", path)
            continue
        if not isinstance(event, dict) or not required.issubset(event):
            validator.error("journal-shape", f"line {line_number} lacks required event fields", path)
            continue
        validator.guarded(
            "journal-time",
            lambda event=event: parse_time(event.get("at"), "journal.at"),
            path,
        )
        if event.get("item") is not None and event.get("item") not in known_items:
            validator.error("journal-item", f"line {line_number} references an unknown item", path)
        if not isinstance(event.get("evidence"), list):
            validator.error("journal-evidence", f"line {line_number} evidence must be a list", path)
        summary = event.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            validator.error("journal-summary", f"line {line_number} summary is empty", path)
        elif any(phrase in summary.lower() for phrase in SUSPICIOUS_CONTROL_PHRASES):
            validator.error(
                "journal-instruction-injection",
                f"line {line_number} contains instruction-like external content; store it as evidence instead",
                path,
            )


def _validate_attestation(validator: Validator, card_path: Path) -> None:
    manifest_path = validator.root / ".bounded-work-attestations.json"
    manifest = validator.guarded("attestation-read", lambda: load_json(manifest_path), manifest_path)
    if manifest is None:
        return
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("artifacts"), dict):
        validator.error("attestation-schema", "attestation manifest is malformed", manifest_path)
        return
    relative = card_path.relative_to(validator.root).as_posix()
    record = manifest["artifacts"].get(relative)
    if not isinstance(record, dict):
        validator.error("attestation-missing", f"active Execute card is not attested: {relative}", card_path)
        return
    for field in ("actor", "authority_ref"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            validator.error("attestation-record", f"attestation {relative} has no {field}", manifest_path)
    validator.guarded(
        "attestation-time",
        lambda: parse_time(record.get("attested_at"), "attested_at"),
        manifest_path,
    )
    expected = record.get("sha256")
    digest_valid = isinstance(expected, str) and len(expected) == 64
    if digest_valid:
        try:
            int(expected, 16)
        except ValueError:
            digest_valid = False
    if not digest_valid or expected.lower() != sha256_file(card_path):
        validator.error("attestation-mismatch", f"attested card changed: {relative}", card_path)


def _has_dependency_cycle(items: dict[str, dict[str, Any]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(item_id: str) -> list[str] | None:
        if item_id in visiting:
            start = stack.index(item_id)
            return stack[start:] + [item_id]
        if item_id in visited:
            return None
        visiting.add(item_id)
        stack.append(item_id)
        for dependency in items[item_id].get("depends_on", []):
            if dependency in items:
                cycle = visit(dependency)
                if cycle:
                    return cycle
        stack.pop()
        visiting.remove(item_id)
        visited.add(item_id)
        return None

    for item_id in items:
        cycle = visit(item_id)
        if cycle:
            return cycle
    return None


def validate_root(root: Path) -> tuple[list[Diagnostic], dict[str, Any]]:
    validator = Validator(root)
    context: dict[str, Any] = {"root": str(validator.root)}
    if not validator.root.is_dir():
        validator.error("work-root", "work root does not exist or is not a directory", validator.root)
        return validator.diagnostics, context

    state_path = validator.guarded("state-file", lambda: find_state(validator.root), validator.root)
    if state_path is None:
        return validator.diagnostics, context
    state = validator.guarded("state-read", lambda: load_yaml(state_path), state_path)
    if state is None:
        return validator.diagnostics, context
    context.update({"state_path": str(state_path), "state": state})

    if state.get("schema_version") != 3:
        validator.error("state-schema", "state schema_version must be 3", state_path)
    mode = state.get("operating_mode")
    if mode not in MODES:
        validator.error("state-mode", f"unknown operating_mode: {mode!r}", state_path)
    current_stage = state.get("current_stage")
    if not isinstance(current_stage, str) or not current_stage:
        validator.error("state-stage", "current_stage must be a non-empty string", state_path)

    registry_path = validator.guarded(
        "registry-path",
        lambda: resolve_relative(
            validator.root,
            state.get("item_status_source"),
            "item_status_source",
        ),
        state_path,
    )
    registry = (
        validator.guarded("registry-read", lambda: load_yaml(registry_path), registry_path)
        if registry_path is not None
        else None
    )
    if registry is None:
        return validator.diagnostics, context
    context.update({"registry_path": str(registry_path), "registry": registry})
    if registry.get("schema_version") != 3:
        validator.error("registry-schema", "registry schema_version must be 3", registry_path)
    raw_items = registry.get("items")
    if not isinstance(raw_items, list):
        validator.error("registry-items", "registry items must be a list", registry_path)
        return validator.diagnostics, context

    items: dict[str, dict[str, Any]] = {}
    item_order: list[str] = []
    for index, item in enumerate(raw_items):
        if not isinstance(item, dict):
            validator.error("registry-item", f"items[{index}] must be a mapping", registry_path)
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            validator.error("item-id", f"items[{index}] has no valid id", registry_path)
            continue
        if item_id in items:
            validator.error("item-id-duplicate", f"duplicate item id: {item_id}", registry_path)
            continue
        items[item_id] = item
        item_order.append(item_id)
    context["items"] = items

    active_claims: set[str] = set()
    claim_path: Path | None = None
    artifacts = state.get("artifacts")
    if not isinstance(artifacts, dict):
        validator.error("state-artifacts", "state artifacts must be a mapping", state_path)
        artifacts = {}
    required_artifacts = ("work_charter", "claim_registry", "journal", "evidence_dir")
    resolved_artifacts: dict[str, Path] = {}
    for key in required_artifacts:
        resolved = validator.guarded(
            "artifact-path",
            lambda key=key: resolve_relative(validator.root, artifacts.get(key), f"artifacts.{key}"),
            state_path,
        )
        if resolved is not None:
            resolved_artifacts[key] = resolved
    if "evidence_dir" in resolved_artifacts and not resolved_artifacts["evidence_dir"].is_dir():
        validator.error("evidence-dir", "artifacts.evidence_dir must be a directory", resolved_artifacts["evidence_dir"])
    if "claim_registry" in resolved_artifacts:
        claim_path = resolved_artifacts["claim_registry"]
        claims = validator.guarded("claims-read", lambda: load_yaml(claim_path), claim_path)
        if claims is not None:
            if claims.get("schema_version") != 1 or not isinstance(claims.get("items"), list):
                validator.error("claims-schema", "claim registry schema_version must be 1 with an items list", claim_path)
            else:
                seen_claims: set[str] = set()
                for index, claim in enumerate(claims["items"]):
                    if not isinstance(claim, dict) or not isinstance(claim.get("id"), str):
                        validator.error("claim-shape", f"claims.items[{index}] is malformed", claim_path)
                        continue
                    claim_id = claim["id"]
                    if claim_id in seen_claims:
                        validator.error("claim-duplicate", f"duplicate claim id: {claim_id}", claim_path)
                    seen_claims.add(claim_id)
                    if claim.get("status") == "active":
                        active_claims.add(claim_id)
                    if not isinstance(claim.get("statement"), str) or not claim["statement"].strip():
                        validator.error("claim-statement", f"claim {claim_id} has no observable statement", claim_path)
                    if not isinstance(claim.get("owner"), str) or not claim["owner"].strip():
                        validator.error("claim-owner", f"claim {claim_id} has no owner", claim_path)
                context["claims"] = claims
                context["known_claims"] = sorted(seen_claims)

    auth_path = validator.guarded(
        "authorization-path",
        lambda: resolve_relative(validator.root, state.get("authorization_ref"), "authorization_ref"),
        state_path,
    )
    state_auth = _validate_authorization(validator, auth_path) if auth_path is not None else None
    if state_auth is not None:
        context["authorization"] = state_auth
        context["authorization_path"] = str(auth_path)
        if mode not in state_auth.get("allowed_modes", []):
            validator.error("state-mode-unauthorized", f"operating mode {mode!r} is not authorized", state_path)

    policy = state.get("execution_policy")
    if not isinstance(policy, dict):
        validator.error("execution-policy", "execution_policy must be a mapping", state_path)
        policy = {}
    max_active = policy.get("max_active_items")
    if not isinstance(max_active, int) or isinstance(max_active, bool) or max_active < 1:
        validator.error("max-active", "max_active_items must be an integer of at least 1", state_path)
        max_active = 1
    concurrency = policy.get("concurrency_enabled") is True
    if max_active > 1 and not concurrency:
        validator.error("concurrency-disabled", "max_active_items above 1 requires concurrency_enabled", state_path)
    if concurrency and max_active > 1 and not isinstance(policy.get("merge_owner"), str):
        validator.error("merge-owner", "parallel work requires a merge_owner", state_path)
    default_attempts = policy.get("default_max_attempts", 3)
    if not isinstance(default_attempts, int) or isinstance(default_attempts, bool) or default_attempts < 1:
        validator.error("attempt-policy", "default_max_attempts must be a positive integer", state_path)
        default_attempts = 3
    if not policy.get("require_claim_coverage", False):
        validator.warn("claim-coverage-disabled", "claim coverage enforcement is disabled", state_path)
    if not policy.get("require_attested_cards", False):
        validator.warn("attestation-disabled", "card attestation enforcement is disabled", state_path)

    card_paths: dict[str, Path] = {}
    item_auth: dict[str, dict[str, Any] | None] = {}
    for item_id, item in items.items():
        status = item.get("status")
        if status not in ITEM_STATUSES:
            validator.error("item-status", f"item {item_id} has unknown status {status!r}", registry_path)
        dependencies = _as_string_list(item.get("depends_on"), f"{item_id}.depends_on", validator, registry_path)
        for dependency in dependencies:
            if dependency not in items:
                validator.error("dependency-missing", f"item {item_id} depends on unknown item {dependency}", registry_path)
            if dependency == item_id:
                validator.error("dependency-self", f"item {item_id} depends on itself", registry_path)
        item_claims = _as_string_list(item.get("claims", []), f"{item_id}.claims", validator, registry_path)
        known_claims = set(context.get("known_claims", []))
        unknown = sorted(set(item_claims) - known_claims)
        if unknown:
            validator.error("item-claims", f"item {item_id} references unknown claims: {unknown}", registry_path)
        if policy.get("require_claim_coverage") and item.get("type") in {
            "implementation",
            "validation",
            "external_operation",
            "acceptance_gate",
        } and not item_claims:
            validator.error("item-claim-coverage", f"item {item_id} must link at least one claim", registry_path)

        attempts = item.get("attempts", 0)
        maximum = item.get("max_attempts", default_attempts)
        if not isinstance(attempts, int) or isinstance(attempts, bool) or attempts < 0:
            validator.error("item-attempts", f"item {item_id} attempts must be a non-negative integer", registry_path)
            attempts = 0
        if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
            validator.error("item-budget", f"item {item_id} max_attempts must be positive", registry_path)
            maximum = default_attempts
        if status in {"ready", "in_progress"} and attempts >= maximum:
            validator.error("item-budget-exhausted", f"item {item_id} exhausted its attempt budget", registry_path)

        card_path = validator.guarded(
            "card-path",
            lambda item=item, item_id=item_id: resolve_relative(
                validator.root,
                item.get("card"),
                f"{item_id}.card",
            ),
            registry_path,
        )
        if card_path is not None:
            card_paths[item_id] = card_path
            frontmatter_and_text = validator.guarded(
                "card-frontmatter",
                lambda card_path=card_path: parse_card(card_path),
                card_path,
            )
            if frontmatter_and_text is not None:
                frontmatter, _ = frontmatter_and_text
                comparisons = {
                    "id": item_id,
                    "stage": item.get("stage"),
                    "mode": item.get("mode"),
                    "depends_on": dependencies,
                    "claims": item_claims,
                    "owner": item.get("owner"),
                    "write_scope": item.get("write_scope"),
                    "max_attempts": maximum,
                    "authority_ref": item.get("authority_ref"),
                }
                for field, expected in comparisons.items():
                    if frontmatter.get(field) != expected:
                        validator.error(
                            "card-registry-mismatch",
                            f"card {item_id} field {field} disagrees with the registry",
                            card_path,
                        )

        authority_ref = item.get("authority_ref")
        card_auth_path = validator.guarded(
            "item-authorization-path",
            lambda authority_ref=authority_ref, item_id=item_id: resolve_relative(
                validator.root,
                authority_ref,
                f"{item_id}.authority_ref",
            ),
            registry_path,
        )
        auth = _validate_authorization(validator, card_auth_path) if card_auth_path is not None else None
        item_auth[item_id] = auth
        if status in {"ready", "in_progress"} and auth is not None:
            item_mode = item.get("mode")
            if item_mode not in auth.get("allowed_modes", []):
                validator.error("item-mode-unauthorized", f"item {item_id} mode {item_mode!r} is not authorized", registry_path)
            write_scope = _as_string_list(item.get("write_scope"), f"{item_id}.write_scope", validator, registry_path)
            allowed_scope = auth.get("allowed_scope", [])
            for requested in write_scope:
                allowed = False
                for scope in allowed_scope:
                    try:
                        if scope_contains(scope, requested):
                            allowed = True
                            break
                    except ControlError as exc:
                        validator.error("item-write-scope", str(exc), registry_path)
                if not allowed:
                    validator.error("item-scope-unauthorized", f"item {item_id} scope is not authorized: {requested}", registry_path)

        if status == "blocked" and not item.get("blocker"):
            validator.error("blocker-missing", f"blocked item {item_id} must link a blocker", registry_path)
        if status in {"canceled", "superseded"} and not item.get("resolution"):
            validator.error("resolution-missing", f"terminal item {item_id} must link a resolution", registry_path)
        for field in ("blocker", "resolution"):
            if item.get(field):
                validator.guarded(
                    f"{field}-path",
                    lambda item=item, field=field, item_id=item_id: resolve_relative(
                        validator.root,
                        item[field],
                        f"{item_id}.{field}",
                    ),
                    registry_path,
                )

        evidence_refs = _as_string_list(item.get("evidence"), f"{item_id}.evidence", validator, registry_path)
        if status == "completed" and policy.get("require_mandatory_evidence", True) and not evidence_refs:
            validator.error("completion-evidence", f"completed item {item_id} has no evidence", registry_path)
        for evidence_ref in evidence_refs:
            evidence_path = validator.guarded(
                "evidence-path",
                lambda evidence_ref=evidence_ref, item_id=item_id: resolve_relative(
                    validator.root,
                    evidence_ref,
                    f"{item_id}.evidence",
                ),
                registry_path,
            )
            if evidence_path is not None:
                _validate_evidence(
                    validator,
                    evidence_path,
                    set(context.get("known_claims", [])),
                    require_passing=status == "completed",
                )

    cycle = _has_dependency_cycle(items)
    if cycle:
        validator.error("dependency-cycle", f"dependency cycle: {' -> '.join(cycle)}", registry_path)

    if policy.get("require_claim_coverage"):
        linked_claims = {
            claim
            for item in items.values()
            if item.get("status") not in {"canceled", "superseded"}
            for claim in item.get("claims", [])
        }
        for claim in sorted(active_claims - linked_claims):
            validator.error("claim-unmapped", f"active claim has no work item: {claim}", claim_path)

    active_items = _as_string_list(state.get("active_items"), "active_items", validator, state_path)
    next_items = _as_string_list(state.get("next_items"), "next_items", validator, state_path)
    registry_active = [item_id for item_id in item_order if items[item_id].get("status") == "in_progress"]
    if active_items != registry_active:
        validator.error(
            "active-pointer-mismatch",
            f"active_items {active_items} does not match in_progress items {registry_active}",
            state_path,
        )
    if len(active_items) > max_active:
        validator.error("active-capacity", "active_items exceeds max_active_items", state_path)
    for item_id in active_items + next_items:
        if item_id not in items:
            validator.error("pointer-unknown", f"state points to unknown item {item_id}", state_path)

    available_slots = max(0, max_active - len(registry_active))
    eligible: list[str] = []
    for item_id in item_order:
        item = items[item_id]
        if item.get("status") != "ready" or item.get("stage") != current_stage:
            continue
        dependencies = item.get("depends_on", [])
        if any(items.get(dep, {}).get("status") != "completed" for dep in dependencies):
            continue
        maximum = item.get("max_attempts", default_attempts)
        if item.get("attempts", 0) >= maximum:
            continue
        auth = item_auth.get(item_id)
        if auth is None or item.get("mode") not in auth.get("allowed_modes", []):
            continue
        eligible.append(item_id)
    expected_next = eligible[:available_slots]
    if next_items != expected_next:
        validator.error(
            "next-pointer-mismatch",
            f"next_items {next_items} does not match eligible items {expected_next}",
            state_path,
        )
    context["eligible_items"] = eligible
    context["next_items_expected"] = expected_next

    if concurrency and len(active_items) > 1:
        ownership: list[tuple[str, str]] = []
        for item_id in active_items:
            item = items.get(item_id, {})
            if not isinstance(item.get("owner"), str) or not item["owner"].strip():
                validator.error("concurrency-owner", f"active item {item_id} has no owner", registry_path)
            scopes = _as_string_list(item.get("write_scope"), f"{item_id}.write_scope", validator, registry_path)
            if not scopes:
                validator.error("concurrency-scope", f"active item {item_id} has no write_scope", registry_path)
            for scope in scopes:
                for other_id, other_scope in ownership:
                    try:
                        if scopes_overlap(scope, other_scope):
                            validator.error(
                                "concurrency-overlap",
                                f"active items {other_id} and {item_id} have overlapping scopes: {other_scope} / {scope}",
                                registry_path,
                            )
                    except ControlError as exc:
                        validator.error("concurrency-scope", str(exc), registry_path)
                ownership.append((item_id, scope))

    if policy.get("require_attested_cards"):
        for item_id in active_items:
            item = items.get(item_id, {})
            if item.get("mode") == "execute" and item_id in card_paths:
                _validate_attestation(validator, card_paths[item_id])

    gates = state.get("gates")
    if not isinstance(gates, dict):
        validator.error("gates-shape", "gates must be a mapping", state_path)
    else:
        for gate_id, gate in gates.items():
            if not isinstance(gate, dict):
                validator.error("gate-shape", f"gate {gate_id} must be a mapping", state_path)
                continue
            gate_type = gate.get("type")
            status = gate.get("status")
            allowed = (
                {"pending", "approved", "rejected", "not_applicable"}
                if gate_type == "human"
                else {"not_run", "pass", "fail", "not_applicable"}
                if gate_type == "automated"
                else set()
            )
            if status not in allowed:
                validator.error("gate-status", f"gate {gate_id} has invalid type/status", state_path)
            if gate_type == "human" and status in {"approved", "rejected"} and not gate.get("decision_ref"):
                validator.error("gate-decision", f"human gate {gate_id} requires decision_ref", state_path)
            if gate_type == "automated" and status in {"pass", "fail"} and not gate.get("report"):
                validator.error("gate-report", f"automated gate {gate_id} requires a report", state_path)
            if status == "not_applicable" and not gate.get("not_applicable_reason"):
                validator.error("gate-na-reason", f"gate {gate_id} requires not_applicable_reason", state_path)
            for field in ("report", "decision_ref"):
                if gate.get(field):
                    validator.guarded(
                        "gate-path",
                        lambda gate=gate, field=field, gate_id=gate_id: resolve_relative(
                            validator.root,
                            gate[field],
                            f"gates.{gate_id}.{field}",
                        ),
                        state_path,
                    )

    work_status = state.get("work_status", state.get("migration_status"))
    if work_status in TERMINAL_WORK_STATUSES and (active_items or next_items):
        validator.error("terminal-pointers", "terminal work cannot retain active_items or next_items", state_path)

    if "journal" in resolved_artifacts:
        _validate_journal(validator, resolved_artifacts["journal"], set(items))

    return validator.diagnostics, context


def _result_payload(root: Path) -> dict[str, Any]:
    diagnostics, context = validate_root(root)
    errors = [diagnostic for diagnostic in diagnostics if diagnostic.level == "error"]
    warnings = [diagnostic for diagnostic in diagnostics if diagnostic.level == "warning"]
    return {
        "valid": not errors,
        "root": str(root.resolve()),
        "errors": [asdict(diagnostic) for diagnostic in errors],
        "warnings": [asdict(diagnostic) for diagnostic in warnings],
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "eligible_items": context.get("eligible_items", []),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_root", type=Path, help="Directory containing the bounded-work control plane")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()
    payload = _result_payload(args.work_root)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        status = "PASS" if payload["valid"] else "FAIL"
        print(
            f"{status}: {payload['root']} "
            f"({payload['summary']['errors']} errors, {payload['summary']['warnings']} warnings)"
        )
        for diagnostic in payload["errors"] + payload["warnings"]:
            location = f" [{diagnostic['path']}]" if diagnostic["path"] else ""
            print(f"- {diagnostic['level'].upper()} {diagnostic['code']}{location}: {diagnostic['message']}")
        if payload["summary"]["eligible_items"]:
            print(f"Eligible: {', '.join(payload['summary']['eligible_items'])}")
    return 0 if payload["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
