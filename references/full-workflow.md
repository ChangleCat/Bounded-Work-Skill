# Full Workflow

Read when work escalates beyond the solo profile: several owners or approvers, unseen or parallel automation, material external risk, or required audit or handoff. The shared rules in `SKILL.md` still apply.

## Mode results

Close each mode proportionately; these are contracts, not headings.

- **Frame**: outcome, done-when, scope, risks, assumptions, work units, next step.
- **Bootstrap**: artifacts, state location, validation status, first eligible item or blocker.
- **Execute**: outcome, changes, evidence and limits, state transition, remaining risk, newly eligible work.
- **Audit**: facts, inferences, gaps, conflicts, unsupported claims, ranked corrections, authority needed.

## Frame

Proportionately define: **outcome** (a result, not activity), **definition of done** (observable evidence), **scope** (in and out), **constraints**, **risks and recovery** (failure modes, reversible boundary, point of no return), and **authority** (what needs approval). Record material unknowns as decisions or blockers; don't invent requirements. See [task-design.md](task-design.md) for decomposition.

## Cards

Each card yields one independently verifiable result. Include only useful fields: ID, outcome, dependencies; required context; allowed and forbidden scope; steps or decision criteria; exact verification; binary acceptance; recovery; state transition. Persistent work adds claim links and authority reference; add write ownership, retry budget, or stall limit only when execution needs them.

Separate decision, implementation, validation, external-operation, and gate cards when authority or evidence differs. A gate evaluates evidence; it never hides repair.

## Context

Load in order: user request and workspace instructions; work state and pointers; registry entry and completed dependencies; stage packet; one card; only the files that card needs. Expand only when a reference is undefined, reality contradicts the plan, a failure crosses a boundary, or authorities conflict.

## State and authority

Default item states:

```text
planned -> ready -> in_progress -> completed
                         \-> blocked -> ready
planned | ready | blocked -> canceled | superseded
```

`canceled` and `superseded` are terminal, not success; record reason and downstream impact. Full vocabularies and invariants are in [control-plane.md](control-plane.md).

Before acting, confirm the card is eligible, dependencies are complete, no other work owns the scope, current changes are preserved, and authority covers the action.

Don't rely on remembered chat permission: resolve a durable authorization record (source, grantor, modes, scope, environments, expiry, revocation). Validation never creates authorization. Parallel work needs non-overlapping write ownership and one coordinator for shared state.

## Execute

- Run one eligible card per Execute pass unless concurrency is explicitly enabled.
- Honor the card's scope and the user's chosen approach.
- Write a failing check first when it materially raises confidence.
- Record discovered cross-card work instead of absorbing it.
- Stop when the attempt, time, cost, or stall budget is spent; widening it needs a new decision.
- If the task outgrows one result, stop at a safe boundary and split it.

## Prove completion

Run every mandatory check in order. Complete a card only when its artifact exists and all mandatory criteria are supported. Bind reusable evidence to claims, artifact identity, environment, input revisions or digests, time, and validity window. When an upstream input changes materially, mark dependent evidence stale and reopen downstream gates. See [evidence-and-gates.md](evidence-and-gates.md) and [traceability-and-resume.md](traceability-and-resume.md).

## Approval and blockers

Automation may gather evidence and recommend; it never grants approval reserved for a person. Beyond the shared hard stops, also pause before accepting material risk or waiving evidence.

Stop and report a blocker when state, dependencies, scope, or sources of truth conflict; work falls outside the card or request; a key safety, ownership, acceptance, or recovery rule is undefined; a failed check needs another card or decision; completion needs new authority or a waiver; or overlapping changes can't be preserved. Report confirmed facts, the blocking condition, affected criteria, preserved results, and the exact decision needed.

## Bootstrap assets

Adapt only needed templates from `assets/work-control/`; migration uses `assets/workflows/migration/migration-state.template.yaml` in place of the generic state template. Follow repository conventions; filenames are examples. If Python and PyYAML are available, use the fail-closed helpers in [tooling.md](tooling.md); otherwise keep the invariants manually and report validation as `not_run`.

Before resuming, apply the cold-resume contract in [traceability-and-resume.md](traceability-and-resume.md). Close or de-escalate per [control-plane.md](control-plane.md).

## Executed-card report

```text
Work item: <id>
Result: completed | blocked
Outcome: <observable result>
Changes: <artifacts or resources>
Verification: <check -> pass | fail | not_run>
Evidence record: <artifact, receipt, or inline record and known limits>
Environment: <relevant platform or context>
Scope/decision impact: none | <approved change>
Remaining issues: none | <issues>
Next eligible items: <ids | none>
```
