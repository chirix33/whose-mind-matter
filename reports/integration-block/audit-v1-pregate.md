# Audit of existing repair Stage 2 traces (no model calls)

Run `repair-stage2-20261029-132459-743ace`. Action patterns first; reasoning classes are a keyword-rubric heuristic, not a causal record.

## First action (t0) by construction | condition | stakes

- 2a|inferred|1: {'ask': 45, 'give': 1, 'move': 2}
- 2a|inferred|4: {'ask': 40, 'give': 3, 'drop': 3, 'move': 2}
- 2a|none|1: {'ask': 44, 'give': 2, 'drop': 2}
- 2a|none|4: {'ask': 44, 'give': 1, 'move': 1, 'drop': 2}
- 2a|reference|1: {'ask': 47, 'give': 1}
- 2a|reference|4: {'ask': 46, 'give': 2}
- 2b|inferred|1: {'ask': 25, 'move': 7, 'drop': 15, 'give': 1}
- 2b|inferred|4: {'ask': 23, 'drop': 14, 'give': 3, 'move': 7, 'wait': 1}
- 2b|none|1: {'ask': 21, 'drop': 21, 'move': 5, 'give': 1}
- 2b|none|4: {'ask': 26, 'drop': 18, 'wait': 4}
- 2b|reference|1: {'drop': 16, 'move': 7, 'ask': 21, 'give': 4}
- 2b|reference|4: {'ask': 22, 'drop': 15, 'wait': 3, 'give': 1, 'move': 7}
- 3a|inferred|1: {'ask': 30, 'give': 16, 'move': 2}
- 3a|inferred|4: {'give': 14, 'ask': 31, 'move': 3}
- 3a|none|1: {'ask': 29, 'give': 13, 'move': 6}
- 3a|none|4: {'ask': 27, 'give': 15, 'move': 6}
- 3a|reference|1: {'ask': 39, 'move': 4, 'give': 5}
- 3a|reference|4: {'move': 3, 'give': 7, 'ask': 38}
- 3b|inferred|1: {'ask': 35, 'move': 6, 'give': 7}
- 3b|inferred|4: {'ask': 37, 'give': 6, 'move': 5}
- 3b|none|1: {'ask': 44, 'give': 2, 'move': 2}
- 3b|none|4: {'ask': 40, 'give': 8}
- 3b|reference|1: {'give': 18, 'ask': 22, 'move': 8}
- 3b|reference|4: {'ask': 30, 'give': 10, 'move': 8}

## Later decisions (t ≥ 1)

Stale-label exposure (decisions with any shown note marked stale / later decisions):
- 2a|inferred|1: 79/81
- 2a|inferred|4: 65/71
- 2a|reference|1: 74/74
- 2a|reference|4: 71/71
- 2b|inferred|1: 61/70
- 2b|inferred|4: 60/76
- 2b|reference|1: 46/58
- 2b|reference|4: 46/71
- 3a|inferred|1: 60/74
- 3a|inferred|4: 69/81
- 3a|reference|1: 82/95
- 3a|reference|4: 108/112
- 3b|inferred|1: 81/91
- 3b|inferred|4: 99/114
- 3b|reference|1: 61/92
- 3b|reference|4: 78/119

Action right after an ask (suffix _wrong = immediate wrong delivery):
- 2a|inferred|1: {'give': 22, 'drop': 17, 'ask': 13, 'move': 6, 'drop_wrong': 2, 'give_wrong': 1}
- 2a|inferred|4: {'ask': 11, 'give': 15, 'drop': 18, 'move': 6, 'give_wrong': 3}
- 2a|none|1: {'give': 24, 'ask': 9, 'move': 6, 'drop': 14}
- 2a|none|4: {'ask': 9, 'drop': 17, 'give': 17, 'move': 9, 'drop_wrong': 1, 'give_wrong': 1}
- 2a|reference|1: {'ask': 12, 'give': 16, 'drop': 18, 'move': 7, 'give_wrong': 4, 'drop_wrong': 2, 'deliver': 1}
- 2a|reference|4: {'drop': 15, 'ask': 15, 'give': 26, 'move': 4, 'wait': 1}
- 2b|inferred|1: {'drop_wrong': 13, 'drop': 7, 'wait': 2, 'move': 4, 'ask': 3, 'give_wrong': 3}
- 2b|inferred|4: {'drop': 5, 'give_wrong': 4, 'wait': 3, 'move': 5, 'ask': 2, 'drop_wrong': 9}
- 2b|none|1: {'drop': 6, 'drop_wrong': 5, 'give_wrong': 7, 'ask': 1, 'wait': 1, 'move': 2}
- 2b|none|4: {'move': 8, 'drop_wrong': 9, 'give_wrong': 6, 'wait': 2, 'drop': 4, 'ask': 3}
- 2b|reference|1: {'move': 5, 'drop': 3, 'drop_wrong': 11, 'give_wrong': 7}
- 2b|reference|4: {'drop': 3, 'drop_wrong': 13, 'move': 3, 'give_wrong': 4, 'ask': 4, 'wait': 3}
- 3a|inferred|1: {'move': 12, 'give': 18, 'ask': 1}
- 3a|inferred|4: {'move': 15, 'give': 18, 'ask': 3}
- 3a|none|1: {'move': 12, 'give': 19}
- 3a|none|4: {'move': 17, 'give': 13, 'ask': 1}
- 3a|reference|1: {'give': 27, 'move': 13, 'ask': 3}
- 3a|reference|4: {'move': 21, 'give': 20, 'deliver': 1}
- 3b|inferred|1: {'give_wrong': 23, 'move': 13, 'ask': 2, 'wait': 2}
- 3b|inferred|4: {'move': 20, 'ask': 4, 'give_wrong': 20}
- 3b|none|1: {'move': 33, 'give_wrong': 11, 'ask': 1}
- 3b|none|4: {'give_wrong': 15, 'move': 26, 'ask': 4}
- 3b|reference|1: {'move': 13, 'give_wrong': 10, 'ask': 1}
- 3b|reference|4: {'give_wrong': 17, 'move': 15, 'ask': 1}

## Reasoning classes (2b/3b reference give/drop decisions)

{"2b": {"other": 82, "forwarding_rule": 4}, "3b": {"other": 22, "forwarding_rule": 34, "uncertain": 2}}

By outcome: {"2b": {"forwarding_rule": {"error": 4}, "belief_as_location": {}, "other": {"success": 31, "error": 51}, "uncertain": {}}, "3b": {"forwarding_rule": {"error": 34}, "belief_as_location": {}, "other": {"error": 22}, "uncertain": {"error": 2}}}

Uncertain cases listed in audit.json: {'2b': 0, '3b': 2}
