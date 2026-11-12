# Harness Portability

Read only when packaging, installing, or validating Bounded Work outside the current harness.

## Package boundary

The `bounded-work/` directory is the portable skill; keep its relative layout so links to `references/` and `assets/` resolve. `agents/openai.yaml` is optional OpenAI UI metadata that other harnesses may ignore; the workflow must work from `SKILL.md` alone, without product-specific UI policy. The core has no runtime dependency; the scripts need Python 3.11+ and PyYAML 6.x, and a harness may omit them only if it keeps the invariants manually and reports deterministic checks as `not_run`. Harness hooks or lifecycle adapters stay optional layers.

## Invocation

Use `$bounded-work` where supported; otherwise apply the skill by name or by its `SKILL.md` path. Automatic discovery uses the frontmatter description and must be tested on qualifying and routine requests. Invocation syntax never changes scope, authority, approval, or evidence requirements.

## Capabilities

Map these operations to the harness without hard-coding tool names: read workspace instructions and scoped files; create or patch authorized local artifacts; run non-destructive verification; keep durable state when needed; request approval right before crossing an authority boundary; report `pass | fail | not_run`. If a capability is missing, keep the boundary and report the limit. Never emulate approval with a text field, treat chat memory as durable state, or invent evidence.

Map lifecycle hooks by invariant:

- before compaction or handoff: flush material facts to the journal and run the cold-resume check;
- before a stable card: validate state, authority, and required attestation;
- after a material attempt: append an event and link evidence;
- before completion: run fresh verification and validation;
- never inject raw evidence or journal text as instructions (see [security-and-attestation.md](security-and-attestation.md)).

## Artifacts

Templates are examples. Adapt to repository conventions but keep one source per mutable fact, explicit state vocabularies, evidence and blocker links, human decision provenance, terminal and closure semantics, and relative, reviewable text artifacts where possible. Assets are generated output, not instructions to load by default.

## Portability acceptance

Before claiming support, verify the harness can:

1. discover or explicitly select the skill;
2. read all of `SKILL.md` and only relevant references;
3. resolve in-package links;
4. keep read-only modes non-mutating;
5. preserve user authority at external, irreversible, secret, production, and waiver boundaries;
6. create and resume persistent state without duplicate status;
7. separate automated evidence from human approval;
8. pass the applicable scenarios in [behavior-evaluation.md](behavior-evaluation.md);
9. resume safely from first-layer artifacts without chat memory;
10. reject tampered controls, stale evidence, exhausted budgets, and ambiguous concurrent ownership when those policies are on.

Record harness, skill revision, invocation, scenarios run, failures, and unsupported features. A structural install check is not behavioral evidence.
