# Bounded Work Behavior Evaluation

Read only when maintaining, releasing, or forward-testing the skill. It defines observable behavior, not required wording.

## Scenarios

Scenario prompts, fixtures, expected and forbidden behavior are in [../evals/evals.json](../evals/evals.json); discovery queries are in [../evals/trigger-evals.json](../evals/trigger-evals.json). Use those files as the single source; don't restate them here.

## Method

Run each scenario in an isolated scratch project or a read-only fixture suited to its mode. Give the evaluating agent only the realistic request, the skill, and normal context, never the expected answer, suspected failure, or fix.

Record: skill revision; harness or product; model and settings when available; fixture identity and writability; observed mode, files or systems read, mutations, orientation, and result; each expectation as `pass | fail | not_run`; evidence path and run limits. When the harness exposes them, also capture tokens, duration, user interruptions, unsafe mutations, false completion claims, and artifacts created.

Compare candidates against the prior release, not only a no-skill baseline. Use an independent agent run when the harness allows and the user has authorized delegation; otherwise label the review non-independent. An unrun scenario or phrase match is never behavioral proof.

## Discovery and portability

In each supported harness, test one routine one-shot request and one qualifying complex request without explicit invocation, and record whether discovery skips the first and selects the second. Then run BW-E02, BW-E05, and BW-E07 through the harness's explicit invocation, even without `$skill-name` syntax.

Claim support for a harness only after its applicable scenarios pass. Report unsupported invocation, reference loading, approval semantics, or artifact handling as compatibility gaps instead of weakening the skill. Structural script tests cover only the tooling.
