# Atomic Work Design

Read when framing a complex outcome, building a task graph, or splitting an oversized card.

## Start from outcomes

Decompose by observable result, not folder or job title. For each item, know: what becomes true, who consumes it, what proves it, what must already be true, and whether it can be accepted or recovered alone. Avoid activity-only items ("work on tests", "improve security"); name the state change.

## Card types

| Type | Produces | Typical evidence |
|---|---|---|
| Discovery | Verified facts, open questions | Inventory, measurements, reproduction |
| Decision | Approved choice and consequences | Decision record and approver |
| Contract | Frozen behavior or interface | Schema, fixture, acceptance test |
| Implementation | Bounded behavior or artifact | Focused tests, inspection |
| Integration | Connected components | End-to-end or environment evidence |
| Remediation | Closed known finding | Before/after reproduction, regression test |
| Operation | Authorized external or environment change | Preflight, execution log, postconditions |
| Gate | Acceptance or rejection of evidence | Evidence matrix, human decision when required |

Don't combine an unresolved decision with the implementation that depends on it, or an external operation with preparatory code to dodge an approval pause.

## Atomicity test

Split a card if any is true:

1. Part of the result is independently useful and acceptable.
2. It has unrelated consumers or owners.
3. Parts need different authorization or environments.
4. One check can fail while another part legitimately completes.
5. Recovery would revert only part of it.
6. It needs unrelated context or overlapping write ownership.
7. It likely exceeds one focused session.

Group small tasks only when they share outcome, scope, verification, and recovery boundary.

## Dependencies

B depends on A only when B would be unsafe, invalid, or unverifiable without A's completed result. Prefer a DAG to a forced serial chain. Expose several ready cards only when concurrent ownership is safe and permitted; one coordinator owns shared state.

Common mistakes: depending on a whole stage when one artifact suffices; omitting a decision or contract dependency; tracking artifact readiness in two places; completing a prerequisite without its evidence; unlocking implementation before environment or authority exists.

## Claims and authority

In persistent work, link cards to stable claim IDs instead of copying requirement text; give coordination-only cards an explicit type. An executable card resolves a durable authority reference and records its mode and any narrower environment or action limit; it cannot widen the grant. For parallel work, use structured `owner` and `write_scope` fields a validator can check, plus a merge owner; prose is not enough.

## Retries and stalls

Set a proportional retry, time, cost, or stall limit when repeats could hide a design problem, consume real resources, or repeat external effects. Record each materially different attempt. Exhausting it makes the card `blocked`; it never authorizes broader attempts, another environment, weaker checks, or a counter reset. Only a user or decision owner may approve a new budget after reviewing evidence.

## Binary acceptance

Criteria must be checkable without interpreting intent:

- "all three supported inputs produce the recorded outputs", not "handles common cases";
- "no clipping at the target size", not "layout looks good";
- "SEC-12 no longer reproduces and its regression test passes", not "security improved";
- "artifact digest X passes install and rollback checks", not "release ready".

Qualitative outcomes may use review, with named reviewer, rubric, and decision status.

## Replanning

Replan when evidence invalidates dependencies, scope, risk, or acceptance. Keep completed evidence, record why, and change only affected downstream items. Never rewrite history to make the original plan look right; keep superseded plans and rejected decisions when traceability matters.
