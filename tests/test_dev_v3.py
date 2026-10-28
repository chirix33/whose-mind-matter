"""dev-v3 qualification invariants (reports/dev-v3-block/experiment-plan.md, A.3 checks 1-4, 8-10).

Every check runs over ALL positive-prior worlds of every dev-v3 instance, at t0 and after every legal first action.
"""

from __future__ import annotations

import re
from fractions import Fraction

import pytest

from officeminds.devgen3 import (CONSTRUCTIONS, ROLES, VARIANTS, draw_spec, generate, hidden_vars, role_names)
from officeminds.episode import VisibleHistory, episode_record, fixed_policy, replay, run_episode
from officeminds.world import COOPERATIVE, UNKNOWN, Action, legal_actions
from vomi.oracle import ExactOracle
from vomi.pilot import PEOPLE_RULES_R6, ledger, task_card
from vomi.units import K, content

INSTS = generate()
BY_ID = {i.instance_id: i for i in INSTS}


def worlds(inst):
    for params, _ in inst.scenario.prior:
        yield params, inst.scenario.build(params)


def after_first_actions(inst):
    """(world, history) at t0 and after each legal first action, for every prior world."""
    for params, w in worlds(inst):
        o0 = w.reset()
        yield w, VisibleHistory(inst.scenario.brief, [(None, o0)])
        for a in legal_actions(w.config, o0):
            w2 = inst.scenario.build(params)
            o = w2.reset()
            yield w2, VisibleHistory(inst.scenario.brief, [(None, o), (a, w2.step(a))])


def test_counts_and_balance():
    assert len(INSTS) == 48 and len({i.group_id for i in INSTS}) == 12
    levels = {}
    for i in INSTS:
        levels.setdefault(i.stratum, set()).add(i.distractor)
    assert all(v == {"none", "plausible", "obvious"} for v in levels.values())


def test_variants_share_hidden_draw_and_prior():
    for g in {i.group_id for i in INSTS}:
        members = [i for i in INSTS if i.group_id == g]
        assert len(members) == 4 and len({i.hidden for i in members}) == 1
        assert len({i.scenario.prior for i in members}) == 1


def test_reference_inputs_are_the_disclosed_spec():
    """A.3 check 3: hidden variables, supports and probabilities in the prior == the disclosed spec in the card."""
    for inst in INSTS:
        n = inst.role
        hv = hidden_vars(inst.spec, n)
        card = task_card(inst.scenario.config, inst.scenario.brief, rev=6)
        names = sorted(p[0] for p in inst.scenario.prior[0][0])
        assert names == sorted(h.name for h in hv)
        for h in hv:
            assert h.description in card
            assert sum(p for _, p in h.dist) == 1
            if h.name not in ("m1", "m2", "x_lie", "y_lie"):  # these are printed as "each equally likely"
                for v, p in h.dist:
                    assert f"{v} {float(p):.4g}" in card
            else:
                assert "equally likely" in h.description and all(p == Fraction(1, 2) for _, p in h.dist)
        # the prior is the product of the disclosed distributions (filtered by the disclosed 4b conflict rule)
        total = 0.0
        for params, w in inst.scenario.prior:
            d = dict(params)
            prod = 1.0
            for h in hv:
                prod *= float(dict(h.dist)[d[h.name]])
            total += prod
        for params, w in inst.scenario.prior:
            d = dict(params)
            prod = 1.0
            for h in hv:
                prod *= float(dict(h.dist)[d[h.name]])
            assert abs(w - prod / total) < 1e-12


def test_card_has_r6_and_public_model_and_no_hidden_values():
    for inst in INSTS:
        cfg = inst.scenario.config
        card = task_card(cfg, inst.scenario.brief, rev=6)
        assert PEOPLE_RULES_R6 in card and "PUBLIC MODEL OF THIS TASK" in card
        assert cfg.roster == tuple(sorted(cfg.roster))
        # card and brief identical in every world of the instance (no world-specific text)
        cards = {task_card(w.config, inst.scenario.brief, rev=6) for _, w in worlds(inst)}
        assert len(cards) == 1


def traced(w):
    """Wrap World._apply to record (event, people present when it applied, minds before, minds after)."""
    rec = []
    orig = w._apply

    def spy(ev):
        before = {p: m.copy() for p, m in w.minds.items()}
        orig(ev)
        present = ev.present if ev.present is not None else tuple(p for p, r in w.people_rooms.items() if r == ev.room)
        rec.append((ev, present, before, {p: m.copy() for p, m in w.minds.items()}))
    w._apply = spy
    return rec


def all_traces(inst):
    """Traced t0 prologue of every prior world, plus (on a fresh world each) every legal first ask's answer."""
    for params, _ in inst.scenario.prior:
        w = inst.scenario.build(params)
        rec = traced(w)
        o = w.reset()
        yield rec
        for act in [x for x in legal_actions(w.config, o) if x.kind == "ask"]:
            w2 = inst.scenario.build(params)
            rec2 = traced(w2)
            w2.reset()
            del rec2[:]  # only the answer
            w2.step(act)
            yield rec2


def test_rule1_and_rule5_quiet_conversations():
    """Only the addressee adopts; speaker and addressee form the stated nested beliefs; bystanders' beliefs and
    nested beliefs are unchanged (rule 1, rule 5 bystander clause)."""
    n_quiet = 0
    for inst in INSTS:
        for rec in all_traces(inst):
            for ev, present, before, after in rec:
                if not (ev.visible_as and ev.visible_as[0] == "quiet"):
                    continue
                n_quiet += 1
                speaker, addressee = ev.present
                assert ev.actor == speaker and after[addressee].beliefs[ev.fact] == ev.value
                assert after[addressee].nested[(speaker, ev.fact)] == ev.value
                assert after[speaker].nested[(addressee, ev.fact)] == ev.value
                lobby = [p for p in after if p not in ev.present]
                for p in lobby:
                    assert after[p].beliefs == before[p].beliefs and after[p].nested == before[p].nested
    assert n_quiet > 0


def test_rule2_recipient_knows_own_office():
    for inst in INSTS:
        R = inst.scenario.config.recipient
        lf = f"{R}_loc"
        for w, h in after_first_actions(inst):
            if lf in w.config.query_facts:
                assert w.minds[R].beliefs.get(lf) == w.people_rooms[R]


def test_rule2_lobby_sightings_change_no_beliefs():
    """Arriving, leaving and being seen (enter events) change no one's beliefs or nested beliefs."""
    n = 0
    for inst in INSTS:
        for rec in all_traces(inst):
            for ev, present, before, after in rec:
                if ev.kind == "enter":
                    n += 1
                    assert all(after[p].signature() == before[p].signature() for p in after)
    assert n > 0


def test_rule3_statements_are_not_adopted_and_give_speaker_nothing():
    """t0 statements and every first-question answer, in every prior world."""
    n = 0
    for inst in INSTS:
        for rec in all_traces(inst):
            for ev, present, before, after in rec:
                if ev.kind != "claim":
                    continue
                listeners = [p for p in present if p != ev.actor]
                n += len(listeners)
                for p in after:
                    assert after[p].beliefs == before[p].beliefs
                assert after[ev.actor].nested == before[ev.actor].nested
                for p in listeners:
                    assert after[p].nested[(ev.actor, ev.fact)] == ev.value
    assert n > 0


def test_rule4_remarks_change_nothing():
    for inst in INSTS:
        for rec in all_traces(inst):
            for ev, present, before, after in rec:
                if ev.kind == "say":
                    assert all(after[p].signature() == before[p].signature() for p in after)


def test_rule5_nested_beliefs_only_from_statements_and_announcements():
    """Every change to a nested belief j->k is caused by a statement/announcement BY k that j heard, or by j's own
    announcement/quiet conversation that k heard (t0 prologue and every first-question answer)."""
    for inst in INSTS:
        for rec in all_traces(inst):
            for ev, present, before, after in rec:
                for j in after:
                    for key, v in after[j].nested.items():
                        if before[j].nested.get(key) == v:
                            continue
                        k, f = key
                        assert ev.kind in ("tell", "claim") and ev.fact == f and ev.value == v, (inst.instance_id, ev)
                        assert (ev.actor == k and j in present) or (ev.actor == j and ev.kind == "tell" and k in present)


def test_quiet_notice_names_speaker_and_excludes_addressee_from_others():
    for inst in INSTS:
        o = inst.scenario.build(inst.hidden).reset()
        for kind, actor, line, others in o.notices:
            if kind == "quiet":
                addressee = line.split(" talks quietly to ")[1].split(";")[0]
                assert line.startswith(f"{actor} talks quietly to ") and addressee not in others and actor not in others


def test_rule6_only_declared_people_may_mislead():
    for inst in INSTS:
        allowed = {inst.role[r] for r in ("X", "Y") if r in inst.role and inst.construction in ("4b", "4c")}
        if inst.construction == "4c":
            allowed = {inst.role["X"]}
        for _, w in worlds(inst):
            for p, m in w.minds.items():
                if m.intent != COOPERATIVE:
                    assert p in allowed


def test_designed_contents():
    """A.3 check 2: the designed first-order and depth-2 contents (t0, every world)."""
    for inst in INSTS:
        n, c, o = inst.role, inst.construction, inst.scenario.config.offices
        for params, w in worlds(inst):
            w.reset()
            p = dict(params)
            a = p["a"]
            if c in ("2a", "2b"):
                assert content(w, K(n["N"])) == (a,)  # stale
                assert content(w, K(n["H"]))[0] == w.people_rooms[n["R"]] != a  # current
            if c == "2c":
                assert content(w, K(n["N"]))[0] == w.people_rooms[n["R"]]
            if c.startswith("3"):
                fr = content(w, K(n["F"], n["R"]))[0]
                assert w.people_rooms[n["R"]] == (fr if c in ("3a", "3c") else w.facts["meeting_room"])
                if c == "3b":
                    assert fr == a and content(w, K(n["F"]))[0] == w.facts["meeting_room"] != a
            if c == "1b":
                assert all(content(w, K(x)) == (UNKNOWN,) for x in w.minds if x != n["R"])


def test_evidence_resolved_access_status():
    """A.3 check 4 (strata 1-3): each focal unit's access status is identical in every world consistent with t0."""
    from officeminds.devgen3 import focal_units

    from officeminds.devgen3 import access_status

    for inst in INSTS:
        if inst.stratum == 4:
            continue
        w0 = inst.scenario.build(inst.hidden)
        h = VisibleHistory(inst.scenario.brief, [(None, w0.reset())])
        o = ExactOracle(inst.scenario, h)
        for u in focal_units(inst):
            sts = {access_status(x, u) for x in o.worlds}
            assert len(sts) == 1, (inst.instance_id, str(u), sts)


def test_no_bounded_actor_in_dev_v3_primary_code():
    """R7: primary dev-v3 quantities use the plain posterior; no GROUNDED_* record or face-value epsilon."""
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    for f in ("scripts/qualify_dev_v3.py", "scripts/run_dev_v3_notes.py", "src/officeminds/devgen3.py"):
        p = root / f
        if p.exists():
            src = p.read_text(encoding="utf-8")
            assert "GROUNDED" not in src and "TESTIMONY_DEFAULTS" not in src and "testimony=" not in src, f


def test_agent_visible_text_has_no_design_labels():
    """R15: no instance/group/construction IDs, stratum names, construction labels, purpose text or focal lists."""
    from officeminds.devgen3 import PURPOSE, STRATA, focal_units
    from vomi.pilot import load_prompts, policy_messages, unit_messages
    prompts = load_prompts("pilot-v2.1")
    banned = [r"\bdev-v3\b", r"\b[1-4][abc]\b", r"\bfocal\b", r"\brelayed\b", r"\bstale\b", r"\buninformed\b",
              r"\bdeparted\b", r"\bdistractor\b", r"\bsuperset\b"] + [rf"\b{v}\b" for v in STRATA.values()]
    for inst in INSTS:
        w = inst.scenario.build(inst.hidden)
        h = VisibleHistory(inst.scenario.brief, [(None, w.reset())])
        cfg = inst.scenario.config
        texts = [policy_messages(prompts, cfg, inst.scenario.brief, h, None, 6)[0][1]["content"]]
        texts += [unit_messages(prompts, cfg, inst.scenario.brief, h, u, "pilot-v2.1", 6)[0][1]["content"]
                  for u in focal_units(inst)]
        for t in texts:
            assert inst.instance_id not in t and inst.group_id not in t and PURPOSE[inst.construction] not in t
            for b in banned:
                assert not re.search(b, t), (inst.instance_id, b)


def test_hidden_stream_independent_of_variant():
    import inspect
    from officeminds import devgen3
    src = inspect.getsource(devgen3.sample_hidden)
    assert "variant" not in src and "permuted" not in src and "stakes" not in src


def test_permuted_variant_is_isomorphic():
    for g in {i.group_id for i in INSTS}:
        base = BY_ID[f"{g}-stakes1-perm0"]
        perm = BY_ID[f"{g}-stakes1-perm1"]
        m = {base.role[r]: perm.role[r] for r in base.role}
        hb = ledger(VisibleHistory(base.scenario.brief, [(None, base.scenario.build(base.hidden).reset())]))[0]
        hp = ledger(VisibleHistory(perm.scenario.brief, [(None, perm.scenario.build(perm.hidden).reset())]))[0]
        assert hb != hp
        mapped = re.sub(r"(?<![A-Za-z])(" + "|".join(m) + r")(?![A-Za-z])", lambda x: m[x[0]], hb)  # incl. <name>_loc

        def norm(text):  # name lists are sorted alphabetically, so compare them as sets; seen-lines as a multiset
            out = []
            for line in text.splitlines():
                line = re.sub(r"\[t0:seen:\w+\]", "[t0:seen]", line)
                line = re.sub(r"others present: ([\w, ]+)\)", lambda x: "others present: "
                              + ", ".join(sorted(x[1].split(", "))) + ")", line)
                out.append(line)
            return sorted(out)
        assert norm(mapped) == norm(hp)


def test_replay_reproduces_rollouts():
    for inst in INSTS[:: 4]:
        w = inst.scenario.build(inst.hidden)
        acts = [a for a in legal_actions(w.config, w.reset()) if a.kind in ("move", "ask", "wait")][:1]
        acts += [Action("wait")] * (w.config.horizon - 1)
        hist, trace, _ = run_episode(inst.scenario, inst.hidden, fixed_policy(acts))
        rec = episode_record(hist, trace)
        reg = {inst.instance_id: (lambda s=inst.scenario: s)}
        assert replay(rec, reg) == rec
