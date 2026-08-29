---
id: "WX-000"
stage: "stage-x"
type: "implementation"
mode: "execute"
depends_on: []
claims: []
owner: null
write_scope: []
max_attempts: 3
stall_after_minutes: null
authority_ref: "authorization.yaml"
estimated_scope: "small"
---

# WX-000: One independently verifiable outcome

## Outcome

State what becomes observably true when this item completes.

## Preconditions

- The stage is unlocked.
- This item is `ready` or `in_progress`.
- Every dependency is `completed`.

## Required context

- List exact sources required for this item.

## Allowed scope

- List exact files, resources, people, or environments.

## Forbidden scope

- List adjacent or high-risk work that must remain untouched.

## Steps or decision criteria

1. Each step produces an inspectable intermediate result.

## Verification

```text
exact-command-or-check-without-placeholders
```

## Acceptance criteria

- Every criterion is binary or has a named qualitative rubric and reviewer.

## Recovery or contingency

- Define safe rollback, preserved evidence, or the point of no return and compensating action.

## State transitions

- Start: set this item to `in_progress`, add it to `active_items`, and remove it from `next_items`.
- Success: set it to `completed`, link mandatory evidence in the registry, remove it from `active_items`, and recompute `next_items`.
- Blocked: set it to `blocked`, link a blocker record, remove it from `active_items`, preserve results, and do not open gates.
- Canceled or superseded: record the reason and downstream impact, remove it from active and eligible pointers, and do not satisfy dependencies that require completion.
