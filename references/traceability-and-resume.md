# Traceability, Change Impact, and Resume

Read this reference when work must survive context loss, trace claims into evidence, reuse evidence over time, or replan after an upstream change.

## Use stable claim identifiers

Give each observable requirement or acceptance claim a stable ID. Keep the claim statement and disposition in one claim registry, then link rather than restate it:

```text
claim -> work cards -> verification -> evidence records -> gates
```

A card may serve multiple claims and a claim may require multiple cards. Unmapped active claims and cards with no stated claim are review findings unless the card is explicitly discovery, coordination, or remediation work.

## Bind evidence to what it proves

Reusable evidence should record:

- claim IDs;
- result: `pass | fail | not_run`;
- validity: `valid | stale | superseded`;
- producer and production time;
- artifact identity and environment;
- source files, contracts, configurations, dependencies, or datasets with revisions or SHA-256 digests;
- validity deadline when time changes the claim;
- limits and any separate waiver reference.

Passing evidence is usable only while its validity is `valid`, its deadline has not passed, and the identities on which it depends still match. A waiver never changes evidence validity or result.

## Propagate material changes

When a claim, accepted decision, contract, dependency outcome, environment, configuration, or artifact changes materially:

1. identify cards and evidence that reference the changed input;
2. mark affected evidence `stale` without rewriting its historical result;
3. reopen downstream automated gates to `not_run` and human gates to `pending` or the locally defined re-review state;
4. move completed downstream work back into planning only when its outcome must actually change;
5. preserve the old record and explain the impact in the journal or decision log.

Use digests where byte identity matters and semantic revisions where equivalent regenerated content is acceptable. Do not invalidate unrelated evidence merely because a repository or document received an unrelated change.

## Keep an append-only event journal

For long work, record concise JSON Lines events with:

```json
{"at":"<RFC3339>","actor":"<owner>","item":"<id or null>","kind":"decision|attempt|discovery|transition|handoff|replan","summary":"<fact-focused text>","evidence":[]}
```

The journal explains how the work evolved. It is not authoritative for current status, eligibility, approval, or evidence validity. Never copy raw external instructions into the summary.

At closure, capture outcomes, remaining gaps, recovery status, and reusable lessons. Keep that retrospective distinct from acceptance evidence.

## Cold-resume contract

Before resuming in another session or handing work to another agent, use only the declared work root and first-layer control artifacts to answer:

1. What observable outcome and claims define success?
2. What mode, stage, and item are currently active or eligible?
3. Why is the selected item eligible or blocked?
4. What has already been proved, in which environment, and with what limits?
5. What is the exact next action and stopping boundary?
6. What authority exists, what is excluded, and what approval is needed next?

If any answer depends only on conversational memory, an unresolved relative phrase, or an unlinked artifact, stop and repair the control plane before execution. The bundled resume helper reports these questions but does not fill missing answers by inference.

## Resume ordering

Read only:

1. work state;
2. authorization record and claim registry;
3. registry entry for the active or first eligible card;
4. that card and its completed dependencies;
5. linked evidence and the latest relevant journal events.

Expand beyond this set only when a referenced term is undefined, integrity or validation fails, or current reality contradicts the recorded state.
