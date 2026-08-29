# Reference Tooling

Read this reference when creating, validating, resuming, or attesting a file-backed Bounded Work control plane with the bundled scripts.

## Requirements and boundary

The helpers require Python 3.11+ and PyYAML 6.x. Install the dependency from `scripts/requirements.txt` in an isolated environment. The core workflow remains usable without the scripts, but any unrun deterministic check must be reported as `not_run`.

All helpers are local and fail closed. They reject unsafe control-file paths and never grant approval, change a human gate to approved, execute a work card, or repair inconsistent state automatically.

## Initialize

```text
python scripts/init_work.py <work-root> \
  --title "<outcome-oriented title>" \
  --owner "<responsible owner>" \
  --authority-ref "<request or decision reference>" \
  --claim "<observable success claim>"
```

Add `--migration` to use the migration state template. Initialization creates a bootstrap-only authorization record, state, registry, claim registry, charter, first card, evidence directory, and empty append-only journal. It refuses to overwrite an existing control plane.

## Promote from Bootstrap to Execute

The initializer intentionally cannot perform this transition. After an authorized owner accepts the charter and claims:

1. add bounded execution cards and link each outcome-bearing card to claim IDs;
2. record a new or updated durable authorization decision that explicitly allows `execute` for the required scope and environment;
3. set the state mode to `execute`, enable claim coverage, and enable card attestation when unattended or cross-session execution requires it;
4. attest accepted stable cards, then run validation and the cold-resume report;
5. start only the exact item exposed as eligible.

Changing a YAML field is not itself approval. Preserve the authority source and human decision provenance that justified the change.

## Validate

```text
python scripts/validate_work.py <work-root>
python scripts/validate_work.py <work-root> --json
```

Validation checks schemas, path containment, state vocabularies, pointers, dependencies, cycles, eligibility, authority, claim coverage policy, completed evidence, evidence freshness and bound-input digests, gate semantics, budgets, concurrency ownership, terminal closure, journal syntax, and required attestations.

Exit status is `0` when no errors exist and `2` when the control plane is inconsistent. Warnings remain visible but do not make an otherwise bootstrap-safe control plane invalid.

## Resume

```text
python scripts/resume_work.py <work-root>
python scripts/resume_work.py <work-root> --json
```

The output implements the cold-resume contract: outcome, current state, eligibility reason, proved results, next action, and durable authority. It includes validation findings and exits `2` if safe continuation cannot be established.

## Attest or verify stable controls

```text
python scripts/attest_control.py <work-root> attest <relative-path>... \
  --actor "<reviewer>" --authority-ref "<review reference>"
python scripts/attest_control.py <work-root> verify [<relative-path>...]
python scripts/attest_control.py <work-root> show
python scripts/attest_control.py <work-root> clear <relative-path>...
```

The manifest is `.bounded-work-attestations.json` under the work root. Attest cards, charters, contracts, or decisions that should remain stable during execution. Do not attest mutable state or journals merely to avoid expected changes.

Verification compares SHA-256 digests and exits nonzero for missing, changed, unsafe, or unreadable records. A valid digest is integrity evidence only; human approval and execution authority remain separate records.
