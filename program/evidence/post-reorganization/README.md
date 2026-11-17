# Post-reorganization evidence inventory (epoch 2)

`program/registry.json` remains the sole machine-readable portfolio and
priority authority. This inventory is subordinate evidence for epoch 2,
not a queue or a second portfolio.

Epoch 2 opened on 2026-11-17 by Michael Davis's decision ("Start a new
epoch", chosen over keeping the epoch-1 registry sealed with addenda).
The epoch-1 registry is preserved unchanged at
`program/history/epoch-1/registry.json`, and the epoch-1 inventory
remains at `program/evidence/post-consolidation/inventory.json`,
untouched.

What changed from epoch 1:

- Every live repository now sits under `sneakocom`; the `opsle`
  organization was deleted in October 2026. Registry `github_url`
  values are canonical `sneakocom` URLs, and the validator pins them.
- Opsle Tasks retired on 2026-10-31 (repository deleted,
  tasks.opsle.com returns 410 Gone) and `.github` was deleted with the
  organization. Both are historical members in epoch 2.
- `sneakocom/context-budget-preflight` (published 2026-11-13) joined
  the current membership.
- Workload and task-management authority moved from the retired Tasks
  system to the Opsle research program itself
  (`sneakocom/research`), recorded as
  `program_control.research_stewardship`.
- Current membership is 10 repositories; historical membership is 14;
  the registry records 24 repositories in total.

Observation method: GitHub repository metadata and default-branch
HEADs observed 2026-11-17 through the GitHub API. Core 4 HEADs are the
revisions verified by the 2026-11-16 weekly fresh-clone verify run
(12 of 12 cells passing) and are unchanged since. Supporting
repositories, research, site, and context-budget-preflight are
HEAD-inspected only; no new verify run is claimed for them.
`consolidation_destinations` is carried over unchanged because the
validator pins it to the epoch-1 final consolidation receipt, which
remains the record of that consolidation.

The factual bridge that preceded this epoch is
`program/CURRENT_STATE.md`.
