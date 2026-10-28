"""Checkable forms of the theory safeguards (AGENTS §5.4) and the D-005 incentive audit."""

from __future__ import annotations

from officeminds.world import Observation, World, legal_actions


def p2_certifies_no_flip(q: dict, max_gap_decrease: dict) -> bool:
    """P2 (current-action component only).

    ``q``: the actor's action values under allocation S. ``max_gap_decrease[a]``: an upper bound,
    over every feasible content of the units rooted at person j, on how much the PAIRWISE gap
    q(a1) - q(a) can shrink, where a1 is the current best action. The best action cannot change
    iff every gap strictly exceeds its bound. At equality a tie is possible, so certification
    fails. A bound on each action's own change (|Δq(a)| <= δ) bounds a gap change only by 2δ.
    """
    a1 = max(q, key=q.get)
    return all(q[a1] - q[a] > max_gap_decrease[a] for a in q if a != a1)


def gap_decrease_bounds(q: dict, q_by_content: list[dict]) -> dict:
    """Exact max gap decrease over an enumerated list of content-conditioned action values."""
    a1 = max(q, key=q.get)
    return {a: max((q[a1] - q[a]) - (qc[a1] - qc[a]) for qc in q_by_content) for a in q if a != a1}


def best_return_by_outcome(world: World, obs: Observation, horizon_left: int | None = None) -> dict[str, float]:
    """Full-information audit: best achievable return for each terminal outcome (success /
    error / timeout) by exhaustive search. Used to detect early-failure incentives."""
    out: dict[str, float] = {}
    for a in legal_actions(world.config, obs):
        w = world.clone()
        o = w.step(a)
        if o.done:
            out[o.outcome] = max(out.get(o.outcome, -1e9), o.reward)
            continue
        for outcome, r in best_return_by_outcome(w, o).items():
            out[outcome] = max(out.get(outcome, -1e9), o.reward + r)
    return out
