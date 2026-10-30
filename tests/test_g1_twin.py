"""G1 symbolic twin (D-023): hand-checkable cases and invariants (CPU only)."""

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import g1_symbolic_twin as T  # noqa: E402


def P(listeners, contents, a="o1", q=0.3):
    return T.Person("p0", a, q, list(listeners), list(contents))


def test_no_messages_everyone_aligned_give():
    p = P([], [])
    v, opt, _ = T.value(p, {}, 1.0)
    assert opt == "give(c1)" and v == pytest.approx(0.95)
    assert T.sel_dv(p, {}, 1.0, 0.04) == [] and T.sel_action_prov(p, {}, 1.0) == []


def test_provenance_establishes_alignment_without_value():
    p = P(["p3", "c2"], ["o2", "o3"])  # c2 heard the latest message; its value is unknown to the robot
    v, opt, _ = T.value(p, {}, 4.0)
    assert opt == "give(c2)" and v == pytest.approx(0.95)
    assert T.sel_dv(p, {}, 4.0, 0.04) == [] and T.sel_action_prov(p, {}, 4.0) == []


def test_perspective_pair_changes_best_read_with_fixed_physical_history():
    a = P(["c1", "c2"], ["o2", "o3"])  # c2 heard the latest: no read needed
    b = P(["c1", "p5"], ["o2", "o3"])  # nobody with a route heard the latest: reading is worth it
    assert T.sel_dv(a, {}, 4.0, 0.04) == []
    assert T.sel_dv(b, {}, 4.0, 0.04) != []
    assert a.loc() == b.loc()


def test_markov_prior_and_normalization():
    p = P(["p3"], ["o1"], q=0.5)
    ws = dict(T.chain_worlds(p, {}))
    assert ws[("o1",)] == pytest.approx(0.5) and ws[("o2",)] == pytest.approx(0.25)
    assert sum(ws.values()) == pytest.approx(1.0)


def test_realized_search_order():
    p = P(["p3"], ["o3"], q=0.1)  # posterior favours o1 (stay); truth o3
    known = {1: "o3"}
    r, opt = T.realized(p, known, 1.0)
    assert opt == "search" and r == pytest.approx(0.85)


def test_voi_nonnegative_and_full_info_dominates():
    rng = random.Random(0)
    cast = ["c1", "c2"] + [f"p{i}" for i in range(8)]
    for _ in range(200):
        p = T.make_person(rng, "p0", cast, L=rng.choice((1, 2, 3)))
        for s in (1.0, 4.0):
            for j in range(1, p.L + 1):
                assert T.voi(p, {}, (j,), s) >= -1e-12
            full = {j: p.contents[j - 1] for j in range(1, p.L + 1)}
            # expected full-information value >= provenance-only value (averaged over the prior)
            assert T.voi(p, {}, tuple(range(1, p.L + 1)), s) >= -1e-12 if p.L <= 3 else True
            assert T.value(p, full, s)[0] >= -1


def test_day_generation_is_deterministic():
    a, b = T.make_day("sparse", 7), T.make_day("sparse", 7)
    assert [(x.a, x.q, x.listeners, x.contents) for x in a.people.values()] == \
           [(x.a, x.q, x.listeners, x.contents) for x in b.people.values()]
    assert a.recipients == b.recipients
