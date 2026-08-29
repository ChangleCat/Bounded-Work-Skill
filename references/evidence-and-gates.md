# Evidence and Gates

Read this reference when defining verification, evaluating completion, handling high-risk operations, or auditing claims.

## Match evidence to the claim

Evidence should observe the actual outcome as directly as practical:

| Claim | Strong evidence examples |
|---|---|
| Code behavior | Focused regression test plus relevant integration test |
| Build or packaging | Clean build of the identified artifact and checksum |
| Document quality | Rendered visual inspection plus content checks |
| Data correctness | Reproducible query, reconciliation, and invariant checks |
| Security remediation | Original exploit/reproduction fails; regression and abuse cases pass |
| Reliability | Fault injection and durable-state verification |
| Performance | Repeatable benchmark with environment and baseline |
| Operational readiness | Production-shaped rehearsal, monitoring, recovery, and owner review |
| Policy or stakeholder acceptance | Named approver and recorded decision against a rubric |

Static inspection is weaker than execution for runtime claims. A unit test is weaker than an integration test for behavior owned by a real database, broker, filesystem, identity provider, or network.

## Evidence record

For auditable work, record:

- requirement or claim;
- exact producer: command, test, query, render, reviewer, or external receipt;
- artifact identity: revision, digest, dataset, or document version;
- environment and relevant configuration;
- pass, fail, or not run;
- time and owner;
- known limitations;
- approval or waiver reference when applicable.
- evidence validity, any expiry, and the revisions or digests of inputs on which the result depends.

Evidence from one artifact or environment cannot silently prove another. Clearly label simulations, local runs, staging runs, and production facts.

Keep result and validity separate. A historical result may remain `pass` while its validity becomes `stale` after an input change or deadline. `superseded` means a newer evidence record has replaced it; it does not erase the old observation.

Before reusing evidence, verify that its claim IDs, artifact identity, environment, bound inputs, and validity window still match. Follow [traceability-and-resume.md](traceability-and-resume.md) when upstream changes may invalidate downstream proof.

## Risk-scaled gates

Possible gates include:

- **Automated gate**: deterministic checks all pass.
- **Reviewer gate**: a named reviewer evaluates qualitative or architectural criteria.
- **Owner gate**: the accountable owner accepts operational or business consequences.
- **User authorization gate**: the requested action exceeds current permission or changes external state materially.

A gate must specify entry requirements, evidence, decision maker, pass/fail outcomes, and what becomes eligible afterward. Automated evidence may support a human gate but cannot approve it.

Keep automated and human state distinct:

- automated gates use `not_run | pass | fail`;
- human gates use `pending | ready_for_approval | approved | rejected | not_applicable`;
- automated recommendations use `ready_for_approval | not_ready | blocked`, never `approve`;
- `approved` and `rejected` require a decision owner and decision reference;
- `not_applicable` requires a recorded reason and must not hide missing mandatory evidence.

## Recovery and contingency

For reversible work, define the safe rollback unit and preserved state. For irreversible work, define:

- point of no return;
- precondition and approval immediately before it;
- backup, export, or compensating action;
- abort conditions before the point of no return;
- monitoring and reconciliation after it;
- owner of the consequences.

Do not call a plan reversible when recovery depends on untested assumptions.

## Waivers

A missing or failed mandatory check remains visible. A waiver should state:

- the exact requirement being waived;
- why evidence cannot be obtained;
- risk introduced;
- compensating controls;
- expiry or follow-up item;
- authorized approver.

Never rewrite a failure or `not_run` result as pass because a waiver exists.

A waiver also does not extend an expired result, repair a mismatched digest, or make stale evidence current. The approver accepts a documented gap; automation must keep the gap visible.

## Audit procedure

An audit should distinguish:

1. **Fact**: directly supported by current evidence.
2. **Inference**: reasonable conclusion with stated assumptions.
3. **Gap**: required evidence or definition is missing.
4. **Conflict**: sources of truth disagree.
5. **Unsupported claim**: status exceeds its evidence.

Check the highest-risk claims first. Avoid repairing during a read-only audit; report the smallest corrective work items and the authority they require.

## Blocker report

Use this compact structure:

```text
Confirmed facts: <evidence-backed state>
Blocker: <specific unmet condition>
Affected acceptance: <criteria that cannot pass>
Preserved results: <safe partial artifacts/evidence>
Required next decision: <who must decide or authorize what>
```
