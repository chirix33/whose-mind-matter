# Fixed unit-inference contexts `unit-contexts-v1`

Selection rule: `scripts/freeze_unit_contexts.py` docstring. Renderer r3; packages ['pilot-v1', 'pilot-v2']. Frozen before any pilot-v2 or API output.

- Contexts: 24; by family {'false_belief': 4, 'conflict': 3, 'corroborated': 2, 'ambiguity': 2, 'distractors': 3, 'directed_perspective': 2, 'relevance_shift': 4, 'nested_reliability': 4}
- By unit type {'K1': 14, 'R2': 2, 'R1': 2, 'K2': 6}; history prefix k: {0: 16, 1: 8}
- Truth 'unknown': 6; default-violating content: 4
- With a stored original pilot-v1 (r2) output: 16
- sha256 public `1197f7303cc202607c711662c681113c5bf05b27e489071f8d7714b724cffe4d`, privileged `7b4e38bd218a81b1420b40f94082b9f823273fdd18f5bb6a41ad57fc14ca1521`

| id | instance | k | unit | source |
|---|---|---|---|---|
| uc01 | dev-v2-false_belief-g0-stakes4-evidence0 | 0 | K(wen) | prespecified_intervention |
| uc02 | dev-v2-conflict-g1-stakes4 | 0 | K(judy) | prespecified_intervention |
| uc03 | dev-v2-corroborated-g3-evidence0 | 0 | K(grace) | prespecified_intervention |
| uc04 | dev-v2-ambiguity-g0-evidence1 | 0 | K(carol) | prespecified_intervention |
| uc05 | dev-v2-distractors-g3-permuted1 | 0 | K(leo) | prespecified_intervention |
| uc06 | dev-v2-conflict-g3-stakes1 | 0 | K(mia) | prespecified_intervention |
| uc07 | dev-v2-conflict-g2-stakes1 | 0 | K(heidi) | prespecified_intervention |
| uc08 | dev-v2-directed_perspective-g2-permuted1 | 0 | K(yara) | prespecified_intervention |
| uc09 | dev-v2-relevance_shift-g1-stakes1 | 0 | K(dave) | prespecified_intervention |
| uc10 | dev-v2-nested_reliability-g1-permuted0 | 1 | R(uma->vik) | pass:R2 |
| uc11 | dev-v2-nested_reliability-g2-permuted0 | 0 | R(zane->ravi) | pass:R2 |
| uc12 | dev-v2-nested_reliability-g0-permuted0 | 1 | R(nadia) | pass:R1 |
| uc13 | dev-v2-nested_reliability-g3-permuted1 | 0 | R(grace) | pass:R1 |
| uc14 | dev-v2-relevance_shift-g0-stakes1 | 0 | K(wen->leo) | pass:K2 |
| uc15 | dev-v2-directed_perspective-g1-permuted0 | 0 | K(vik->ivan) | pass:K2 |
| uc16 | dev-v2-false_belief-g1-stakes1-evidence1 | 0 | K(alice->wen) | pass:K2 |
| uc17 | dev-v2-false_belief-g2-stakes1-evidence1 | 1 | K(tomas->vik) | pass:K2 |
| uc18 | dev-v2-relevance_shift-g3-stakes1 | 1 | K(quinn->uma) | pass:K2 |
| uc19 | dev-v2-false_belief-g3-stakes4-evidence0 | 1 | K(omar->leo) | pass:K2 |
| uc20 | dev-v2-relevance_shift-g2-stakes1 | 1 | K(ivan) | pass:default_violating |
| uc21 | dev-v2-distractors-g2-permuted0 | 1 | K(frank) | pass:k1 |
| uc22 | dev-v2-corroborated-g2-evidence0 | 1 | K(alice) | pass:k1 |
| uc23 | dev-v2-ambiguity-g3-evidence1 | 0 | K(alice) | pass:any |
| uc24 | dev-v2-distractors-g1-permuted0 | 0 | K(vik) | pass:any |
