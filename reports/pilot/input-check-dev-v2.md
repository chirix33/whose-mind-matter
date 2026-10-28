# Pilot input check: `dev-v2`

Fully rendered t=0 policy requests (task card with rewards and stakes, layout, history ledger, physical summary, legal actions) compared across single-knob variant pairs. No LLM call is made. No response cache is used.

MUST-differ violations: **0**.

| group | knob | variant a | variant b | identical history view | identical rendered policy request | verdict |
|---|---|---|---|---|---|---|
| dev-v2-ambiguity-g0 | evidence | evidence0 | evidence1 | False | False | ok |
| dev-v2-ambiguity-g1 | evidence | evidence0 | evidence1 | False | False | ok |
| dev-v2-ambiguity-g2 | evidence | evidence0 | evidence1 | False | False | ok |
| dev-v2-ambiguity-g3 | evidence | evidence0 | evidence1 | False | False | ok |
| dev-v2-conflict-g0 | stakes | stakes1 | stakes4 | True | False | ok |
| dev-v2-conflict-g1 | stakes | stakes1 | stakes4 | True | False | ok |
| dev-v2-conflict-g2 | stakes | stakes1 | stakes4 | True | False | ok |
| dev-v2-conflict-g3 | stakes | stakes1 | stakes4 | True | False | ok |
| dev-v2-corroborated-g0 | evidence | evidence0 | evidence1 | False | False | ok |
| dev-v2-corroborated-g1 | evidence | evidence0 | evidence1 | False | False | ok |
| dev-v2-corroborated-g2 | evidence | evidence0 | evidence1 | False | False | ok |
| dev-v2-corroborated-g3 | evidence | evidence0 | evidence1 | False | False | ok |
| dev-v2-directed_perspective-g0 | permuted | permuted0 | permuted1 | False | False | by design |
| dev-v2-directed_perspective-g1 | permuted | permuted0 | permuted1 | False | False | by design |
| dev-v2-directed_perspective-g2 | permuted | permuted0 | permuted1 | False | False | by design |
| dev-v2-directed_perspective-g3 | permuted | permuted0 | permuted1 | False | False | by design |
| dev-v2-distractors-g0 | permuted | permuted0 | permuted1 | True | True | by design |
| dev-v2-distractors-g1 | permuted | permuted0 | permuted1 | False | False | by design |
| dev-v2-distractors-g2 | permuted | permuted0 | permuted1 | True | True | by design |
| dev-v2-distractors-g3 | permuted | permuted0 | permuted1 | False | False | by design |
| dev-v2-false_belief-g0 | evidence | stakes1-evidence0 | stakes1-evidence1 | False | False | ok |
| dev-v2-false_belief-g0 | stakes | stakes1-evidence0 | stakes4-evidence0 | True | False | ok |
| dev-v2-false_belief-g0 | stakes | stakes1-evidence1 | stakes4-evidence1 | True | False | ok |
| dev-v2-false_belief-g0 | evidence | stakes4-evidence0 | stakes4-evidence1 | False | False | ok |
| dev-v2-false_belief-g1 | evidence | stakes1-evidence0 | stakes1-evidence1 | False | False | ok |
| dev-v2-false_belief-g1 | stakes | stakes1-evidence0 | stakes4-evidence0 | True | False | ok |
| dev-v2-false_belief-g1 | stakes | stakes1-evidence1 | stakes4-evidence1 | True | False | ok |
| dev-v2-false_belief-g1 | evidence | stakes4-evidence0 | stakes4-evidence1 | False | False | ok |
| dev-v2-false_belief-g2 | evidence | stakes1-evidence0 | stakes1-evidence1 | False | False | ok |
| dev-v2-false_belief-g2 | stakes | stakes1-evidence0 | stakes4-evidence0 | True | False | ok |
| dev-v2-false_belief-g2 | stakes | stakes1-evidence1 | stakes4-evidence1 | True | False | ok |
| dev-v2-false_belief-g2 | evidence | stakes4-evidence0 | stakes4-evidence1 | False | False | ok |
| dev-v2-false_belief-g3 | evidence | stakes1-evidence0 | stakes1-evidence1 | False | False | ok |
| dev-v2-false_belief-g3 | stakes | stakes1-evidence0 | stakes4-evidence0 | True | False | ok |
| dev-v2-false_belief-g3 | stakes | stakes1-evidence1 | stakes4-evidence1 | True | False | ok |
| dev-v2-false_belief-g3 | evidence | stakes4-evidence0 | stakes4-evidence1 | False | False | ok |
| dev-v2-nested_reliability-g0 | permuted | permuted0 | permuted1 | False | False | by design |
| dev-v2-nested_reliability-g1 | permuted | permuted0 | permuted1 | False | False | by design |
| dev-v2-nested_reliability-g2 | permuted | permuted0 | permuted1 | False | False | by design |
| dev-v2-nested_reliability-g3 | permuted | permuted0 | permuted1 | False | False | by design |
| dev-v2-relevance_shift-g0 | stakes | stakes1 | stakes4 | True | False | ok |
| dev-v2-relevance_shift-g1 | stakes | stakes1 | stakes4 | True | False | ok |
| dev-v2-relevance_shift-g2 | stakes | stakes1 | stakes4 | True | False | ok |
| dev-v2-relevance_shift-g3 | stakes | stakes1 | stakes4 | True | False | ok |
| dev-v2-stop-g0 | bystander | bystander0 | bystander1 | False | False | ok |
| dev-v2-stop-g1 | bystander | bystander0 | bystander1 | False | False | ok |
| dev-v2-stop-g2 | bystander | bystander0 | bystander1 | False | False | ok |
| dev-v2-stop-g3 | bystander | bystander0 | bystander1 | False | False | ok |
