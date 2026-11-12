# Migration Workflow

Read for language, framework, backend, platform, queue, database, or service-boundary migrations. It adds migration-specific constraints to the core instructions. For shadowing, staged cutover, rollback rehearsal, production adoption, or legacy retirement, also read [migration-cutover.md](migration-cutover.md).

## Modes

- **Frame**: assess current and target systems, compatibility envelope, risks, seams, evidence, and migration shape.
- **Bootstrap**: set up frozen contracts, phases, registry, and the first eligible card.
- **Execute**: one eligible card, without absorbing adjacent phases or cutover authority.
- **Audit**: contract parity, state consistency, recovery evidence, and unsupported adoption or retirement claims.

Don't create a migration control plane during a read-only assessment unless asked.

## Compatibility envelope

Before target implementation, record:

1. current and target architecture, including capabilities deliberately staying on the original runtime;
2. externally observable behavior to preserve: APIs, events, authentication, schemas, files, CLI, protocols, operational semantics, errors;
3. data and runtime invariants: source of truth, identity propagation, ownership, ordering, idempotency, commit and acknowledgement points, recovery facts, security boundaries;
4. accepted decisions, deliberate compatibility changes, and who approves them;
5. rollback boundary, compatibility window, and retirement conditions.

Freeze key behavior as machine-readable contracts, golden fixtures, schema snapshots, protocol definitions, or cross-implementation tests. Never edit a baseline to make the target pass; a deliberate change needs an approved decision and updated acceptance first.

## Replacement technique

| Situation | Technique | Key evidence |
|---|---|---|
| Stable external boundary, implementation changes behind it | Strangler-style incremental replacement | Cross-implementation contract tests |
| Internal dependency changes without switching all callers | Branch by abstraction via adapter | Old/new adapter behavior tests |
| Side-effect-free outputs can be compared | Shadow or parallel comparison | Normalized diff with explicit tolerances |
| Schema must serve old and new versions | Expand/contract | Upgrade policy, mixed-version tests |
| Database commit triggers broker work | Transactional outbox plus idempotent dispatcher | Crash-after-commit, duplicate-delivery tests |
| Runtime control moves between implementations | Durable owner record with generation or fencing | Stale-owner rejection, handover and rollback tests |
| Long-running async work changes executors | Durable queue, lease, idempotent completion, reconciliation | Crash, reclaim, duplicate completion, drain tests |

Shadow state-changing requests only if effects are suppressed, isolated, or provably idempotent. Ordinary active/active execution is not shadow traffic.

## Phases

1. **Baseline and feasibility**: inventory contracts and risks, freeze compatibility artifacts, prove the riskiest end-to-end path with failure injection.
2. **Seams**: add adapters or protocols; separate specialized workloads that shouldn't move.
3. **Execution paths**: route the old control plane through the new durable mechanism; prove completion, cancellation, retry, reconciliation, and drain.
4. **Target control plane**: replace target-facing behavior incrementally against frozen contracts.
5. **Release-candidate rehearsal**: compare implementations, exercise production-shaped artifacts, prove recovery, without claiming adoption.
6. **Retirement and closure**: remove obsolete entry points only after approval; finish observability, disaster recovery, ownership handoff, and evidence archive.

Combine or skip phases when risk allows, never to bypass a decision, evidence, or approval boundary.

## Invariants

- Don't move specialized runtime logic just for language uniformity; keep a split architecture when it fits dependencies or operations better.
- Never run two state-changing consumers or owners concurrently without isolation or idempotency plus proven ownership or fencing.
- Avoid database-and-broker dual writes; use an outbox, log, or reconciliation design for cross-system actions.
- Define commit, publish, completion, and acknowledgement order. A restart doesn't prove durable recovery.
- Keep ephemeral notifications apart from durable facts; recover from durable state.
- Keep versions schema-compatible through an explicit expand/contract window; no destructive contraction while rollback depends on the old reader.
- Propagate one stable business ID through submission, queueing, execution, completion, events, persistence, and reconciliation.
- Treat rehearsal, local, release-candidate, staging, and production as separate evidence domains.

## Cross-component decisions

For every cross-component path, define: source of truth; end-to-end identifier; owner and ownership transition; delivery guarantee and duplicate behavior; commit and acknowledgement order; retryable versus terminal failures; reconciliation source and trigger; cancellation; observability and alert thresholds; drain, rollback, and retirement rules. Undefined answers are design blockers, not choices for an executing agent to invent.

## Cards

Use the core card format, adding when relevant: affected contract or invariant; old/new ownership before and after; mixed-version expectation; durable recovery and reconciliation evidence; rollback window and preserved legacy capability; evidence environment.

Separate contract decisions, implementation, parity repair, gate composition, rehearsal, production operations, and retirement when evidence or authority differs. A migration gate composes evidence and never repairs inside the gate.

## Assets

Use core templates from `assets/work-control/` for ordinary cards and decisions, plus only the needed ones from `assets/workflows/migration/`: `compatibility-envelope.template.md` (frozen boundary, approved differences), `migration-state.template.yaml` (replaces the generic work-state template, never alongside it; no duplicate item status), and `cutover-gate-report.template.md` (adoption, recovery, retirement evidence).

## Report fields

Add to the executed-card report when relevant:

```text
Compatibility impact: none | <approved change and decision reference>
Old/new ownership: <before -> after | unchanged>
Rollback window: <open | closed by approved gate | not applicable>
Evidence domain: <local | isolated | release candidate | staging | production>
```
