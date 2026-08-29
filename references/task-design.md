# Atomic Work Design

Read this reference when framing a complex outcome, building a task graph, or splitting an oversized card.

## Start from outcomes

Decompose from observable results rather than repository folders or job titles. A useful work breakdown answers:

- What becomes true when this item completes?
- Who or what consumes the result?
- What evidence proves it?
- What must already be true?
- Can it be accepted or recovered independently?

Avoid activity-only items such as “work on tests” or “improve security.” Name the specific state change.

## Card types

Use card types to keep authority and evidence clear:

| Type | Produces | Typical evidence |
|---|---|---|
| Discovery | Verified facts and open questions | Inventory, measurements, reproduction |
| Decision | Approved choice and consequences | Decision record and approver |
| Contract | Frozen behavior or interface | Schema, fixture, acceptance test |
| Implementation | A bounded behavior or artifact | Focused tests and inspection |
| Integration | Connected components | End-to-end or environment evidence |
| Remediation | Closure of a known finding | Reproduction before/after and regression test |
| Operation | Authorized external or environment change | Preflight, execution log, postconditions |
| Gate | Acceptance or rejection of prior evidence | Evidence matrix and human decision when required |

Do not mix a decision with the implementation that depends on it when the decision is unresolved. Do not mix an external operation with preparatory code merely to avoid an approval pause.

## Atomicity test

Split a card if any answer is yes:

1. Can part of the result be useful and accepted independently?
2. Are there multiple unrelated consumers or owners?
3. Do different parts need different authorization or environments?
4. Can one verification fail while another part still legitimately completes?
5. Would recovery require reverting only part of the card?
6. Does it require unrelated context or overlapping write ownership?
7. Is its outcome likely to exceed one focused working session?

Small tasks may be grouped only when they share one outcome, scope, verification set, and recovery boundary.

## Dependency graph

Dependencies should express facts, not preferred ordering. Item B depends on A only when B would be unsafe, invalid, or unverifiable without A's completed result.

Prefer a directed acyclic graph over a forced serial chain. Expose multiple ready cards only when concurrent ownership is safe and explicitly permitted. Keep shared-state updates under one coordinator.

Common dependency mistakes:

- depending on an entire stage when one artifact is sufficient;
- omitting a decision or contract dependency;
- using status to represent artifact readiness in two places;
- completing a prerequisite without its required evidence;
- unlocking implementation before the environment or authority exists.

## Trace claims and authority

For persistent work, link each card to stable claim IDs rather than copying requirement text. Give coordination-only cards an explicit type so they are not mistaken for claim-closing implementation.

An executable card should resolve a durable authority reference. Record its operating mode and any environment or action boundary that is narrower than the overall grant. A card cannot widen the authorization record that makes it eligible.

When parallel work is enabled, structure `owner` and `write_scope` so a validator can detect overlap. Name a merge owner for shared integration. Free-form prose about ownership is not sufficient for concurrent dispatch.

## Bound retries and stalls

Define a proportional retry, time, cost, or stall boundary when repeated attempts could hide a design problem, consume material resources, or repeat external effects. Record each materially different attempt and its result.

Exhausting a budget changes the card to `blocked`; it does not authorize a broader attempt, a different environment, weaker verification, or an automatic reset of the counter. A user or decision owner may approve a revised budget after reviewing the evidence.

## Binary acceptance criteria

Write criteria that another reviewer can evaluate without interpreting intent:

- Prefer “all three supported inputs produce the recorded outputs” over “handles common cases.”
- Prefer “rendered pages contain no clipping at the target size” over “layout looks good.”
- Prefer “finding SEC-12 cannot be reproduced and its regression test passes” over “security is improved.”
- Prefer “release artifact digest X passes install and rollback checks” over “release is ready.”

Qualitative review is valid when the outcome is qualitative, but name the reviewer, rubric, and decision status.

## Replanning

Replan when new evidence invalidates dependencies, scope, risk, or acceptance criteria. Preserve completed evidence, record why the plan changed, and update only affected downstream items.

Do not rewrite history to make the original plan appear correct. Superseded plans and rejected decisions may remain as audit evidence when the work requires traceability.
