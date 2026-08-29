# Migration Workflow

Read this reference for language, framework, backend, platform, queue, database, or service-boundary migrations. Apply it together with the core Bounded Work instructions; this file contains only migration-specific decisions and constraints.

For shadow comparison, staged cutover, rollback rehearsal, production adoption, or legacy retirement, also read [migration-cutover.md](migration-cutover.md).

## Choose the migration operating mode

Map the core modes as follows:

- **Frame**: assess the current and target systems, compatibility envelope, risks, seams, evidence, and migration shape.
- **Bootstrap**: establish frozen contracts, phases, task registry, and the first eligible migration card.
- **Execute**: perform one eligible migration card without absorbing adjacent phases or cutover authority.
- **Audit**: evaluate contract parity, state consistency, recovery evidence, and unsupported adoption or retirement claims.

Do not create a migration control plane during a read-only assessment unless the user asks for artifacts.

## Establish the compatibility envelope

Before target implementation, determine and record:

1. Current and target architecture, including capabilities deliberately staying on the original runtime.
2. Externally observable behavior that must remain compatible: APIs, events, authentication, schemas, files, CLI behavior, protocols, operational semantics, and errors.
3. Data and runtime invariants: source of truth, identity propagation, ownership, ordering, idempotency, commit and acknowledgement points, recovery facts, and security boundaries.
4. Accepted decisions, deliberate compatibility changes, and the authority for approving them.
5. Rollback boundary, compatibility window, and legacy retirement conditions.

Freeze important behavior as machine-readable contracts, golden fixtures, schema snapshots, protocol definitions, or cross-implementation tests. Never edit a baseline merely to make the target pass. A deliberate compatibility change requires an approved decision and updated acceptance criteria before implementation.

## Select the replacement technique

| Situation | Preferred technique | Key evidence |
|---|---|---|
| Stable external boundary; implementation changes behind it | Strangler-style incremental replacement | Cross-implementation contract tests |
| Internal dependency must change without switching all callers | Branch by abstraction through an adapter | Old/new adapter behavior tests |
| Read-only or side-effect-free outputs can be compared | Shadow or parallel comparison | Normalized diff with explicit tolerances |
| Persistent schema must serve old and new versions | Expand/contract migration | Upgrade policy and mixed-version tests |
| Database commit triggers broker work | Transactional outbox plus idempotent dispatcher | Crash-after-commit and duplicate-delivery tests |
| Runtime control moves between implementations | Durable owner record with generation or fencing | Stale-owner rejection and handover/rollback tests |
| Long-running asynchronous work changes executors | Durable queue, lease, idempotent completion, reconciliation | Crash, reclaim, duplicate completion, and drain tests |

Do not use shadowing for state-changing requests unless effects are suppressed, isolated, or provably idempotent. Do not describe ordinary active/active execution as shadow traffic.

## Prefer incremental replacement

A useful phase shape is:

1. **Baseline and feasibility**: inventory contracts and risks, freeze compatibility artifacts, and prove the riskiest end-to-end path with representative failure injection.
2. **Create seams**: introduce adapters or protocols and separate specialized workloads that should not move to the target stack.
3. **Move execution paths**: route the old control plane through the new durable mechanism and prove completion, cancellation, retry, reconciliation, and drain behavior.
4. **Implement the target control plane**: replace target-facing behavior incrementally against frozen contracts.
5. **Release-candidate rehearsal**: compare implementations, exercise production-shaped artifacts, and prove recovery without claiming production adoption.
6. **Retirement and operational closure**: remove obsolete entry points only after approval, then complete observability, disaster recovery, ownership handoff, and evidence archive.

Adapt or combine phases when the risk does not justify all six, but never combine work merely to bypass a decision, evidence, or approval boundary.

## Migration-specific invariants

- Do not move specialized runtime logic solely to achieve language uniformity; preserve a split architecture when it better fits dependencies or operational constraints.
- Do not run two state-changing consumers or owners concurrently unless isolation or idempotency plus a proven ownership/fencing mechanism prevents duplicate effects.
- Avoid database-and-broker dual writes. Use a durable outbox, log, or reconciliation design when one business action crosses systems.
- Define commit, publish, completion, and acknowledgement order explicitly. A process restart is not proof of durable recovery.
- Keep ephemeral notifications separate from durable facts. Recovery must use durable state.
- Keep old and new versions schema-compatible through an explicit expand/contract window; do not perform destructive contraction while rollback still depends on the old reader.
- Propagate one stable business identifier across submission, queueing, execution, completion, events, persistence, and reconciliation.
- Treat rehearsals, local environments, release candidates, staging, and production as distinct evidence domains.

## Architecture decision checklist

For every cross-component path, define:

- authoritative source of truth;
- identifier propagated end to end;
- owner and ownership transition;
- delivery guarantee and duplicate behavior;
- commit and acknowledgement order;
- retryable versus terminal failures;
- reconciliation source and trigger;
- cancellation semantics;
- observability and alert thresholds;
- drain, rollback, and retirement rules.

Undefined answers are design blockers, not implementation choices for an executing agent to invent.

## Migration card specializations

Use the core work-card format, adding fields only when relevant:

- compatibility contract or invariant affected;
- old/new ownership before and after the card;
- mixed-version compatibility expectation;
- durable recovery and reconciliation evidence;
- rollback window and preserved legacy capability;
- environment in which the evidence is valid.

Separate contract decisions, implementation, parity repair, gate composition, rehearsal, production operations, and retirement into different cards when they require different evidence or authority. A migration gate composes existing evidence and must not repair implementation failures inside the gate.

## Migration bootstrap assets

Use the core templates under `assets/work-control/` for ordinary cards and decisions. Add only the needed migration-specific templates under `assets/workflows/migration/`:

- `compatibility-envelope.template.md` for the frozen boundary and approved differences;
- `migration-state.template.yaml` for migration-specific artifact and approval fields;
- `cutover-gate-report.template.md` for adoption, recovery, and retirement evidence.

Use `migration-state.template.yaml` in place of the generic work-state template, not beside it. Do not duplicate item status in both the registry and migration state.

## Migration result fields

Add these fields to the core executed-card report when relevant:

```text
Compatibility impact: none | <approved change and decision reference>
Old/new ownership: <before -> after | unchanged>
Rollback window: <open | closed by approved gate | not applicable>
Evidence domain: <local | isolated | release candidate | staging | production>
```
