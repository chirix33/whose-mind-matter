# Round 2 results: replicated value-of-notes diagnostic (development data; exploratory)

Run `notes-value-20261028-085354-5b41df` (commit `7c22105`, dirty paths 0); policy gpt-6.1-sol effort low, cap 6000, concurrency 4, rules r5, package pilot-v2.1. Wall clock 257 s.
Frozen notes: `round2-notes-freeze.json` (notes file sha256 `89481aa05e6f2ccc…`); every injected payload hash was checked against it.
Episodes: 135 dispatched, 0 blocked; complete replicate layers used: [0, 1, 2] (135 episodes). Counts: 9 states, 1 note per state x condition, 3 policy draws.

## Per state: mean return over draws (success/error/timeout counts; within-state SD)

| state | unit | label | stratum | none | inferred | inferred_bare | reference | privileged |
|---|---|---|---|---|---|---|---|---|
| s1 | K(wen) | useful_current_action | C | +0.850 (3/0/0; sd 0.04) | +0.800 (3/0/0; sd 0.00) | +0.750 (3/0/0; sd 0.00) | +0.750 (3/0/0; sd 0.00) | +0.900 (3/0/0; sd 0.00) |
| s2 | K(judy) | useful_current_action | B | +0.750 (3/0/0; sd 0.00) | +0.750 (3/0/0; sd 0.00) | +0.750 (3/0/0; sd 0.00) | +0.850 (3/0/0; sd 0.00) | +0.950 (3/0/0; sd 0.00) |
| s3 | K(grace) | useful_current_action | A | +0.950 (3/0/0; sd 0.00) | +0.883 (3/0/0; sd 0.05) | +0.850 (3/0/0; sd 0.00) | +0.950 (3/0/0; sd 0.00) | +0.950 (3/0/0; sd 0.00) |
| s4 | K(carol) | zero_value_stop | C | +0.717 (3/0/0; sd 0.02) | +0.817 (3/0/0; sd 0.02) | +0.833 (3/0/0; sd 0.02) | +0.817 (3/0/0; sd 0.02) | +0.950 (3/0/0; sd 0.00) |
| s5 | K(leo) | zero_value_stop | C | +0.900 (3/0/0; sd 0.00) | +0.817 (3/0/0; sd 0.06) | +0.850 (3/0/0; sd 0.07) | +0.817 (3/0/0; sd 0.06) | +0.950 (3/0/0; sd 0.00) |
| s6 | K(mia) | zero_value_stop | B | +0.750 (3/0/0; sd 0.00) | +0.850 (3/0/0; sd 0.00) | +0.750 (3/0/0; sd 0.00) | +0.883 (3/0/0; sd 0.05) | +0.817 (3/0/0; sd 0.05) |
| s7 | K(heidi) | negative | B | +0.850 (3/0/0; sd 0.00) | +0.850 (3/0/0; sd 0.00) | +0.850 (3/0/0; sd 0.00) | +0.850 (3/0/0; sd 0.00) | +0.850 (3/0/0; sd 0.00) |
| s8 | K(yara) | negative | C | +0.950 (3/0/0; sd 0.00) | +0.867 (3/0/0; sd 0.12) | +0.950 (3/0/0; sd 0.00) | +0.950 (3/0/0; sd 0.00) | +0.867 (3/0/0; sd 0.06) |
| s9 | K(dave) | carryover | C | -0.600 (0/3/0; sd 0.00) | -0.167 (1/2/0; sd 0.61) | +0.700 (3/0/0; sd 0.00) | -0.600 (0/3/0; sd 0.00) | -0.600 (0/3/0; sd 0.00) |

## Condition − none, per state averaged over draws

| condition | mean Δ (9 states) | better/worse/tie states | useful+carryover states positive (of 4) | drop-one-state range | reversed by dropping one draw? | bootstrap 90% interval over states | reliable (pre-registered) |
|---|---|---|---|---|---|---|---|
| inferred | +0.039 | 3/4/2 | 1 | -0.010 … +0.054 | yes | [-0.035, +0.131] | no |
| inferred_bare | +0.130 | 2/3/4 | 1 | -0.017 … +0.158 | no | [-0.043, +0.411] | no |
| reference | +0.017 | 3/2/4 | 1 | +0.002 … +0.031 | no | [-0.026, +0.057] | no |
| privileged | +0.057 | 5/1/3 | 2 | +0.035 … +0.075 | no | [+0.007, +0.115] | no |

## By stratum and by original label (mean Δ vs none)

| group | states | inferred | inferred_bare | reference | privileged |
|---|---|---|---|---|---|
| A (reference informative, consistent) | s3 | -0.067 | -0.100 | +0.000 | +0.000 |
| B (reference informative via undisclosed base rates) | s2, s6, s7 | +0.033 | +0.000 | +0.078 | +0.089 |
| C (reference uninformative 0.5/0.5) | s1, s4, s5, s8, s9 | +0.063 | +0.253 | -0.017 | +0.050 |
| label useful_current_action | s1, s2, s3 | -0.039 | -0.067 | +0.000 | +0.083 |
| label carryover | s9 | +0.433 | +1.300 | +0.000 | +0.000 |
| label zero_value_stop | s4, s5, s6 | +0.039 | +0.022 | +0.050 | +0.117 |
| label negative | s7, s8 | -0.042 | +0.000 | +0.000 | -0.042 |

## Contrasts between note conditions (mean over states of per-state difference)

| contrast | mean | better/worse/tie | stratum A | stratum B | stratum C |
|---|---|---|---|---|---|
| inferred − inferred_bare | -0.091 | 3/4/2 | +0.033 | +0.033 | -0.190 |
| inferred_bare − reference | +0.113 | 3/3/3 | -0.100 | -0.078 | +0.270 |
| inferred − reference | +0.022 | 2/4/3 | -0.067 | -0.044 | +0.080 |
| privileged − reference | +0.041 | 4/2/3 | +0.000 | +0.011 | +0.067 |
| privileged − inferred_bare | -0.072 | 6/2/1 | +0.100 | +0.089 | -0.203 |

## Do notes change what the policy does? First action vs the modal `none` first action

| state | modal none first action | inferred | inferred_bare | reference | privileged |
|---|---|---|---|---|---|
| s1 | ask(wen,quinn_loc) | 0/3 differ | 0/3 differ | 0/3 differ | 0/3 differ |
| s2 | move(hall) | 0/3 differ | 0/3 differ | 0/3 differ | 3/3 differ |
| s3 | drop(lab_south) | 2/3 differ | 3/3 differ | 0/3 differ | 0/3 differ |
| s4 | ask(ivan,carol_loc) | 1/3 differ | 2/3 differ | 1/3 differ | 3/3 differ |
| s5 | ask(ravi,leo_loc) | 0/3 differ | 0/3 differ | 0/3 differ | 3/3 differ |
| s6 | move(hall) | 0/3 differ | 0/3 differ | 1/3 differ | 0/3 differ |
| s7 | move(hall) | 0/3 differ | 0/3 differ | 0/3 differ | 0/3 differ |
| s8 | give(tomas) | 1/3 differ | 0/3 differ | 0/3 differ | 2/3 differ |
| s9 | ask(dave,yara_loc) | 0/3 differ | 0/3 differ | 0/3 differ | 0/3 differ |

## Compute and cost

Note generation (inferred notes, 9 API calls, one-time in this experiment; NOT free in deployment): USD 0.0610 (ledger delta).

| condition | episodes | mean decision calls | mean prompt tokens / episode | mean completion tokens / episode | mean reasoning tokens / episode | mean USD / episode (list price) | mean steps | mean wall clock / episode (s) |
|---|---|---|---|---|---|---|---|---|
| none | 27 | 3.07 | 3141 | 89 | 39 | 0.0072 | 3.07 | 6.8 |
| inferred | 27 | 3.41 | 4046 | 112 | 57 | 0.0092 | 3.41 | 7.9 |
| inferred_bare | 27 | 3.81 | 4215 | 144 | 82 | 0.0099 | 3.81 | 9.4 |
| reference | 27 | 2.74 | 3007 | 125 | 80 | 0.0073 | 2.74 | 7.5 |
| privileged | 27 | 1.93 | 2024 | 87 | 54 | 0.0049 | 1.93 | 5.5 |

Failed attempts: 0; fallbacks to wait(): 0. Episodes ran with concurrency 4; per-episode wall clock includes provider queueing and is not a compute measure.

## Note payloads (top value, p; status)

| state | unit | truth | inferred | inferred_bare | reference | privileged |
|---|---|---|---|---|---|---|
| s1 | K(wen) | desk_9 | desk_3 0.40, desk_9 0.40, unknown 0.20 [uncertain] | desk_3 0.40, desk_9 0.40, unknown 0.20 [uncertain] | desk_3 0.50, desk_9 0.50 [uncertain] | desk_9 1.00 [grounded] |
| s2 | K(judy) | office_b | office_a 0.50, office_b 0.50, unknown 0.00 [uncertain] | office_a 0.50, office_b 0.50, unknown 0.00 [uncertain] | office_b 0.95, office_a 0.05 [grounded] | office_b 1.00 [grounded] |
| s3 | K(grace) | lab_south | lab_south 0.85, lab_north 0.10, unknown 0.05 [grounded] | lab_south 0.85, lab_north 0.10, unknown 0.05 [grounded] | lab_south 1.00 [grounded] | lab_south 1.00 [grounded] |
| s4 | K(carol) | office_a | office_a 0.50, office_b 0.50, unknown 0.00 [uncertain] | office_a 0.50, office_b 0.50, unknown 0.00 [uncertain] | office_a 0.50, office_b 0.50 [uncertain] | office_a 1.00 [grounded] |
| s5 | K(leo) | room_12 | room_12 0.50, room_7 0.50, unknown 0.00 [uncertain] | room_12 0.50, room_7 0.50, unknown 0.00 [uncertain] | room_12 0.50, room_7 0.50 [uncertain] | room_12 1.00 [grounded] |
| s6 | K(mia) | room_7 | room_7 0.50, room_12 0.35, unknown 0.15 [uncertain] | room_7 0.50, room_12 0.35, unknown 0.15 [uncertain] | room_7 0.97, room_12 0.03 [grounded] | room_7 1.00 [grounded] |
| s7 | K(heidi) | desk_3 | desk_3 0.85, desk_9 0.10, unknown 0.05 [grounded] | desk_3 0.85, desk_9 0.10, unknown 0.05 [grounded] | desk_3 0.87, desk_9 0.13 [grounded] | desk_3 1.00 [grounded] |
| s8 | K(yara) | desk_9 | desk_3 0.50, desk_9 0.50, unknown 0.00 [uncertain] | desk_3 0.50, desk_9 0.50, unknown 0.00 [uncertain] | desk_3 0.50, desk_9 0.50 [uncertain] | desk_9 1.00 [grounded] |
| s9 | K(dave) | lab_north | lab_north 0.40, lab_south 0.40, unknown 0.20 [uncertain] | lab_north 0.40, lab_south 0.40, unknown 0.20 [uncertain] | lab_north 0.50, lab_south 0.50 [uncertain] | lab_north 1.00 [grounded] |
