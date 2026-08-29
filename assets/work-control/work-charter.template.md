# {{WORK_TITLE}}

## Outcome

{{OUTCOME}}

## Definition of done

- Every active claim in `claims.yaml` is supported by valid evidence or explicitly resolved by an authorized decision.
- Mandatory validation passes without relying on conversational memory.

## Included scope

- {{WORK_ROOT}}

## Excluded scope

- Production, external, irreversible, secret-bearing, or destructive actions unless separately authorized.

## Constraints

- Preserve existing work and applicable workspace instructions.
- Execute only cards whose dependencies, scope, authority, budget, and evidence requirements validate.

## Risks and recovery

- Stop at the last verified state when a boundary is unclear.
- Preserve evidence and record blockers before recovery or replanning.

## Authority

- Durable record: `authorization.yaml`
- Bootstrap authority source: {{AUTHORITY_SOURCE}}
- Bootstrap creates coordination artifacts only; it does not grant Execute authority.
