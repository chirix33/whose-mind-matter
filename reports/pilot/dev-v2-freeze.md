# Frozen development set `dev-v2` (Stage 2 pilot)

Frozen by `scripts/freeze_dev_groups.py`, run `pilot-freeze-20261028-055959-68a918`, commit `4bb749c`, seed 20261028, **before any LLM output was produced or inspected.**
**Development data only: never to be used as confirmatory test data.** Set hash (over file hashes): `3e8afe544f7e2900df54777048dcaa38a4d73eaa01d33c78fa2d1b36e7e6fd8e`.

- Groups: **36**; instances: **80**; variants stay inside their group and share one hidden world.
- Groups per family: {'ambiguity': 4, 'conflict': 4, 'corroborated': 4, 'directed_perspective': 4, 'distractors': 4, 'false_belief': 4, 'nested_reliability': 4, 'relevance_shift': 4, 'stop': 4}
- Instances per family: {'stop': 8, 'ambiguity': 8, 'false_belief': 16, 'distractors': 8, 'conflict': 8, 'nested_reliability': 8, 'directed_perspective': 8, 'relevance_shift': 8, 'corroborated': 8}
- Instances by stakes: {'1.0': 64, '4.0': 16}
- Exclusions (rules E1–E4, see script): 0 instances; excluded groups: none
- Instances whose face-value defaults are jointly unsatisfiable at h (D-008 audit; logged, not filtered): 12

## Symbolic categories (grounded_typed, face value; privileged evaluator annotations)

These categories may not transfer to the LLM; the pilot checks whether they do.

| category | instances |
|---|---|
| carryover | 8 |
| mixed_flip_and_carryover | 19 |
| useful_current_action | 13 |
| zero_value_stop | 40 |

Required depth by family (family:depth → instances):

| family:depth | instances |
|---|---|
| ambiguity:0 | 8 |
| conflict:0 | 5 |
| conflict:1 | 3 |
| corroborated:0 | 3 |
| corroborated:1 | 5 |
| directed_perspective:2 | 8 |
| distractors:0 | 8 |
| false_belief:0 | 8 |
| false_belief:1 | 8 |
| nested_reliability:1 | 8 |
| relevance_shift:1 | 8 |
| stop:0 | 8 |

## Prespecified paired-intervention states (9)

Selected per category in the order useful, zero/STOP, negative, carryover, walking a fixed sha256 order of instance ids (independent of any LLM outcome); at most 3 per category, one family per category, no instance twice. Negatives fall back to the scalar records in a declared order (column `record`). Counts above are multi-label.

| instance | decision state | unit | symbolic category | record |
|---|---|---|---|---|
| dev-v2-false_belief-g0-stakes4-evidence0 | t0 | K(wen) | useful_current_action | grounded_typed/face_value |
| dev-v2-conflict-g1-stakes4 | t0 | K(judy) | useful_current_action | grounded_typed/face_value |
| dev-v2-corroborated-g3-evidence0 | t0 | K(grace) | useful_current_action | grounded_typed/face_value |
| dev-v2-ambiguity-g0-evidence1 | t0 | K(carol) | zero_value_stop | grounded_typed/face_value |
| dev-v2-distractors-g3-permuted1 | t0 | K(leo) | zero_value_stop | grounded_typed/face_value |
| dev-v2-conflict-g3-stakes1 | t0 | K(mia) | zero_value_stop | grounded_typed/face_value |
| dev-v2-conflict-g2-stakes1 | t0 | K(heidi) | negative | grounded_scalar/face_value |
| dev-v2-directed_perspective-g2-permuted1 | t0 | K(yara) | negative | grounded_scalar/hedged |
| dev-v2-relevance_shift-g1-stakes1 | t0 | K(dave) | carryover | grounded_typed/face_value |

## Files

Data (gitignored, regenerable from code + seed): `data/pilot/dev-v2/`

| file | sha256 |
|---|---|
| interventions.json | `dc1cd96d4b9b35f98662b7b45adc0dff8d4b67f43ef9a419a9630907d66210fc` |
| privileged.jsonl | `1177fd88076192e1246692ce7368ba1c268ddb176d041c2cf32ba0254c8fa7b1` |
| public.jsonl | `dbcf2220ae4d1acfb14bae4044c35c323665d97d629bb17135acbc3639573694` |
