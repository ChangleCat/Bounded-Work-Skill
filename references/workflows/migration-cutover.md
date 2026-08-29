# Migration Cutover, Recovery, and Retirement

Read this reference only for migration shadowing, staged cutover, rollback rehearsal, production adoption, or legacy retirement. Apply it together with the core evidence and authorization rules and [migration.md](migration.md).

## Evidence hierarchy

Prefer the strongest practical evidence:

1. Identified production-shaped artifact exercised in an isolated or release-candidate environment.
2. Cross-implementation contract or integration test against real infrastructure.
3. Component integration test.
4. Unit test of isolated logic.
5. Static inspection or documentation assertion.

Use mocks for local behavior, not for semantics owned by a real database, broker, filesystem, identity provider, load balancer, or network protocol when those semantics determine correctness.

## Failure and recovery scenarios

Select scenarios from the actual design. Common examples include:

- crash before and after database commit;
- crash after publish but before acknowledgement;
- duplicate delivery and stale lease reclaim;
- broker or dependency outage followed by recovery;
- subscriber disconnect and missed ephemeral events;
- cancellation before start, during execution, and after terminal state;
- stale owner or fencing token;
- partial deployment and mixed-version schema access;
- invalid credentials, identity, paths, permissions, or configuration;
- backup restore followed by business-level reconciliation.

Each failure test must assert durable end state and side-effect cardinality, not merely that a process restarted.

## Shadow comparison

Define before running:

- eligible request classes;
- how side effects are suppressed or isolated;
- normalization rules for timestamps, IDs, ordering, and nondeterminism;
- exact tolerances and forbidden differences;
- privacy and redaction rules;
- sample size and duration;
- abort conditions;
- evidence retention.

Do not normalize away semantic differences. Keep protected raw evidence or checksums sufficient for audit.

## Staged cutover

Use stages appropriate to the system rather than a mandatory percentage sequence. For each stage, define:

- entry evidence and approver;
- traffic or workload scope;
- health, error, latency, queue, and data-consistency thresholds;
- observation duration;
- automated and manual abort conditions;
- maximum drain wait;
- rollback owner and exact runbook;
- post-stage reconciliation.

Pause at every approval boundary. A successful rehearsal authorizes no real traffic movement by itself.

## Rollback readiness

A credible rollback includes:

- a compatible previous artifact;
- schema compatibility window or forward-fix plan;
- verified backup and restore procedure;
- queue, stream, lease, or in-flight drain semantics;
- treatment of duplicate or partially completed work;
- configuration and ownership handback;
- authentication and session compatibility;
- per-entity or per-task reconciliation;
- explicit point of no return.

Avoid destructive cleanup until the rollback window is explicitly closed. Preserve durable queue, event, database, and artifact evidence needed for reconciliation.

## Adoption and retirement gates

Require an explicit human decision for:

- changing a frozen compatibility contract;
- accepting a new architecture, security, or data-loss tradeoff;
- moving real traffic or workloads;
- using production secrets or personal data;
- destructive schema or data operations;
- closing the rollback window;
- declaring a legacy implementation retired;
- accepting incomplete or waived evidence.

An automated report may recommend readiness for approval but cannot grant approval. Keep release-candidate evidence separate from production facts, and keep repository retirement separate from the claim that every deployed environment has adopted the target.

## Cutover evidence record

For each gate, record:

| Field | Meaning |
|---|---|
| Requirement | Binary claim being evaluated |
| Evidence producer | Exact test, script, query, or reviewer |
| Artifact identity | Version, revision, digest, package checksum, schema version |
| Environment | Isolated, release candidate, staging, or production |
| Result | Pass, fail, or not run |
| Time and owner | Who or what produced the result and when |
| Limits | What this evidence does not prove |
| Approval | Human decision reference when required |

Immutable artifact identities prevent a later build from borrowing earlier evidence.
