# Migration Cutover, Recovery, and Retirement

Read only for migration shadowing, staged cutover, rollback rehearsal, production adoption, or legacy retirement, together with the core evidence and authorization rules and [migration.md](migration.md).

## Evidence hierarchy

Strongest first:

1. identified production-shaped artifact exercised in an isolated or release-candidate environment;
2. cross-implementation contract or integration test on real infrastructure;
3. component integration test;
4. unit test of isolated logic;
5. static inspection or documentation.

Mock only local behavior, never semantics owned by a real database, broker, filesystem, identity provider, load balancer, or protocol when they decide correctness.

## Failure scenarios

Choose from the actual design, for example: crash before or after commit; crash after publish before acknowledgement; duplicate delivery and stale lease reclaim; broker or dependency outage and recovery; subscriber disconnect and missed ephemeral events; cancellation before start, during execution, and after terminal state; stale owner or fencing token; partial deployment and mixed-version schema access; invalid credentials, identity, paths, permissions, or configuration; backup restore plus business-level reconciliation.

Each test asserts durable end state and side-effect counts, not just a restart.

## Shadow comparison

Define first: eligible request classes; side-effect suppression or isolation; normalization of timestamps, IDs, ordering, and nondeterminism; exact tolerances and forbidden differences; privacy and redaction; sample size and duration; abort conditions; evidence retention. Never normalize away semantic differences; keep protected raw evidence or checksums for audit.

## Staged cutover

Choose stages that fit the system, not a fixed percentage ladder. Per stage, define: entry evidence and approver; traffic or workload scope; health, error, latency, queue, and consistency thresholds; observation time; automated and manual abort conditions; maximum drain wait; rollback owner and runbook; post-stage reconciliation. Pause at every approval boundary; a successful rehearsal authorizes no real traffic movement.

## Rollback readiness

Requires: a compatible previous artifact; a schema compatibility window or forward-fix plan; verified backup and restore; queue, stream, lease, or in-flight drain semantics; handling of duplicate or partial work; configuration and ownership handback; authentication and session compatibility; per-entity or per-task reconciliation; an explicit point of no return. No destructive cleanup until the rollback window is explicitly closed; keep queue, event, database, and artifact evidence needed for reconciliation.

## Human decisions required

Changing a frozen contract; accepting a new architecture, security, or data-loss tradeoff; moving real traffic or workloads; using production secrets or personal data; destructive schema or data operations; closing the rollback window; declaring legacy retired; accepting incomplete or waived evidence.

Automation may recommend readiness, never approve. Keep release-candidate evidence apart from production facts, and repository retirement apart from claims that every deployment has adopted the target.

## Cutover evidence

Record each gate's evidence with the fields in [evidence-and-gates.md](../evidence-and-gates.md#evidence-record), naming the environment as isolated, release candidate, staging, or production. Immutable artifact identities stop a later build from borrowing earlier evidence.
