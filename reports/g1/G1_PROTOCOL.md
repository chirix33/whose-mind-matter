# G1 protocol: symbolic twin of "cheap provenance, costly content" (D-023)

Frozen before any measurement; its sha256 is pinned in `g1-freeze.json` with the code.
- Runner: `scripts/g1_symbolic_twin.py` (CPU only, stdlib).
- One evaluation pass. No model calls, text, spending, or progression to G2.

**What a pass would mean:** a promising symbolic setting. It would not establish a method, novelty, a paper, or that real text extraction is expensive (D-023 item 6).

## 1. Generator (fixed; not adjusted after measuring)

- **Offices:** 3. Layout: lobby–hall–offices. Horizon 8 steps per task; step cost −0.05; success +1; wrong handoff −0.5·stakes.
- **Cast:**
  - Two couriers, c1 and c2. They are silent (no location messages of their own) and present in the lobby at every task.
  - *Others*: the people who send messages and can be recipients.
- **Each other person p:**
  - publicly announced office a_p, uniform over the 3 offices;
  - public change rate q_p, uniform over {0.1, 0.3, 0.5};
  - L_p private location messages, L_p uniform over {0, 1, 2, 3}.
- **Message j of p:**
  - goes to one listener, uniform over everyone except p (couriers included);
  - content Y_j is the office p says it is going to: Y_j = Y_{j−1} with probability 1 − q_p, otherwise uniform over the two other offices (Y_0 = a_p);
  - p then goes there, so p's location = Y_{L_p}.
- **Beliefs.** A person's belief about p's location = the content of the latest p-message they heard, else a_p.
- **Couriers.** They forward to their own belief about the recipient's location.
- **The robot sees** (provenance; cost 0):
  - every message's speaker, listener and order within the speaker's sequence;
  - every a_p and q_p.
- **Reading a message's content** costs **1 read**. A read is cached for the rest of the day.
- **Day.** K tasks, with recipients drawn **with replacement** from the others, so task reuse happens when a recipient repeats. Tasks are physically independent: the robot starts each one in the lobby.
- **Each day is evaluated at stakes ×1 and ×4** (paired, same world).

| condition | others | K tasks | intent |
|---|---|---|---|
| **sparse** (gated) | 8 | 3 | most messages come from people who never receive a package |
| **dense** (relevance-density control; reported, not gated) | 3 | 4 | every sender is a recipient; repeats are certain |

**Seeds:**
- day d of condition X uses `random.Random("G1:X:<20261600+d>")`, d = 0…1999, for both conditions (2,000 days each);
- perspective set (§4): 500 chains, `random.Random("G1:persp:<20262600+i>")`;
- bootstrap seed 0, with 2,000 resamples over days.

## 2. Task decision interface (shared by every selector)

After the selector's reads for a task, the robot has the exact posterior over the recipient R's message contents, given the public model and every read content of R's sequence. It then picks the option with the highest expected value (ties go to search):
- `give(c)`, valued `J = −0.05 + p_c − (1−p_c)·0.5·s`, where p_c = P(c's belief = R's location);
- search in person (declared order: descending posterior probability, then office order), valued exactly by `search_value` from the lobby with 8 steps.

**Realized return** comes from the true world: give succeeds iff c's true belief equals R's true location. Search returns `1 − 0.05·(steps + 1)`, where steps is the walk to R's true office in the chosen order.

## 3. Read selectors (all use provenance, public parameters and cached contents only)

| id | rule |
|---|---|
| `none` | never read (provenance only) |
| `dense` | read every message of the day once, at the start (full information) |
| `structural` | read every message whose speaker or listener is R or a courier |
| `latest` | read R's latest message (if any). Perspective-blind |
| `action_prov` | If L_R = 0, or some courier heard R's latest message: read nothing (provenance establishes alignment, without revealing the value). Otherwise take c* = the courier whose latest-heard R-message is latest (ties: c1); read R's latest message, plus c*'s source message if it is a message rather than the announcement |
| `risk(θ)` | n = number of R-messages after the latest one any courier heard; risk = (1 − (1 − q_R)^n)·(1 + 0.5·s). Read R's latest message iff risk > θ; θ ∈ {0.05, 0.1, 0.2, 0.4, 0.8, 1.6} |
| `entropy(B)` | B times: read the unread R-message with maximal posterior content entropy (ties: later); B ∈ {1, 2} |
| `random(B)` | B uniformly random unread R-messages (seeded per day and task); B ∈ {1, 2} |
| **`dv(λ)`** | Repeat: over every unread R-message and every pair of them, compute exact net value VOI(S) − λ·\|S\|. Stop if the best is ≤ 0; otherwise read the best set (ties: fewer reads, then earlier messages). λ ∈ {0.005, 0.01, 0.02, **0.04**, 0.08, 0.16}; operating point 0.04 |

- **Accounting.** Reads per day = distinct messages read. **U = reads per day ÷ messages per day.**
- Messages outside R's sequence have zero value under the public model. `dv`, `latest`, `action_prov`, `risk`, `entropy` and `random` never read them; `structural` and `dense` do.

## 4. Perspective-paired set (amendment 2)

- 500 chains, each with one recipient R using the sparse parameters but L_R uniform over {1, 2, 3}, and the two couriers.
- Each chain gets **4 audience variants**: listeners are resampled while R's contents (the physical history) stay fixed.
- Evaluated with `dv(0.04)`, `latest` and `action_prov` at both stakes. One task per variant, no other people.

## 5. Gates (sparse condition; returns are per task, averaged over stakes ×1 and ×4)

**G1a: sparsity.**
- **Pass:** U_dv(0.04) ≤ 0.35 **and** return_dv(0.04) ≥ return_dense − 0.02.
- **Stop:** U > 0.60.
- **Otherwise inconclusive.** U in (0.35, 0.60] is not a pass.

**G1b: no cheap rule matches decision value** (amendments 1 and 4).
- Cheap points: every setting of `none`, `structural`, `latest`, `action_prov`, `risk(θ)`, `entropy(B)` and `random(B)`. `dense` is the full-information reference, not a cheap rule.
- **Stop:** some cheap point b has reads_b ≤ 1.1·reads_dv **and** return_b ≥ return_dv − 0.02. A simple rule then performs equally well.
- **Pass:** no point matches; **and** every cheap point with reads_b ≤ 1.1·reads_dv has a paired 95% CI lower bound on (return_dv − return_b) **> 0.02**; **and** every cheap point with more reads has return_b ≤ return_dv + 0.02.
- **Otherwise inconclusive.**
- Ties are part of the matching rule: within 0.02 return at ≤ 1.1× reads counts as a match.

**G1c: costly content matters.**
- **Comparable initial task states:** the first task of each distinct recipient within a day (no cached content for that recipient), counted once per stakes. Repeat-recipient tasks are reuse, not STOP, and are reported separately.
- **Pass:** at least 30% of comparable initial task states have exact V_full − V_none ≥ 0.10. Otherwise stop.

**G1d: allocation exists.**
- **Pass:**
  - the STOP share of `dv(0.04)` (no read bought at the task's first decision) is in [0.20, 0.90], over the comparable initial task states defined in G1c, so cached repeats and later states cannot inflate it;
  - **and** at least 5% of those tasks change between READ and STOP across ×1 and ×4.
- Otherwise stop.

**G1e: perspectives matter** (§4 set).
- **Pass:**
  - at least 20% of chains have a `dv(0.04)` initial read set that differs across the 4 audience variants (at either stakes);
  - **and** on the whole set, `dv` beats perspective-blind `latest` by Δreturn ≥ +0.02 at ≤ 1.1× reads, or by ≤ 0.6× reads with Δreturn ≥ −0.01.
- Otherwise stop.

**Overall.**
- **PASS** only if G1a–G1e all pass.
- **STOP** if any gate says stop.
- **Otherwise INCONCLUSIVE.**

## 6. Reporting

Report all of this in `reports/g1/G1_RESULTS.md`, regardless of outcome:
- every selector point with return (and CI), reads per day and U, for both conditions and both stakes;
- the frontier;
- the gate table;
- the perspective-set statistics;
- examples where provenance settles alignment without revealing the value;
- CPU time.

The dense condition is reported as the relevance-density control. Thresholds are not revised after measuring.
