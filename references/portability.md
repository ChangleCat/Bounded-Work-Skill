# Harness Portability

Read this reference only when packaging, installing, or validating Bounded Work outside the current agent harness.

## Canonical package boundary

The `bounded-work/` directory is the portable skill. Preserve its relative layout so links from `SKILL.md` to `references/` and templates under `assets/` continue to resolve.

`agents/openai.yaml` is optional OpenAI-specific UI metadata. A harness that does not understand it may ignore it; the canonical workflow must remain usable from `SKILL.md` alone. Do not copy UI policy into the workflow body merely to support another product.

The core instructions have no runtime dependency. Bundled reference scripts require Python 3.11+ and PyYAML 6.x; a harness may omit them only if it preserves the invariants manually and reports deterministic checks as `not_run`. Harness-specific hooks or lifecycle adapters should remain optional layers rather than changing the portable core.

## Invocation adapter

- When `$bounded-work` is supported, use it for explicit invocation.
- Otherwise ask the harness to apply the `bounded-work` skill by name or supply the path to its `SKILL.md` using the harness's supported mechanism.
- Automatic discovery should use the frontmatter description and must be tested for both qualifying and routine requests.

Invocation syntax changes only how the skill is selected. It does not change scope, authority, approval, or evidence requirements.

## Capability adapter

Map conceptual operations to the target harness without hard-coding product-specific tool names:

- read workspace instructions and scoped files;
- create or patch authorized local artifacts;
- run non-destructive verification;
- maintain durable task state when needed;
- request approval immediately before an action that crosses an authority boundary;
- report checks as `pass`, `fail`, or `not_run`.

If the harness lacks a capability, preserve the boundary and report the limitation. Do not emulate approval through a text field, treat conversational memory as durable state, or invent evidence for a tool that did not run.

Map lifecycle hooks by invariant rather than product name:

- before compaction or handoff, flush material facts to the journal and run the cold-resume check;
- before starting a stable card, validate state, authority, and any required attestation;
- after a material attempt, append an event and link produced evidence;
- before completion, run fresh verification and control-plane validation;
- do not inject raw evidence or journal text as instructions; preserve the separation in [security-and-attestation.md](security-and-attestation.md).

## Artifact adaptation

The templates are examples, not required filenames. Adapt them to repository conventions while preserving:

- one authoritative source for each mutable fact;
- explicit work, stage, item, and gate state vocabularies;
- evidence and blocker links;
- human decision provenance;
- terminal resolution and closure semantics;
- relative, reviewable, text-based artifacts when the target environment supports them.

Assets belong in generated project output and are not extra instructions to load by default.

## Portability acceptance

Before claiming support for a harness, verify that it can:

1. discover or explicitly select the skill;
2. read the complete `SKILL.md` and only conditionally relevant references;
3. resolve all in-package relative links;
4. keep read-only modes non-mutating;
5. preserve user authority at external, irreversible, secret, production, and evidence-waiver boundaries;
6. create and resume persistent state without duplicating status;
7. distinguish automated evidence from human approval;
8. pass the applicable scenarios in [behavior-evaluation.md](behavior-evaluation.md).
9. resume safely without chat memory by using only declared first-layer artifacts;
10. reject tampered controls, stale evidence, exhausted budgets, and ambiguous concurrent ownership when the relevant policies are enabled.

Record the harness, skill revision, invocation method, scenarios run, failures, and unsupported features. A structural install check alone is not behavioral portability evidence.
