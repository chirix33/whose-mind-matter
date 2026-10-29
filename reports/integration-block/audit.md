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

Stale exposure split (after an ask / after a sighting or mention only):
- 2a|inferred|1: {'after_ask': '77/77', 'sighting_only': '2/4'}
- 2a|inferred|4: {'after_ask': '65/65', 'sighting_only': '0/6'}
- 2a|reference|1: {'after_ask': '74/74', 'sighting_only': '0/0'}
- 2a|reference|4: {'after_ask': '71/71', 'sighting_only': '0/0'}
- 2b|inferred|1: {'after_ask': '54/54', 'sighting_only': '7/16'}
- 2b|inferred|4: {'after_ask': '54/57', 'sighting_only': '6/19'}
- 2b|reference|1: {'after_ask': '40/40', 'sighting_only': '6/18'}
- 2b|reference|4: {'after_ask': '38/38', 'sighting_only': '8/33'}
- 3a|inferred|1: {'after_ask': '60/60', 'sighting_only': '0/14'}
- 3a|inferred|4: {'after_ask': '67/67', 'sighting_only': '2/14'}
- 3a|reference|1: {'after_ask': '78/78', 'sighting_only': '4/17'}
- 3a|reference|4: {'after_ask': '105/105', 'sighting_only': '3/7'}
- 3b|inferred|1: {'after_ask': '75/76', 'sighting_only': '6/15'}
- 3b|inferred|4: {'after_ask': '95/95', 'sighting_only': '4/19'}
- 3b|reference|1: {'after_ask': '56/56', 'sighting_only': '5/36'}
- 3b|reference|4: {'after_ask': '68/68', 'sighting_only': '10/51'}

Asks that occurred (reference episodes): true content unchanged / posterior unchanged:
- 2a|asked-H|K(bob): {'asks': 18, 'true_content_unchanged': 18, 'posterior_unchanged': 10}
- 2a|asked-H|K(carol): {'asks': 10, 'true_content_unchanged': 10, 'posterior_unchanged': 7}
- 2a|asked-H|K(frank): {'asks': 7, 'true_content_unchanged': 7, 'posterior_unchanged': 0}
- 2a|asked-H|K(grace): {'asks': 11, 'true_content_unchanged': 11, 'posterior_unchanged': 11}
- 2a|asked-H|K(judy): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 2a|asked-H|K(leo): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 4}
- 2a|asked-H|K(mia): {'asks': 26, 'true_content_unchanged': 26, 'posterior_unchanged': 19}
- 2a|asked-H|K(nadia): {'asks': 20, 'true_content_unchanged': 20, 'posterior_unchanged': 12}
- 2a|asked-H|K(omar): {'asks': 5, 'true_content_unchanged': 5, 'posterior_unchanged': 5}
- 2a|asked-H|K(pia): {'asks': 8, 'true_content_unchanged': 8, 'posterior_unchanged': 0}
- 2a|asked-H|K(quinn): {'asks': 19, 'true_content_unchanged': 19, 'posterior_unchanged': 4}
- 2a|asked-H|K(ravi): {'asks': 6, 'true_content_unchanged': 6, 'posterior_unchanged': 3}
- 2a|asked-H|K(sara): {'asks': 9, 'true_content_unchanged': 9, 'posterior_unchanged': 5}
- 2a|asked-H|K(tomas): {'asks': 14, 'true_content_unchanged': 14, 'posterior_unchanged': 6}
- 2a|asked-H|K(uma): {'asks': 8, 'true_content_unchanged': 8, 'posterior_unchanged': 0}
- 2a|asked-H|K(vik): {'asks': 8, 'true_content_unchanged': 8, 'posterior_unchanged': 8}
- 2a|asked-H|K(wen): {'asks': 11, 'true_content_unchanged': 11, 'posterior_unchanged': 7}
- 2a|asked-H|K(yara): {'asks': 6, 'true_content_unchanged': 6, 'posterior_unchanged': 3}
- 2a|asked-N|K(bob): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 2a|asked-N|K(carol): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 2a|asked-N|K(frank): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 2a|asked-N|K(grace): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 2a|asked-N|K(judy): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 2a|asked-N|K(mia): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 4}
- 2a|asked-N|K(nadia): {'asks': 5, 'true_content_unchanged': 5, 'posterior_unchanged': 5}
- 2a|asked-N|K(omar): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 2a|asked-N|K(pia): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 2a|asked-N|K(quinn): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 4}
- 2a|asked-N|K(ravi): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 2a|asked-N|K(sara): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 2a|asked-N|K(tomas): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 2a|asked-N|K(uma): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 2a|asked-N|K(vik): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 4}
- 2a|asked-N|K(wen): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 2a|asked-N|K(yara): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 2a|asked-R|K(tomas): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 2a|asked-R|K(wen): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 2b|asked-N|K(alice): {'asks': 7, 'true_content_unchanged': 7, 'posterior_unchanged': 7}
- 2b|asked-N|K(dave): {'asks': 5, 'true_content_unchanged': 5, 'posterior_unchanged': 5}
- 2b|asked-N|K(erin): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 2b|asked-N|K(frank): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 2b|asked-N|K(ivan): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 2b|asked-N|K(kim): {'asks': 11, 'true_content_unchanged': 11, 'posterior_unchanged': 11}
- 2b|asked-N|K(leo): {'asks': 8, 'true_content_unchanged': 8, 'posterior_unchanged': 8}
- 2b|asked-N|K(omar): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 4}
- 2b|asked-N|K(pia): {'asks': 7, 'true_content_unchanged': 7, 'posterior_unchanged': 7}
- 2b|asked-N|K(vik): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 2b|asked-N|K(wen): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 2b|asked-N|K(yara): {'asks': 7, 'true_content_unchanged': 7, 'posterior_unchanged': 7}
- 3a|asked-F|K(alice->bob): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(alice->carol): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 0}
- 3a|asked-F|K(erin->judy): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(grace->alice): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(grace->kim): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(ivan->bob): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(leo->frank): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 0}
- 3a|asked-F|K(leo->grace): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(leo->heidi): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 1}
- 3a|asked-F|K(leo->nadia): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(leo->zane): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 0}
- 3a|asked-F|K(omar->erin): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 0}
- 3a|asked-F|K(pia->alice): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(quinn->mia): {'asks': 5, 'true_content_unchanged': 5, 'posterior_unchanged': 1}
- 3a|asked-F|K(ravi->nadia): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 0}
- 3a|asked-F|K(ravi->omar): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(ravi->pia): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(ravi->uma): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 0}
- 3a|asked-F|K(sara->uma): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(tomas->dave): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 0}
- 3a|asked-F|K(uma->omar): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 0}
- 3a|asked-F|K(yara->ravi): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 0}
- 3a|asked-F|K(zane->alice): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 0}
- 3a|asked-F|K(zane->yara): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 1}
- 3a|asked-R|K(pia->alice): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 3b|asked-F|K(alice->frank): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(alice->vik): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 3b|asked-F|K(carol->vik): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(frank->sara): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 3b|asked-F|K(heidi->quinn): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 3b|asked-F|K(ivan->kim): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 3b|asked-F|K(judy->pia): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(kim->mia): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 3b|asked-F|K(leo->carol): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(mia->sara): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(mia->vik): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 3b|asked-F|K(mia->yara): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(omar->grace): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(pia->omar): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(sara->mia): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(sara->tomas): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(tomas->frank): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 3b|asked-F|K(tomas->heidi): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(uma->alice): {'asks': 2, 'true_content_unchanged': 2, 'posterior_unchanged': 2}
- 3b|asked-F|K(uma->judy): {'asks': 3, 'true_content_unchanged': 3, 'posterior_unchanged': 3}
- 3b|asked-F|K(uma->ravi): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 3b|asked-F|K(yara->quinn): {'asks': 4, 'true_content_unchanged': 4, 'posterior_unchanged': 4}
- 3b|asked-F|K(yara->ravi): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 3b|asked-P|K(judy->pia): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}
- 3b|asked-P|K(uma->judy): {'asks': 1, 'true_content_unchanged': 1, 'posterior_unchanged': 1}

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

{"2b": {"other": 82, "forwarding_rule": 4}, "3b": {"uses_own_belief": 1, "other": 21, "forwarding_rule": 28, "uncertain": 8}}

By outcome: {"2b": {"uses_own_belief": {}, "forwarding_rule": {"error": 4}, "belief_as_location": {}, "other": {"success": 31, "error": 51}, "uncertain": {}}, "3b": {"uses_own_belief": {"error": 1}, "forwarding_rule": {"error": 28}, "belief_as_location": {}, "other": {"error": 21}, "uncertain": {"error": 8}}}

Uncertain cases listed in audit.json: {'2b': 0, '3b': 8}
