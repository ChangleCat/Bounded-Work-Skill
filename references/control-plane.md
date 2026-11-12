# Work Control Plane

Read when work needs persistent state across sessions, owners, or environments, or when auditing one.

## Lightest viable form

| Work shape | Mechanism |
|---|---|
| One focused session, low risk | In-turn checklist |
| Dependent items or sessions, one owner (solo profile) | One plan file with card checklist; git as history and evidence |
| Multi-owner resumable work | State file plus work cards |
| Multiple owners, stages, or approval gates | Registry, stage packets, evidence reports, validator |

Promote only when coordination failures become plausible. Don't keep persistent state for work that will finish safely this turn.

## Sources of truth

Each fact has one owner; generate summaries instead of copying mutable status.

| Fact | Owner |
|---|---|
| Outcome, scope, decision authority | Work charter |
| Execution grant: modes, scope, environments, expiry, revocation | Authorization record |
| Acceptance claims and dispositions | Claim registry |
| Work status, active stage, active/eligible pointers, gates, artifact readiness | Work state |
| Item ID, dependencies, card location, item status | Work registry |
| Item outcome, scope, procedure, verification, recovery | Work card |
| Stage boundaries and exit evidence | Stage packet |
| Accepted choice and consequences | Decision record |
| Execution result | Evidence or gate report |
| Attempts, discoveries, transitions, handoffs | Append-only journal |

The journal explains history and never owns status. An attestation manifest proves bytes, never approval. Neither affects eligibility unless policy requires a valid attestation.

## State vocabularies

Use only what's needed, and never reuse a word with another meaning:

- **Work**: `planned | active | blocked | completed | canceled | archived`
- **Stage**: `locked | active | blocked | completed | canceled`
- **Item**: `planned | ready | in_progress | blocked | completed | canceled | superseded`
- **Automated gate**: `not_run | pass | fail`
- **Human gate**: `pending | ready_for_approval | approved | rejected | not_applicable`

`canceled` and `superseded` need a reason and impact record and never satisfy a dependency on completion. `archived` means a closed record preserved inactive, not acceptance. Automation may set automated gates and recommend `ready_for_approval | not_ready | blocked` for human gates; only the named decision owner sets `approved` or `rejected`. `not_applicable` needs a reason.

## Invariants

Useful defaults:

- at most one item `in_progress` unless concurrency is enabled;
- `active_items` equals the registry's `in_progress` items;
- `next_items` holds only `ready` items with completed dependencies, an active stage, and sufficient authority;
- only `ready` or `in_progress` items execute; locked stages expose none;
- completed items have completed dependencies and mandatory evidence links;
- each registry item resolves to one card;
- approved or rejected human gates link a decision and are never set by validation;
- blocked items link a blocker record and keep partial artifacts and diagnostics;
- reopening completed work needs a reason and impact review;
- completed, canceled, or archived work has no active or eligible pointers;
- an executing item resolves to an active, unexpired, unrevoked authorization covering its mode, scope, and environment;
- an item past its attempt budget is blocked;
- evidence for completed items is valid, unexpired, and bound to matching inputs;
- an attestation-required active card matches its digest.

## Context map

Keep shared stage context small; put item-specific sources and commands in the card. For large documentation, keep a map of first-layer sources, second-layer sources with their triggers, expansion conditions, and stable anchors.

## Concurrency and handoff

Parallelize only cards with completed shared prerequisites, disjoint write ownership or a merge owner, independent verification, no shared irreversible operation, and one coordinator for registry and gates. When `max_active_items` > 1, record structured ownership, write scopes, claims or leases if the harness needs them, and a merge owner. Block dispatch on ambiguous ownership, expired claims, or overlapping paths without a merge rule.

A handoff gives card ID, status, changes, evidence, checks not run, open risks, and the exact next action. Chat memory is never the only durable record. Before handoff or resume, apply the [cold-resume contract](traceability-and-resume.md); if first-layer artifacts can't reconstruct outcome, eligibility, proof, next action, and authority, repair them first.

## Close or de-escalate

Close only after final acceptance is approved or recorded as not applicable. Before marking work `completed`:

1. resolve every item as `completed`, `canceled`, or `superseded`, with reasons for the latter two;
2. clear `active_items` and `next_items`;
3. link final evidence and state what it doesn't prove;
4. record whether recovery remains possible, any open rollback window, and who owns residual risk;
5. keep decisions, waivers, blockers, artifact identities, and handoff data needed for audit or recovery.

Use `canceled` for an abandoned outcome and `archived` only once the closed record stays discoverable. If persistent state stops being useful, record why, keep the latest evidence and open obligations, and continue with a simpler plan.

## Deterministic validation

Prefer a read-only, project-native checker that fails closed with exact messages. It should cover statuses and unique IDs, pointer agreement, dependencies, card and evidence links, required card fields, terminal and locked-stage rules, duplicate status sources, gate semantics, authority, budgets, concurrency ownership, evidence freshness and digests, journal syntax, and required attestations. Never weaken it to make state pass. See [tooling.md](tooling.md) for the bundled checker.
