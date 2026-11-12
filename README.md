# Bounded Work Skill

[English](README.md) | [简体中文](README.zh-CN.md)

Bounded Work is a harness-neutral agent skill for planning, executing, resuming, and auditing high-risk, multi-component, or multi-session work.

It turns complex work into bounded, independently verifiable work cards backed by dependency state, durable authority, evidence, recovery boundaries, and approval gates. Migration is included as a specialized workflow rather than treated as the only supported task type.

## When to use it

Use Bounded Work when work spans sessions, owners, components, or environments; when dependency order and recovery matter; or when completion must be auditable.

For a small reversible edit, the skill deliberately falls back to a lightweight objective, scope, and verification checklist instead of creating a full control plane.

For personal projects where you own, decide, and review everything yourself, the skill uses a **solo profile**: one plan file with a card checklist, git as the history and evidence store, and your request as the authorization. It keeps working through cards instead of pausing for approvals that only make sense in a team, and still stops before destructive, production, secret, spending, or public actions. A single agent working alone on your request stays in the solo profile; it escalates to the full workflow only when another person, parallel or scheduled agents, or real external risk enter the picture.

## Highlights

- Four modes: Frame, Bootstrap, Execute, and Audit.
- A solo profile for personal development that drops team-only ceremony.
- Atomic work cards and a single authoritative item-status source.
- Durable authorization separated from automated validation.
- Claim-to-card-to-evidence-to-gate traceability.
- Evidence freshness, validity windows, and SHA-256 input bindings.
- Retry budgets, bounded concurrency, write ownership, and merge ownership.
- Cold resume without relying on conversation history.
- Separation of untrusted evidence from persistent control instructions.
- Optional control-file attestation and tamper detection.
- A specialized migration and cutover workflow.

## Installation

### Recommended: ask your agent to install it

Send the repository URL to an agent that supports installing skills from Git repositories. You can copy this request as-is:

```text
Install the bounded-work skill from this repository:
https://github.com/ChangleCat/Bounded-Work-Skill

Use the repository root as the skill source, install it under the canonical
name bounded-work, and verify that SKILL.md is discoverable after installation.
Do not start any bounded project work yet.
```

In Codex, the agent can use the built-in Skill Installer when it is available. Another harness may use its own installer. Review any requested filesystem or network permission before approving it.

After installation, start a new task and ask:

```text
Use $bounded-work to explain when this skill should and should not be used.
```

The response should recognize the `bounded-work` skill and distinguish full bounded workflows from routine one-shot edits.

### Manual installation for Codex

On macOS or Linux, clone the repository into the default personal skills directory using the canonical folder name:

```bash
git clone https://github.com/ChangleCat/Bounded-Work-Skill.git ~/.codex/skills/bounded-work
```

If `CODEX_HOME` is configured, use `<CODEX_HOME>/skills/bounded-work` instead. On Windows PowerShell, the default destination is:

```powershell
git clone https://github.com/ChangleCat/Bounded-Work-Skill.git "$env:USERPROFILE\.codex\skills\bounded-work"
```

To update an existing manual installation:

```bash
git -C ~/.codex/skills/bounded-work pull --ff-only
```

Confirm that `~/.codex/skills/bounded-work/SKILL.md` exists, then start a new task and invoke `$bounded-work`.

### Other agent harnesses

Use the harness's supported Skill or Agent Skills installation mechanism. The installed skill root must contain [SKILL.md](SKILL.md), and its canonical name is `bounded-work`. If the harness has no installer, clone the repository into its documented personal-skills directory or provide the repository path to the agent explicitly.

The core instructions are harness-neutral and have no runtime dependency. Harness-specific invocation, approval, and lifecycle features are described in [portability guidance](references/portability.md).

### Optional helper dependencies

The deterministic initialization, validation, resume, and attestation helpers are optional. They require Python 3.11+ and PyYAML 6.x:

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
