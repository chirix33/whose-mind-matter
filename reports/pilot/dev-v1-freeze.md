# Frozen development set `dev-v1` (Stage 2 pilot)

Frozen by `scripts/freeze_dev_groups.py`, run `pilot-freeze-20261028-053915-b0eb70`, commit `4f1ae8a`, seed 20261028, **before any LLM output was produced or inspected.**
**Development data only: never to be used as confirmatory test data.** Set hash (over file hashes): `a52414a40294701c93cb3cc3a8673e4c352890a2f52df04cb2d505f4efb1a474`.

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
| dev-v1-false_belief-g0-stakes1-evidence0 | t0 | K(wen) | useful_current_action | grounded_typed/face_value |
| dev-v1-corroborated-g0-evidence0 | t0 | K(kim) | useful_current_action | grounded_typed/face_value |
| dev-v1-conflict-g1-stakes4 | t0 | K(judy) | useful_current_action | grounded_typed/face_value |
| dev-v1-conflict-g2-stakes1 | t0 | K(heidi) | zero_value_stop | grounded_typed/face_value |
| dev-v1-ambiguity-g1-evidence1 | t0 | K(sara) | zero_value_stop | grounded_typed/face_value |
| dev-v1-false_belief-g0-stakes4-evidence1 | t0 | K(leo) | zero_value_stop | grounded_typed/face_value |
| dev-v1-conflict-g2-stakes4 | t0 | K(wen) | negative | grounded_scalar/face_value |
| dev-v1-directed_perspective-g2-permuted1 | t0 | K(yara) | negative | grounded_scalar/hedged |
| dev-v1-relevance_shift-g3-stakes1 | t0 | K(uma) | carryover | grounded_typed/face_value |

## Files

Data (gitignored, regenerable from code + seed): `data/pilot/dev-v1/`

| file | sha256 |
|---|---|
| interventions.json | `7b112abc5650514c6ee6d2023ce8b9b7e384d01d4db002c057ddafceee6c8916` |
| privileged.jsonl | `2e0593b701248a7383c4e72aa365a61eeb11d9bfb87ceeeb983709ac2b83c7dc` |
| public.jsonl | `99f8ccc606f7213139f08725b495796bc52a40ecca2a6231e8ebe920eae16b0f` |
