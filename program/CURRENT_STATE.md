# Current state — post-reorganization addendum

Recorded 2026-11-16 by the Opsle autopilot (backlog item O13).

## Why this file exists

`program/registry.json` and the generated `PROGRAM_STATUS.md` are the
sealed September 2026 post-consolidation record. They are not stale by
accident. `tools/validate_program.py` pins them to
`program/evidence/post-consolidation/inventory.json`: repository URLs
must read `github.com/opsle/<name>`, current HEADs must equal the
inventory pins, membership must equal the inventory lists, and
`program_control.workload_authority` must read `opsle/tasks`. The
registry validates clean exactly as sealed (23 repositories, 19
concepts, 5 experiments, checked 2026-11-16). Treat it as history.

This addendum records what changed after the seal. It makes no change
to the sealed record.

## What changed after September 2026

- The `opsle` GitHub organization was deleted in October 2026. Every
  live repository now sits under `sneakocom`. URLs in the sealed
  registry that point at the old organization survive only as
  redirects or not at all.
- Opsle Tasks retired on 2026-10-31. The repository was deleted and
  tasks.opsle.com returns 410 Gone. The sealed registry still names
  it the workload authority because the validator requires that
  wording; that is a property of the seal, not a current claim.
- The `.github` repository was deleted with the organization.
- One repository was added after the seal:
  `sneakocom/context-budget-preflight` (2026-11-13), a deterministic
  preflight that plans agent context loading and shows token savings
  before any model call.

## Live repositories and HEADs, 2026-11-16

| Repository | HEAD | Notes |
|---|---|---|
| gearbox | 4cab15c3180d0a95d70a0dab0ecb64aaccdbbf61 | Core 4. Verified weekly 2026-11-16. |
| context-firewall | d614c4accbd832fa5eb0a9be00c872661067dc10 | Core 4. Verified weekly 2026-11-16. |
| affected-verification | 0789231384b298747f560bda5c17675960f40f1d | Core 4. Verified weekly 2026-11-16. |
| visible-value | e5685ac1a307affee8687f223fab51e3466f0e90 | Core 4. Verified weekly 2026-11-16. |
| agent-trajectory-profiler | a18e7233e1c7607ca02a5e7d7a26f1c6b497792e | Supporting research. HEAD inspected 2026-11-16; no new verify run claimed. |
| decision-evidence-protocol | 6a4dd402387bde2d00e4ecbfd37b5923d8dcbd5a | Supporting research. HEAD inspected 2026-11-16; no new verify run claimed. |
| semantic-edit-protocol | 84275765d6fa6c920d269da15e7dfc8def54d11f | Supporting research, theory stage. HEAD inspected 2026-11-16; no new verify run claimed. |
| research | 939003ee824e4085653c735b0f2c22a2eb0318f1 | This repository, main HEAD before this addendum. |
| site | fe20ad76f7ba2d82f0d1f8ea2ba5d9a69dbd1bb3 | Private. Serves opsle.com. |
| context-budget-preflight | c5f423fbfce3e2c69890ee71c3c6c857a19677b2 (main after its CI PR merged 2026-11-16) | Prototype tool. Listed on opsle.com /repositories from 2026-11-16. |

The Core 4 verification is the Monday weekly run: fresh clones, each
product's documented verify run direct and through the Codex and Muse
agent CLIs, 12 of 12 cells passing on 2026-11-16 with counts unchanged
(Gearbox 26, Context Firewall 45/45 plus 33 conformance fixtures,
Affected Verification 126 pass plus 1 documented skip with determinism
12/12 and conformance 15, Visible Value 7/7).

## The open decision

Regenerating `registry.json` itself means opening a new registry
epoch: a new inventory, validator changes to match, and a new
workload-authority framing now that Tasks is retired. That is a
program-direction decision, not a data correction, so the autopilot
has not done it. This addendum is the factual bridge until that
decision is made.
