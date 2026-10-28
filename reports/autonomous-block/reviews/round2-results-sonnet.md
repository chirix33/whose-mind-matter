# Round 2 results gate: Sonnet 5.5 independent numbers check

**Verdict:** CONSISTENT. Commit checked: `046907d`.

The reviewer recomputed everything with its own code from the raw episodes and the frozen payloads.

- **Integrity:**
  - 135 episodes in 45 state × condition cells of 3 draws each; dispatch indices are unique.
  - 124 successes, 11 errors, 0 timeouts; 0 failed attempts and 0 fallbacks.
  - All 108 injected note hashes equal the freeze proof, and the payload hashes recompute.
  - The states-block sha256 is `89481aa0…` (proof = manifest).
  - The run is at commit `7c22105`, not dirty.
- **Per-state means and success/error/timeout counts:** all match. The only difference is that the report uses the population SD and the reviewer the sample SD, which is cosmetic.
- **Per-condition Δ vs. none:** better/worse/tie counts, drop-one-state ranges, useful+carryover counts and drop-one-draw reversal all match.
  - inferred +0.039 is reversed by dropping one draw (min −0.009).
  - inferred_bare +0.130, reference +0.017 and privileged +0.057 are not.
- **Strata, label rows, the 5 contrasts and all 36 first-action cells:** match.
- **Costs:**
  - Per-condition tokens and USD match.
  - Policy spend from tokens is USD 1.0379. Notes cost 0.0610 (ledger delta).
  - 1.8570 + 0.0610 + 1.0379 = 2.9559, which equals the ledger (753 calls, no reservations or unresolved charges).
- **Summary claims:** all reproduced.
  - none succeeds in 24 of 27 draws.
  - Steps: privileged 1.93 vs. none 3.07.
  - inferred_bare gain: s9 +1.300; −0.0167 without s9.
  - s9 successes: none, reference and privileged 0/3; inferred 1/3; inferred_bare 3/3 (each checks both labs).
  - inferred prompt tokens +28.8%.
