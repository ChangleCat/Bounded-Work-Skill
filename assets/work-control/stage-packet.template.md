# Stage X: Outcome boundary

## Status

`locked | active | blocked | completed | canceled`

The current stage is `active`; future stages remain `locked`. A `blocked` stage exposes no new work until its blocker is resolved. `canceled` is terminal and requires a reason and downstream impact record.

## Objective

Define the stage result and why it forms a coherent acceptance boundary.

## Entry conditions

- List required completed items, decisions, environments, and approvals.

## Shared context

- Include only information needed by most items in this stage.

## Invariants and constraints

- Define scope, safety, ownership, evidence, and recovery rules.

## Non-goals

- Exclude future and adjacent work explicitly.

## Exit evidence

- List exact artifacts, checks, reports, and reviews required.

## Approval gate

- Name the decision, approver role, and what automation may mark ready for approval but cannot approve.
