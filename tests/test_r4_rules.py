"""Public people-rules (renderer r5; r4 kept for the record): every clause is checked against the simulator over
EVERY positive-prior world of every dev-v2 instance, not just the realized hidden draw. The scoring reference averages
over that prior support, so a clause that fails anywhere in it misdescribes the reference (Round 1 Opus plan gate).
"""

from __future__ import annotations

import re

import pytest

from officeminds.devgen import generate
from officeminds.world import OBSTRUCTIVE, UNKNOWN, Action, World
from vomi.pilot import PEOPLE_RULES_R4, PEOPLE_RULES_R5, task_card

STATEMENT_FORM = re.compile(r"^\w+ = \w+$")
BEFORE_TASK = {"witness", "tell", "assert", "assess"}
DURING_TASK = {"say", "claim", "enter"}


@pytest.fixture(scope="module")
def traced():
    """[(instance, params, world after reset + one wait step, [(event, minds_before, minds_after)])] over all
    positive-weight prior worlds; scenarios shared by several instances are traced once."""
    out, seen = [], set()
    orig = World._apply
    for inst in generate(version="dev-v2"):
        for params, weight in inst.scenario.prior:
            key = (inst.group_id, inst.family, inst.scenario.brief, repr(params), inst.scenario.config.stakes)
            if weight <= 0 or key in seen:
                continue
            seen.add(key)
            trace = []

            def spy(self, ev, trace=trace):
                before = {p: m.copy() for p, m in self.minds.items()}
                orig(self, ev)
                trace.append((ev, before, {p: m.copy() for p, m in self.minds.items()}))

            World._apply = spy
            try:
                w = inst.scenario.build(params)
                w.reset()
                w.step(Action("wait"))  # t=1 timed events (e.g. the recipient walking in) are applied in step 1
            finally:
                World._apply = orig
            out.append((inst, params, w, trace))
    return out


def test_rules_text_by_revision():
    inst = generate(version="dev-v2")[0]
    cfg, brief = inst.scenario.config, inst.scenario.brief
    assert PEOPLE_RULES_R5 in task_card(cfg, brief, 5) and PEOPLE_RULES_R4 not in task_card(cfg, brief, 5)
    assert PEOPLE_RULES_R4 in task_card(cfg, brief, 4) and PEOPLE_RULES_R5 not in task_card(cfg, brief, 4)
    assert PEOPLE_RULES_R4 not in task_card(cfg, brief, 3)


def test_prior_support_is_covered(traced):
    assert len(traced) > 80  # many worlds per scenario, not only the realized draws


def test_before_and_during_task_event_kinds(traced):
    # rule 1 is about events before the task; rules 2-4 about events during it
    for _, _, _, trace in traced:
        for ev, _, _ in trace:
            assert (ev.kind in BEFORE_TASK and ev.t < 0) or (ev.kind in DURING_TASK and ev.t >= 0) \
                or (ev.kind == "claim" and ev.t < 0), (ev.kind, ev.t)


def test_clause1_belief_formation_adoption_distrust_and_assessments(traced):
    seen = {"witness": 0, "tell": 0, "assert": 0, "assess": 0, "distrust": 0}
    for _, _, w, trace in traced:
        for ev, before, after in trace:
            present = ev.present or ()
            if ev.kind == "witness":
                for p in present:
                    assert after[p].beliefs[ev.fact] == ev.value
                seen["witness"] += 1
            elif ev.kind == "tell":
                for p in present:
                    assert after[p].beliefs[ev.fact] == ev.value
                seen["tell"] += 1
            elif ev.kind == "assert":
                other = next(v for v in w.config.fact_domains[ev.fact] if v != ev.value)
                for p in present:
                    if p == ev.actor:
                        continue
                    distrusts = before[p].assessments.get(ev.actor) == OBSTRUCTIVE
                    seen["distrust"] += distrusts
                    adopted = other if distrusts else ev.value
                    assert after[p].nested[(ev.actor, ev.fact)] == adopted  # takes the speaker to believe it
                    if ev.fact in before[p].beliefs:
                        assert after[p].beliefs[ev.fact] == before[p].beliefs[ev.fact]
                    else:
                        assert after[p].beliefs[ev.fact] == adopted
                seen["assert"] += 1
            elif ev.kind == "assess":
                for p in present:
                    if p != ev.actor or ev.actor != ev.fact:
                        assert after[p].assessments[ev.fact] == ev.value
                seen["assess"] += 1
    assert all(seen.values()), seen


def test_clause2_recipient_self_location_at_start_and_movement_during_task(traced):
    checked = moved = 0
    for inst, params, _, trace in traced:
        cfg = inst.scenario.config
        fact = f"{cfg.recipient}_loc"
        if fact not in cfg.query_facts:
            continue
        w0 = inst.scenario.build(params)
        w0.reset()
        assert w0.minds[cfg.recipient].beliefs.get(fact) == w0.people_rooms[cfg.recipient]
        checked += 1
        for ev, before, after in trace:
            if ev.kind == "enter":
                assert ev.t >= 0 and after[ev.actor].signature() == before[ev.actor].signature()
                moved += 1
    assert checked > 72 and moved > 0


def test_clause3_statements_during_task_make_listeners_attribute_not_adopt(traced):
    n = 0
    for _, _, _, trace in traced:
        for ev, before, after in trace:
            if ev.kind != "claim" or ev.t < 0:
                continue
            n += 1
            assert STATEMENT_FORM.match(ev.text) or ev.text == "I don't know."
            assert after[ev.actor].signature() == before[ev.actor].signature()
            for p in after:
                if p != ev.actor and ev.id in after[p].perceived and ev.id not in before[p].perceived:
                    assert after[p].nested[(ev.actor, ev.fact)] == ev.value
                    assert after[p].beliefs == before[p].beliefs
    assert n > 0


def test_clause4_ordinary_remarks_change_no_beliefs_and_never_look_like_statements(traced):
    n = 0
    for _, _, _, trace in traced:
        for ev, before, after in trace:
            if ev.kind == "say":
                n += 1
                assert not STATEMENT_FORM.match(ev.text) and ev.text != "I don't know."
                assert all(after[p].signature() == before[p].signature() for p in after)
    assert n > 0


def test_clause5_every_change_to_beliefs_about_beliefs_is_explained(traced):
    told_then_updated = 0
    for _, _, _, trace in traced:
        for ev, before, after in trace:
            present = ev.present or ()
            for p in after:
                changed = {k: v for k, v in after[p].nested.items() if before[p].nested.get(k) != v}
                if not changed:
                    continue
                assert ev.kind in ("tell", "claim", "assert"), (ev.kind, p)
                for (other, fact), v in changed.items():
                    assert fact == ev.fact
                    if p == ev.actor:  # speaker models listeners: only tell/assert (never claims)
                        assert ev.kind in ("tell", "assert") and ev.t < 0 and other in present and v == ev.value
                    else:  # listener models the speaker (rule 1 distrust case checked in clause 1)
                        assert other == ev.actor
            if ev.kind == "claim" and ev.t < 0:  # an update passed on in passing: the speaker's view is unchanged
                assert after[ev.actor].nested == before[ev.actor].nested
                told_then_updated += 1
    assert told_then_updated > 0  # the r4 wording of rule 5 was false in these worlds


def test_unknown_answer_is_a_statement_of_no_belief(traced):
    for _, _, _, trace in traced:
        for ev, _, _ in trace:
            if ev.kind == "claim" and ev.text == "I don't know.":
                assert ev.value == UNKNOWN
