# Reference Tooling

Read when creating, validating, resuming, or attesting a file-backed control plane with the bundled scripts.

## Requirements and boundary

Python 3.11+ and PyYAML 6.x; install `scripts/requirements.txt` in an isolated environment. Without the scripts the workflow still works, but report unrun checks as `not_run`. All helpers are local and fail closed: they reject unsafe paths and never grant approval, approve a human gate, execute a card, or auto-repair state.

## Initialize

```text
python scripts/init_work.py <work-root> \
  --title "<outcome-oriented title>" \
  --owner "<responsible owner>" \
  --authority-ref "<request or decision reference>" \
  --claim "<observable success claim>"
```

`--migration` uses the migration state template. Creates a bootstrap-only authorization record, state, registry, claim registry, charter, first card, evidence directory, and empty journal. Refuses to overwrite an existing control plane.

## Promote Bootstrap to Execute

The initializer can't do this. After an authorized owner accepts the charter and claims:

1. add bounded execution cards linked to claim IDs;
2. record a durable authorization explicitly allowing `execute` for the needed scope and environment;
3. set state mode to `execute`, enable claim coverage, and enable attestation if unattended or cross-session execution needs it;
4. attest accepted stable cards, then run validation and the resume report;
5. start only the item exposed as eligible.

Editing a YAML field is not approval; keep the authority source and human decision provenance.

## Validate

```text
python scripts/validate_work.py <work-root> [--json]
```

Checks schemas, path containment, vocabularies, pointers, dependencies, cycles, eligibility, authority, claim coverage, completed evidence, freshness and input digests, gate semantics, budgets, concurrency ownership, closure, journal syntax, and attestations. Exits `0` with no errors, `2` if inconsistent; warnings stay visible but don't fail an otherwise bootstrap-safe plane.

## Resume

```text
python scripts/resume_work.py <work-root> [--json]
```

Implements the cold-resume contract (outcome, state, eligibility reason, proved results, next action, authority) with validation findings; exits `2` if safe continuation can't be established.

## Attest

```text
python scripts/attest_control.py <work-root> attest <relative-path>... \
  --actor "<reviewer>" --authority-ref "<review reference>"
python scripts/attest_control.py <work-root> verify [<relative-path>...]
python scripts/attest_control.py <work-root> show
python scripts/attest_control.py <work-root> clear <relative-path>...
```

Manifest: `.bounded-work-attestations.json` in the work root. Attest stable cards, charters, contracts, or decisions, not mutable state or journals. `verify` compares SHA-256 and exits nonzero for missing, changed, unsafe, or unreadable records. A valid digest is integrity evidence only.
