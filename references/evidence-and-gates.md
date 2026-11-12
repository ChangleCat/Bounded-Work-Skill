# Evidence and Gates

Read when defining verification, judging completion, handling high-risk operations, or auditing claims.

## Match evidence to the claim

Observe the actual outcome as directly as practical.

| Claim | Strong evidence |
|---|---|
| Code behavior | Focused regression test plus relevant integration test |
| Build or packaging | Clean build of the identified artifact plus checksum |
| Document quality | Rendered inspection plus content checks |
| Data correctness | Reproducible query, reconciliation, invariant checks |
| Security fix | Original reproduction fails; regression and abuse cases pass |
| Reliability | Fault injection plus durable-state checks |
| Performance | Repeatable benchmark with environment and baseline |
| Operational readiness | Production-shaped rehearsal, monitoring, recovery, owner review |
| Policy or stakeholder acceptance | Named approver and recorded decision against a rubric |

Static inspection is weaker than execution for runtime claims; unit tests are weaker than integration tests for behavior owned by a real database, broker, filesystem, identity provider, or network.

## Evidence record

For auditable work, record: claim; exact producer (command, test, query, render, reviewer, receipt); artifact identity (revision, digest, dataset, version); environment and configuration; `pass | fail | not_run`; time and owner; limits; approval or waiver reference; validity, expiry, and input revisions or digests.

Evidence from one artifact or environment never silently proves another; label simulations, local, staging, and production facts. Result and validity are separate: a `pass` can become `stale` after an input change or deadline, and `superseded` means a newer record replaced it without erasing the old observation. Before reuse, check claims, identity, environment, bound inputs, and validity window still match; see [traceability-and-resume.md](traceability-and-resume.md) for change impact.

## Gates

- **Automated**: deterministic checks pass.
- **Reviewer**: a named reviewer judges qualitative or architectural criteria.
- **Owner**: the accountable owner accepts operational or business consequences.
- **User authorization**: the action exceeds current permission or materially changes external state.

Each gate states entry requirements, evidence, decision maker, outcomes, and what becomes eligible next. Automated evidence supports a human gate but never approves it. Gate state vocabularies and who may set them are in [control-plane.md](control-plane.md#state-vocabularies); `not_applicable` must not hide missing mandatory evidence.

## Recovery

For reversible work, define the rollback unit and preserved state. For irreversible work, define the point of no return; the precondition and approval just before it; backup, export, or compensating action; abort conditions before it; monitoring and reconciliation after it; and the owner of consequences. A plan resting on untested recovery assumptions is not reversible.

## Waivers

A missing or failed mandatory check stays visible. A waiver states the exact requirement, why evidence can't be obtained, risk introduced, compensating controls, expiry or follow-up, and authorized approver. It never turns `fail` or `not_run` into pass, extends an expired result, fixes a mismatched digest, or makes stale evidence current; it only accepts a documented gap.

## Audit

Classify findings as **fact** (supported by current evidence), **inference** (stated assumptions), **gap** (missing evidence or definition), **conflict** (sources disagree), or **unsupported claim** (status exceeds evidence). Check the highest-risk claims first. Don't repair during a read-only audit; report the smallest corrective items and the authority they need.

## Blocker report

```text
Confirmed facts: <evidence-backed state>
Blocker: <specific unmet condition>
Affected acceptance: <criteria that cannot pass>
Preserved results: <safe partial artifacts/evidence>
Required next decision: <who must decide or authorize what>
```
