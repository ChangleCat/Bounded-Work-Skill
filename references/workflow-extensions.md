# Specialized Workflow Extensions

Read this reference when adding or reviewing a professional subworkflow under Bounded Work.

A specialization should exist only when a class of work has recurring, non-obvious constraints that materially change task design, evidence, recovery, or approval. Ordinary domain examples do not justify a new workflow.

## Extension contract

Each specialization must define:

1. precise selection triggers and near-miss exclusions;
2. how Frame, Bootstrap, Execute, and Audit map into the domain;
3. additional invariants, card fields, evidence, recovery, and human gates;
4. assets or scripts that are genuinely domain-specific;
5. at least one positive, one near-miss, one blocker, and one authority-boundary evaluation;
6. how the workflow de-escalates or closes.

A specialization may narrow allowed execution, require stronger evidence, or introduce domain-specific blockers. It must not:

- replace the core state, scope, evidence, security, or authorization rules;
- grant permission because the workflow was selected;
- duplicate item status in a second registry;
- force its assets on unrelated work;
- hide implementation repair inside an acceptance gate;
- hard-code harness tool names into the portable core when a capability description is sufficient.

## Package layout

Keep substantial guidance in `references/workflows/<name>.md` and generated templates in `assets/workflows/<name>/`. Link the workflow directly from `SKILL.md` with a clear loading condition. Add scripts only for deterministic, repeated operations and document their dependencies and failure behavior.

When a specialization needs another reference, keep the chain shallow and explain the exact trigger. Its behavior evaluations should remain runnable without loading unrelated workflows.
