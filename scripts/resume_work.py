#!/usr/bin/env python3
"""Produce a cold-resume summary from first-layer bounded-work artifacts only."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from validate_work import validate_root


def build_summary(root: Path) -> tuple[dict[str, Any], int]:
    diagnostics, context = validate_root(root)
    errors = [diagnostic for diagnostic in diagnostics if diagnostic.level == "error"]
    warnings = [diagnostic for diagnostic in diagnostics if diagnostic.level == "warning"]
    state = context.get("state", {})
    items = context.get("items", {})
    claims = context.get("claims", {}).get("items", [])
    active = state.get("active_items", []) if isinstance(state, dict) else []
    eligible = context.get("next_items_expected", [])
    selected = active[0] if active else eligible[0] if eligible else None
    selected_item = items.get(selected, {}) if selected else {}

    claim_summary = [
        {
            "id": claim.get("id"),
            "statement": claim.get("statement"),
            "status": claim.get("status"),
        }
        for claim in claims
        if isinstance(claim, dict)
    ]
    completed = [
        {
            "item": item_id,
            "outcome": item.get("title"),
            "evidence": item.get("evidence", []),
        }
        for item_id, item in items.items()
        if item.get("status") == "completed"
    ]
    accepted_gates = [
        {
            "gate": gate_id,
            "status": gate.get("status"),
            "report": gate.get("report"),
            "decision_ref": gate.get("decision_ref"),
        }
        for gate_id, gate in state.get("gates", {}).items()
        if isinstance(gate, dict) and gate.get("status") in {"pass", "approved"}
    ]

    if selected:
        dependencies = selected_item.get("depends_on", [])
        eligibility = (
            f"{selected} is already in progress"
            if selected in active
            else f"{selected} is ready in the current stage and all dependencies are completed"
        )
        next_action = {
            "item": selected,
            "action": selected_item.get("title"),
            "card": selected_item.get("card"),
            "dependencies": dependencies,
            "write_scope": selected_item.get("write_scope", []),
            "attempt_boundary": {
                "attempts": selected_item.get("attempts", 0),
                "max_attempts": selected_item.get("max_attempts"),
            },
        }
    else:
        eligibility = "No item is safely eligible; inspect validation errors, blockers, stage state, and authority."
        next_action = {
            "item": None,
            "action": "Resolve the reported blocker or close terminal work; do not infer a card from chat history.",
        }

    authorization = context.get("authorization", {})
    payload = {
        "valid": not errors,
        "work_root": str(root.resolve()),
        "goal_and_claims": {
            "outcome": state.get("work_title"),
            "claims": claim_summary,
        },
        "current_state": {
            "mode": state.get("operating_mode"),
            "stage": state.get("current_stage"),
            "stage_status": state.get("stage_status"),
            "active_items": active,
            "eligible_items": eligible,
        },
        "eligibility_reason": eligibility,
        "proved_results": {
            "completed_items": completed,
            "accepted_gates": accepted_gates,
            "limits": "Only linked evidence validated by this control plane is summarized.",
        },
        "next_action": next_action,
        "authority": {
            "source": authorization.get("source"),
            "granted_by": authorization.get("granted_by"),
            "allowed_modes": authorization.get("allowed_modes", []),
            "allowed_scope": authorization.get("allowed_scope", []),
            "environments": authorization.get("environments", []),
            "expires_at": authorization.get("expires_at"),
            "revoked_at": authorization.get("revoked_at"),
        },
        "validation": {
            "errors": [asdict(diagnostic) for diagnostic in errors],
            "warnings": [asdict(diagnostic) for diagnostic in warnings],
        },
    }
    return payload, 0 if not errors else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_root", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()
    payload, status = build_summary(args.work_root)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Outcome: {payload['goal_and_claims']['outcome']}")
        print(f"Current state: {payload['current_state']}")
        print(f"Eligibility: {payload['eligibility_reason']}")
        print(f"Proved results: {payload['proved_results']}")
        print(f"Next action: {payload['next_action']}")
        print(f"Authority: {payload['authority']}")
        if payload["validation"]["errors"]:
            print(f"Validation errors: {len(payload['validation']['errors'])}")
        if payload["validation"]["warnings"]:
            print(f"Validation warnings: {len(payload['validation']['warnings'])}")
    return status


if __name__ == "__main__":
    sys.exit(main())
