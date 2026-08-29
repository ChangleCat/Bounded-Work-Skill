---
id: "{{ITEM_ID}}"
stage: "{{STAGE}}"
type: "decision"
mode: "bootstrap"
depends_on: []
claims: []
owner: "{{OWNER}}"
write_scope:
  - "work-charter.md"
  - "claims.yaml"
max_attempts: 3
stall_after_minutes: null
authority_ref: "authorization.yaml"
estimated_scope: "small"
---

# {{ITEM_ID}}: Accept the work charter and claim coverage

## Outcome

The desired outcome, scope, authority boundaries, and observable success claims are reviewable without relying on chat history.

## Preconditions

- The control plane passes deterministic validation.
- Bootstrap authority remains active.

## Required context

- `work-charter.md`
- `claims.yaml`
- `authorization.yaml`

## Allowed scope

- `work-charter.md`
- `claims.yaml`
- control-plane pointers needed to record this card's result

## Forbidden scope

- Product implementation, production operations, external mutation, destructive action, or any Execute-mode work.

## Decision criteria

1. The outcome and definition of done reflect the user's request.
2. Every active claim is observable and has an owner.
3. Included and excluded scope are explicit enough to prevent material drift.
4. Any Execute authority required for later cards is obtained as a separate durable decision.

## Verification

```text
{{VALIDATE_COMMAND}}
```

## Acceptance criteria

- Deterministic validation passes.
- The charter and claim registry are accepted or revised by an authorized owner.

## Recovery or contingency

- Keep the card `ready` and record the exact missing decision when acceptance is not available.

## State transitions

- Start: set this item to `in_progress`, add it to `active_items`, and remove it from `next_items`.
- Success: set it to `completed`, link the acceptance evidence, remove it from `active_items`, and recompute `next_items`.
- Blocked: set it to `blocked`, link a blocker record, remove it from `active_items`, and preserve the draft charter and claims.
