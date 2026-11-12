# Work Control Plane

Read this reference when work needs persistent state across sessions, owners, or environments, or when auditing an existing control plane.

## Use the lightest viable form

| Work shape | Control mechanism |
|---|---|
| One focused session, low risk | In-turn checklist |
| Several dependent items or sessions, one owner (solo profile) | One plan file with a card checklist; git as history and evidence |
| Multi-session or resumable work | State file plus work cards |
| Multiple owners, stages, or approval gates | Registry, stage packets, evidence reports, and validator |

Promote to a heavier form when coordination failures become plausible. Do not maintain persistent state for a task expected to finish safely in the current turn.

## Sources of truth

Keep each fact authoritative in one place:

| Fact | Recommended owner |
|---|---|
| Program outcome, scope, decision authority | Work charter |
| Durable execution grant, allowed modes, scope, environments, expiry, revocation | Authorization record |
| Stable acceptance claims and dispositions | Claim registry |
| Overall work status, active stage, active/eligible pointers, gates, artifact readiness | Work state |
| Item ID, dependencies, card location, task status | Work registry |
| Item outcome, scope, procedure, verification, recovery | Work card |
| Shared stage boundaries and exit evidence | Stage packet |
| Accepted choice and consequences | Decision record |
| Execution result | Evidence or gate report |
| Historical attempts, discoveries, transitions, and handoffs | Append-only event journal |

Generate summaries from the sources of truth rather than copying mutable status into multiple documents.

The event journal explains history but never owns current status. An attestation manifest records byte integrity but never owns approval. Keep both out of eligibility calculations except when policy explicitly requires a valid attestation.

## Use explicit state vocabularies

Use only the states needed by the chosen control mechanism, but do not reuse one word for different meanings:

- **Work**: `planned | active | blocked | completed | canceled | archived`.
- **Stage**: `locked | active | blocked | completed | canceled`.
- **Item**: `planned | ready | in_progress | blocked | completed | canceled | superseded`.
- **Automated gate**: `not_run | pass | fail`.
- **Human gate**: `pending | ready_for_approval | approved | rejected | not_applicable`.

`canceled` and `superseded` require a reason and impact record. They do not satisfy dependencies that require a completed outcome. `archived` means a closed work record was preserved and made inactive; it is not another form of acceptance.

An automated report may set only an automated gate or recommend `ready_for_approval | not_ready | blocked` for a human gate. Only the named decision owner may set `approved` or `rejected`. Record a reason when a gate is `not_applicable`.

## State invariants

Choose invariants appropriate to the work. Useful defaults include:

- at most one item is `in_progress` unless concurrency is explicitly enabled;
- `active_items` exactly matches registry items in `in_progress`;
- `next_items` contains only `ready` items with completed dependencies, an active stage, and sufficient authority;
- only `ready` or `in_progress` items may execute;
- completed items have completed dependencies and links to mandatory evidence;
- locked stages expose no executable cards;
- each registry item resolves to one card;
- approved or rejected human gates resolve to a decision reference and cannot be set by automated validation;
- blocked items resolve to a blocker record and preserve partial artifacts and diagnostic evidence;
- reopening completed work requires a reason and impact review.
- completed, canceled, or archived work has no active or eligible pointers.
- an executing item resolves to an active, unexpired, unrevoked authorization record that permits its mode, scope, and environment;
- an item whose attempts exceed its budget is blocked rather than eligible;
- evidence required by completed items is valid, unexpired, and still bound to matching inputs;
- an attestation-required active card matches its recorded digest.

## Progressive context map

Keep shared stage context small. Put item-specific source files, specifications, datasets, and commands in the card. If repeated routing into large documentation is needed, maintain a context map with:

- first-layer required sources;
- second-layer sources read only after a named trigger;
- conditions that justify expanding context;
- stable anchors or headings.

This prevents both under-reading and indiscriminate loading.

## Concurrency and handoff

Only parallelize cards that have:

- completed shared prerequisites;
- non-overlapping write ownership or a defined merge owner;
- independent verification;
- no shared irreversible operation;
- one coordinator responsible for registry and gate state.

When `max_active_items` exceeds one, record structured ownership, non-overlapping write scopes, claim or lease information when the harness needs it, and a merge owner. On ambiguous ownership, expired claims, or overlapping paths without a merge rule, block dispatch.

A handoff should include the card ID, current status, changes made, evidence produced, checks not run, unresolved risks, and exact next action. Do not rely on conversational memory as the only durable record for long-running work.

Before a handoff or resume, apply the [cold-resume contract](traceability-and-resume.md). If the declared first-layer artifacts cannot reconstruct outcome, eligibility, proof, next action, and authority, repair the control plane before work continues.

## Close or de-escalate the control plane

Close persistent work only after the applicable final acceptance is approved or explicitly recorded as not applicable. Before setting work to `completed`:

1. resolve every item as `completed`, `canceled`, or `superseded`, preserving reasons for non-completed resolutions;
2. clear `active_items` and `next_items`;
3. link the final evidence or gate report and record what it does not prove;
4. record whether recovery remains possible, any open rollback window, and the owner of residual risk;
5. preserve decisions, waivers, blockers, artifact identities, and handoff information needed for audit or recovery.

Use `canceled` when the outcome is abandoned rather than accepted. Use `archived` only after a closed record remains discoverable. If coordination risk falls enough that persistent state is no longer useful, record the de-escalation reason, preserve the latest evidence and unresolved obligations, and continue with a simpler plan or checklist.

## Deterministic validation

When a persistent control plane exists, prefer a read-only project-native checker for:

- valid statuses and unique IDs;
- active/eligible pointer and status agreement;
- completed dependencies;
- card and evidence links;
- required card fields;
- work/stage/item terminal-state and locked-stage rules;
- duplicate status sources;
- gate-type, decision-reference, and human-approval invariants.
- durable authority, retry budgets, concurrency ownership, evidence freshness, bound-input digests, journal syntax, and required attestations.

The checker should fail closed and explain the exact inconsistency. Do not weaken it merely to make state appear valid. The bundled reference checker and its limits are documented in [tooling.md](tooling.md).
