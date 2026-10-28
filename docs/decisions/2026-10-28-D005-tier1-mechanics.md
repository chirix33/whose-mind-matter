# D-005 — Tier 1 mechanics defaults

- Status: **accepted with explicit transition semantics** (review 2026-10-28)
- Date: 2026-10-28
- Affects: outline §5.1; AGENTS §6 Stage 1

| Mechanic | Current default | Why it matters |
|---|---|---|
| Reward | +1 success; −0.05 on **every** step, including the terminal one; −0.5 × stakes on an irreversible error; timeout at the horizon with no extra penalty | outline defaults; the terminal-step charge and the timeout convention are our choices |
| Irreversible errors | wrong chute `drop(office)` (lobby only); `give(person)` routed to the wrong room | the outline names no concrete irreversible action |
| Closed offices | the robot sees occupants only after entering | creates the value of information |
| Handoff routing | the person routes by their own belief, or by a specified nested belief (`depth2_handoff`: rec routes by her belief about Alice's belief) | the source of depth-2 decision relevance |
| Sincere `tell` vs. insincere `claim` | a tell updates the speaker's own belief and the listeners' beliefs; a claim (an answer to `ask`) only updates listeners' nested beliefs | bystanders track what was claimed without adopting it |
| Bug fixed during Stage 0 | sincere tellers originally did not hold the belief they told, so K(alice) = unknown leaked hidden state | caught by the hand check of `depth2_handoff` (J(K(alice)) came out 0.90 instead of 0.85); regression test added |
| Horizon | 8 for the tiny cases | the outline says 5–10 steps, capped at 15 |
| Action set | `move`, `ask(person, fact)`, `drop`, `give`, `deliver`, `wait` | the outline lists `pick/give`; `pick` is unused until objects such as keycards exist |

Requested review: confirm that the irreversible-error mechanics and the terminal-step and timeout conventions are acceptable as Tier 1 defaults before the balanced generator is built.

## Review outcome
**Accepted, with explicit semantics.** Supplied by the research review 2026-10-28 (`research-reviews/stage-0-research-review.md`, supplied by Ashraf; that folder is gitignored, so the binding points are restated here).

- −0.05 on every executed step, including terminal ones. +1 on success.
- A wrong chute drop is irreversible: −0.5 × stakes (only the error component is scaled), and the episode ends in failure. A one-step failure returns −0.55.
- A mis-routed handoff is irreversible **only if the declared world rules make recovery impossible**. Declared rule (this implementation): after `give`, the package leaves the robot's custody and Tier 1 has no recovery action. The handoff is therefore terminal and irreversible.
- At the step cap the transition and reward apply first, so a success on the last allowed step counts. Otherwise the episode times out with no extra penalty.
- One fixed invalid-action protocol for all methods: an invalid action is a no-op that still costs the step. Generation retries are counted in compute.
- Oracle audit for early-failure incentives: report affected scenarios; do not change reward magnitudes or drop cases.
