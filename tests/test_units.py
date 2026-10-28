from officeminds.episode import VisibleHistory
from officeminds.scenarios import TINY_CASES
from officeminds.world import Action
from vomi.units import K, R, content, generate_candidates


def first_hist(case):
    sc = TINY_CASES[case]()
    w = sc.build(sc.prior[0][0])
    return sc, w, VisibleHistory(sc.brief, [(None, w.reset())])


def test_candidates_depend_only_on_visible_history():
    """Worlds that differ only in hidden state must yield identical candidate menus."""
    import json
    for case in TINY_CASES:
        sc = TINY_CASES[case]()
        menus: dict[str, set] = {}
        for params, _ in sc.prior:
            w = sc.build(params)
            hist = VisibleHistory(sc.brief, [(None, w.reset())])
            view = json.dumps(hist.to_agent_dict(), sort_keys=True)
            menus.setdefault(view, set()).add(tuple(generate_candidates(sc.config, hist)))
        assert all(len(m) == 1 for m in menus.values()), case


def test_reliability_requires_visible_incentive_or_conflict():
    sc, _, hist = first_hist("stakes_m1_q0.975")
    assert R("bob") in generate_candidates(sc.config, hist)
    sc, w, hist = first_hist("depth1_knowledge")
    assert not any(u.variable == "reliability" for u in generate_candidates(sc.config, hist))


def test_depth2_requires_visible_communication_or_copresence():
    sc, _, hist = first_hist("depth1_knowledge")
    cands = generate_candidates(sc.config, hist)
    assert K("rec", "alice") not in cands  # Alice only mentioned; no visible contact with rec
    sc, _, hist = first_hist("depth2_handoff")
    assert K("rec", "alice") in generate_candidates(sc.config, hist)


def test_nested_content_is_js_belief_about_k_not_ks_state():
    sc = TINY_CASES["depth2_handoff"]()
    w = sc.build((("alice_heard_move", "yes"), ("initial", "office_b"), ("rec_heard_move", "no")))
    assert content(w, K("alice")) == ("office_a",)
    assert content(w, K("rec", "alice")) == ("office_b",)  # a false nested belief
    assert content(w, R("rec")) == ("cooperative",)


def test_bystanders_track_claims_without_adopting_them():
    sc = TINY_CASES["distractor_plausible"]()
    w = sc.build((("alice_loc", "office_a"), ("carol_saw", "no"), ("rec_saw", "yes")))
    w.reset()
    w.step(Action("ask", "rec", "alice_loc"))
    assert content(w, K("carol", "rec")) == ("office_a",)
    assert content(w, K("carol")) == ("unknown",)
