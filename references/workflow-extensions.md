# Specialized Workflow Extensions

Read when adding or reviewing a subworkflow. Create one only for work with recurring, non-obvious constraints that materially change task design, evidence, recovery, or approval; ordinary domain examples don't qualify.

## Contract

Each specialization defines:

1. selection triggers and near-miss exclusions;
2. how Frame, Bootstrap, Execute, and Audit map to the domain;
3. extra invariants, card fields, evidence, recovery, and human gates;
4. genuinely domain-specific assets or scripts;
5. at least one positive, near-miss, blocker, and authority-boundary evaluation;
6. how it de-escalates or closes.

It may narrow execution, demand stronger evidence, or add blockers. It must not replace core state, scope, evidence, security, or authorization rules; grant permission by being selected; duplicate item status; force its assets on unrelated work; hide repair inside a gate; or hard-code harness tool names where a capability description suffices.

## Layout

Guidance goes in `references/workflows/<name>.md`, templates in `assets/workflows/<name>/`, linked from `SKILL.md` with a clear loading condition. Add scripts only for deterministic, repeated operations, documenting dependencies and failure behavior. Keep reference chains shallow with explicit triggers, and keep evaluations runnable without unrelated workflows.
