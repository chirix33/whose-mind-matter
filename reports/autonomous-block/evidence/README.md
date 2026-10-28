# Evidence bundle index

- `episodes-round2.csv`, `episodes-round3.csv`: one row per episode (state, unit, condition, replicate, dispatch index, frozen note sha256, outcome, return, steps, actions, decision tokens, wall clock). No hidden state.
- `traces/*.visible.json`: representative episodes. Each contains the robot-visible history, the notes shown to the policy, the actions and the policy calls.
  - Files whose condition is `privileged` show privileged content **by design**: that condition gives the policy the true content.
  - The hidden state and unit-fidelity records for each trace are kept apart, in gitignored `data/autonomous-block/<trace>.privileged.json`.
- `manifests/`: run manifests (commit, dirty paths, configuration, prompt hashes, timing) for every run in this block.
- `api-spend-ledger-final.json`: the authoritative spend ledger at block end.
- `block-source-diff.patch`: focused diff of `src/`, `scripts/`, `prompts/`, `tests/` and `AGENTS.md`, from the pre-block commit `9bb0193` to the end of the block.
- Source archive: `reports/autonomous-block/source-<commit>.zip` (gitignored; regenerate with `git archive`).
