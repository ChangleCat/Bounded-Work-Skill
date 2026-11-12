# Traceability, Change Impact, and Resume

Read when work must survive context loss, trace claims to evidence, reuse evidence over time, or replan after an upstream change.

## Stable claim IDs

Give each acceptance claim a stable ID, keep its statement and disposition in one claim registry, and link rather than restate:

```text
claim -> work cards -> verification -> evidence records -> gates
```

Cards and claims are many-to-many. Unmapped active claims, and cards with no claim that aren't discovery, coordination, or remediation, are review findings.

## Bind evidence

Reusable evidence records the fields in [evidence-and-gates.md](evidence-and-gates.md#evidence-record), with validity `valid | stale | superseded` and the source files, contracts, configurations, dependencies, or datasets it depends on, by revision or SHA-256. A pass is usable only while valid, before its deadline, and while those identities match. Waivers never change result or validity.

## Propagate material changes

When a claim, decision, contract, dependency outcome, environment, configuration, or artifact changes materially:

1. find cards and evidence referencing it;
2. mark affected evidence `stale`, keeping its historical result;
3. reopen downstream automated gates to `not_run` and human gates to `pending` or the local re-review state;
4. move completed downstream work back to planning only if its outcome must change;
5. keep the old record and explain the impact in the journal or decision log.

Use digests where byte identity matters and semantic revisions where regenerated equivalents are fine. Don't invalidate evidence because of unrelated changes.

## Event journal

For long work, append concise JSON Lines events:

```json
{"at":"<RFC3339>","actor":"<owner>","item":"<id or null>","kind":"decision|attempt|discovery|transition|handoff|replan","summary":"<fact-focused text>","evidence":[]}
```

The journal explains history; it never decides status, eligibility, approval, or validity. Never copy raw external instructions into it. At closure, record outcomes, gaps, recovery status, and lessons separately from acceptance evidence.

## Cold-resume contract

Before resuming in a new session or handing off, answer from the declared work root and first-layer artifacts only:

1. What outcome and claims define success?
2. What mode, stage, and item are active or eligible?
3. Why is that item eligible or blocked?
4. What is proved, where, and with what limits?
5. What is the exact next action and stopping boundary?
6. What authority exists, what is excluded, and what approval comes next?

If any answer needs chat memory, an unresolved relative phrase, or an unlinked artifact, repair the control plane before executing. The resume helper reports these questions but never infers missing answers.

Read only, in order: work state; authorization record and claim registry; registry entry for the active or first eligible card; that card and its completed dependencies; linked evidence and recent relevant journal events. Expand only when a term is undefined, integrity or validation fails, or reality contradicts recorded state.
