# Bounded Work Skill

Bounded Work is a harness-neutral agent skill for planning, executing, resuming, and auditing high-risk, multi-component, or multi-session work.

It turns complex work into bounded, independently verifiable work cards backed by dependency state, durable authority, evidence, recovery boundaries, and approval gates. Migration is included as a specialized workflow rather than treated as the only supported task type.

## When to use it

Use Bounded Work when work spans sessions, owners, components, or environments; when dependency order and recovery matter; or when completion must be auditable.

For a small reversible edit, the skill deliberately falls back to a lightweight objective, scope, and verification checklist instead of creating a full control plane.

## Highlights

- Four modes: Frame, Bootstrap, Execute, and Audit.
- Atomic work cards and a single authoritative item-status source.
- Durable authorization separated from automated validation.
- Claim-to-card-to-evidence-to-gate traceability.
- Evidence freshness, validity windows, and SHA-256 input bindings.
- Retry budgets, bounded concurrency, write ownership, and merge ownership.
- Cold resume without relying on conversation history.
- Separation of untrusted evidence from persistent control instructions.
- Optional control-file attestation and tamper detection.
- A specialized migration and cutover workflow.

## Install

Clone the repository into your Codex skills directory using the canonical skill name:

```bash
git clone https://github.com/ChangleCat/Bounded-Work-Skill.git ~/.codex/skills/bounded-work
```

Or ask a compatible skill installer to install the `bounded-work` skill from this repository. In harnesses without named skill invocation, point the agent to [SKILL.md](SKILL.md) using that harness's supported mechanism.

The core instructions have no runtime dependency. Optional deterministic helpers require Python 3.11+ and PyYAML 6.x:

```bash
python -m pip install -r scripts/requirements.txt
```

## Use

Explicit invocation examples:

```text
Use $bounded-work to frame this cross-service redesign without changing files.

Use $bounded-work to establish resumable coordination for this reliability program.

Use $bounded-work to continue the one eligible card and update its evidence.

Use $bounded-work to audit release readiness without repairing findings.
```

The skill infers the narrowest applicable mode and explains the immediate boundary in plain language. Bootstrap creates coordination artifacts but does not grant Execute authority.

## Optional tooling

The reference tools can initialize, validate, resume, and attest a file-backed control plane:

```bash
python scripts/init_work.py <work-root> \
  --title "<outcome>" \
  --owner "<owner>" \
  --authority-ref "<request or decision>" \
  --claim "<observable success claim>"

python scripts/validate_work.py <work-root>
python scripts/resume_work.py <work-root>
python scripts/attest_control.py <work-root> verify
```

See [reference tooling](references/tooling.md) for the full command set and security boundaries.

## Repository layout

```text
SKILL.md       Core routing and operating contract
agents/        Optional OpenAI UI metadata
references/    Conditional workflow and maintainer guidance
assets/        Control-plane and migration templates
scripts/       Optional deterministic reference tools
evals/         Behavioral and discovery evaluation definitions
tests/         Structural and tooling regression tests
```

## Validate

Run the tooling and structure tests with Python 3.11+ and PyYAML installed:

```bash
python -m unittest discover -s tests -v
```

Behavioral scenarios are defined in [evals/evals.json](evals/evals.json). Passing structural tests does not by itself prove behavioral portability across agent harnesses.

## License

Licensed under the [Apache License 2.0](LICENSE).
