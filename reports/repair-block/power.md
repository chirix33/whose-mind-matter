# Stage 2 precision simulation (planning only)

Rule (Entry 1a RC5): smallest feasible K with P(helps | Δ=0.10) ≥ 0.8 and P(no practical value | Δ=0) ≥ 0.8 under variance B; otherwise the largest feasible K. Criterion met for K = none; **chosen K = 24** (288 base scenarios).

| K | var | Δ | P(helps) | P(no practical value) | P(unresolved) | CI half-width |
|---|---|---|---|---|---|---|
| 3 | A | 0.0 | 0.01 | 0.20 | 0.79 | 0.111 |
| 3 | A | 0.05 | 0.07 | 0.04 | 0.88 | 0.107 |
| 3 | A | 0.1 | 0.24 | 0.01 | 0.75 | 0.104 |
| 3 | B | 0.0 | 0.01 | 0.15 | 0.84 | 0.164 |
| 3 | B | 0.05 | 0.04 | 0.07 | 0.90 | 0.164 |
| 3 | B | 0.1 | 0.12 | 0.02 | 0.87 | 0.154 |
| 4 | A | 0.0 | 0.02 | 0.20 | 0.78 | 0.102 |
| 4 | A | 0.05 | 0.08 | 0.05 | 0.86 | 0.101 |
| 4 | A | 0.1 | 0.29 | 0.00 | 0.70 | 0.095 |
| 4 | B | 0.0 | 0.02 | 0.11 | 0.88 | 0.154 |
| 4 | B | 0.05 | 0.04 | 0.05 | 0.90 | 0.152 |
| 4 | B | 0.1 | 0.14 | 0.01 | 0.84 | 0.146 |
| 5 | A | 0.0 | 0.01 | 0.21 | 0.78 | 0.094 |
| 5 | A | 0.05 | 0.09 | 0.05 | 0.86 | 0.091 |
| 5 | A | 0.1 | 0.36 | 0.01 | 0.63 | 0.088 |
| 5 | B | 0.0 | 0.01 | 0.12 | 0.87 | 0.142 |
| 5 | B | 0.05 | 0.02 | 0.05 | 0.94 | 0.141 |
| 5 | B | 0.1 | 0.15 | 0.01 | 0.84 | 0.136 |
| 6 | A | 0.0 | 0.01 | 0.20 | 0.78 | 0.089 |
| 6 | A | 0.05 | 0.12 | 0.05 | 0.83 | 0.086 |
| 6 | A | 0.1 | 0.42 | 0.00 | 0.58 | 0.083 |
| 6 | B | 0.0 | 0.02 | 0.12 | 0.86 | 0.136 |
| 6 | B | 0.05 | 0.04 | 0.04 | 0.93 | 0.131 |
| 6 | B | 0.1 | 0.20 | 0.01 | 0.80 | 0.127 |
| 8 | A | 0.0 | 0.01 | 0.27 | 0.73 | 0.079 |
| 8 | A | 0.05 | 0.18 | 0.04 | 0.77 | 0.077 |
| 8 | A | 0.1 | 0.56 | 0.00 | 0.43 | 0.073 |
| 8 | B | 0.0 | 0.02 | 0.15 | 0.83 | 0.119 |
| 8 | B | 0.05 | 0.06 | 0.04 | 0.90 | 0.117 |
| 8 | B | 0.1 | 0.28 | 0.00 | 0.72 | 0.112 |
| 12 | A | 0.0 | 0.01 | 0.32 | 0.66 | 0.066 |
| 12 | A | 0.05 | 0.21 | 0.04 | 0.76 | 0.065 |
| 12 | A | 0.1 | 0.77 | 0.00 | 0.23 | 0.062 |
| 12 | B | 0.0 | 0.02 | 0.16 | 0.82 | 0.101 |
| 12 | B | 0.05 | 0.09 | 0.04 | 0.87 | 0.098 |
| 12 | B | 0.1 | 0.40 | 0.00 | 0.60 | 0.096 |
| 16 | A | 0.0 | 0.01 | 0.41 | 0.58 | 0.058 |
| 16 | A | 0.05 | 0.30 | 0.04 | 0.66 | 0.057 |
| 16 | A | 0.1 | 0.89 | 0.00 | 0.12 | 0.055 |
| 16 | B | 0.0 | 0.00 | 0.20 | 0.80 | 0.087 |
| 16 | B | 0.05 | 0.13 | 0.02 | 0.84 | 0.086 |
| 16 | B | 0.1 | 0.49 | 0.00 | 0.51 | 0.084 |
| 20 | A | 0.0 | 0.01 | 0.47 | 0.53 | 0.052 |
| 20 | A | 0.05 | 0.32 | 0.03 | 0.65 | 0.051 |
| 20 | A | 0.1 | 0.94 | 0.00 | 0.06 | 0.049 |
| 20 | B | 0.0 | 0.01 | 0.24 | 0.75 | 0.079 |
| 20 | B | 0.05 | 0.16 | 0.03 | 0.81 | 0.077 |
| 20 | B | 0.1 | 0.59 | 0.00 | 0.41 | 0.075 |
| 24 | A | 0.0 | 0.01 | 0.54 | 0.45 | 0.048 |
| 24 | A | 0.05 | 0.46 | 0.03 | 0.51 | 0.047 |
| 24 | A | 0.1 | 0.96 | 0.00 | 0.04 | 0.045 |
| 24 | B | 0.0 | 0.02 | 0.27 | 0.71 | 0.072 |
| 24 | B | 0.05 | 0.21 | 0.03 | 0.76 | 0.071 |
| 24 | B | 0.1 | 0.68 | 0.00 | 0.32 | 0.069 |

## Limitations at the chosen K (S4; stated extrapolation from the simulated half-widths)

Method: normal approximation, SE = simulated 95% half-width / 1.96, scaled by sqrt(24/K); "helps" needs Holm p < 0.025 (z = 2.24) at power 0.8 (z = 0.84).

- Variance A: minimum detectable effect at K = 24 ≈ 0.07; P(helps | Δ = 0.10) ≥ 0.8 needs K ≈ 12; P(no practical value | Δ = 0) ≥ 0.8 needs K ≈ 46 (≈ 6.1 h at 8 min per seed, beyond the 4 h limit).
- Variance B: minimum detectable effect at K = 24 ≈ 0.109; P(helps | Δ = 0.10) ≥ 0.8 needs K ≈ 28; P(no practical value | Δ = 0) ≥ 0.8 needs K ≈ 102 (≈ 13.6 h at 8 min per seed, beyond the 4 h limit).

- **Under a true null, the expected outcome at K = 24 is "unresolved"** (P = 0.71 under B, 0.45 under A); "no practical value" is reached only with P = 0.27 (B) / 0.54 (A).
- Effects below the minimum detectable effect will most likely read "unresolved". The planning model assumes independent conditions within a scenario (conservative) and uses Round B returns with the old note format as exploratory input.
