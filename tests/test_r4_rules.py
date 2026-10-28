"""Renderer r4 public people-rules: every clause is checked against the simulator on all dev-v2 instances
(autonomous block, Round 1). A clause that the simulator does not implement must not appear in the rules.
"""

from __future__ import annotations

import re

import pytest

from officeminds.devgen import generate
from officeminds.world import OBSTRUCTIVE, UNKNOWN, Action, World
from vomi.pilot import PEOPLE_RULES_R4, task_card

STATEMENT_FORM = re.compile(r"^\w+ = \w+$")


@pytest.fixture(scope="module")
def traced():
    """(instance, world after reset + one wait step, [(event, minds_before, minds_after)]) per dev-v2 instance."""
    out = []
    orig = World._apply
    for inst in generate(version="dev-v2"):
        trace = []

        def spy(self, ev, trace=trace):
            before = {p: m.copy() for p, m in self.minds.items()}
            orig(self, ev)
            trace.append((ev, before, {p: m.copy() for p, m in self.minds.items()}))

        World._apply = spy
        try:
            w = inst.scenario.build(inst.hidden)
            w.reset()
            w.step(Action("wait"))  # t=1 timed events (e.g. the recipient walking in) are applied during step 1
        finally:
            World._apply = orig
        out.append((inst, w, trace))
    return out


def test_r4_rules_text_is_in_the_task_card_from_revision_4_only():
    inst = generate(version="dev-v2")[0]
    cfg = inst.scenario.config
    assert PEOPLE_RULES_R4 in task_card(cfg, inst.scenario.brief, 4)
    assert PEOPLE_RULES_R4 not in task_card(cfg, inst.scenario.brief, 3)


def test_clause1_seeing_and_sincere_telling_create_beliefs_and_adoption_respects_distrust(traced):
    seen = {"witness": 0, "tell": 0, "assert": 0}
    for _, w, trace in traced:
        for ev, before, after in trace:
            present = ev.present if ev.present is not None else None
            if ev.kind == "witness":
                for p in present or ():
                    assert after[p].beliefs[ev.fact] == ev.value
                seen["witness"] += 1
            elif ev.kind == "tell":
                for p in (present or ()):
                    assert after[p].beliefs[ev.fact] == ev.value  # sincere: speaker and listeners believe it
                seen["tell"] += 1
            elif ev.kind == "assert":
                other = next(v for v in w.config.fact_domains[ev.fact] if v != ev.value)
                for p in (present or ()):
                    if p == ev.actor:
                        continue
                    distrusts = before[p].assessments.get(ev.actor) == OBSTRUCTIVE
                    if ev.fact in before[p].beliefs:  # a person with a belief of their own keeps it
                        assert after[p].beliefs[ev.fact] == before[p].beliefs[ev.fact]
                    else:
                        assert after[p].beliefs[ev.fact] == (other if distrusts else ev.value)
                seen["assert"] += 1
    assert all(seen.values()), seen


def test_clause2_recipient_knows_own_location_at_start_but_movement_updates_no_one(traced):
    checked = moved = 0
    for inst, w, trace in traced:
        cfg = inst.scenario.config
        fact = f"{cfg.recipient}_loc"
        if fact not in cfg.query_facts:
            continue
        w0 = inst.scenario.build(inst.hidden)
        w0.reset()
        assert w0.minds[cfg.recipient].beliefs.get(fact) == w0.people_rooms[cfg.recipient]
        checked += 1
        for ev, before, after in trace:
            if ev.kind == "enter":  # documented limitation: the mover's own belief is not updated
                assert after[ev.actor].signature() == before[ev.actor].signature()
                moved += 1
    assert checked == 72 and moved == 4


def test_clause3_statements_make_listeners_attribute_not_adopt(traced):
    n = 0
    for _, w, trace in traced:
        for ev, before, after in trace:
            if ev.kind != "claim" or ev.t < 0:
                continue
            n += 1
            assert STATEMENT_FORM.match(ev.text) or ev.text == "I don't know."
            assert after[ev.actor].signature() == before[ev.actor].signature()  # speaker gains nothing
            for p in after:
                if p == ev.actor:
                    continue
                if ev.id in after[p].perceived and ev.id not in before[p].perceived:
                    assert after[p].nested[(ev.actor, ev.fact)] == ev.value
                    assert after[p].beliefs == before[p].beliefs
    assert n > 0


def test_clause4_ordinary_remarks_change_no_beliefs_and_never_look_like_statements(traced):
    n = 0
    for _, _, trace in traced:
        for ev, before, after in trace:
            if ev.kind == "say":
                n += 1
                assert not STATEMENT_FORM.match(ev.text) and ev.text != "I don't know."
                assert all(after[p].signature() == before[p].signature() for p in after)
    assert n > 0


def test_clause5_beliefs_about_beliefs_come_only_from_statements(traced):
    for _, _, trace in traced:
        for ev, before, after in trace:
            changed = [p for p in after if after[p].nested != before[p].nested]
            if ev.kind in ("witness", "enter", "say", "assess"):
                assert not changed, (ev.kind, ev.id)
            if ev.kind in ("tell", "assert") and ev.t < 0:  # a speaker who told listeners earlier models them
                present = ev.present or ()
                for p in present:
                    if p != ev.actor:
                        assert after[ev.actor].nested[(p, ev.fact)] == ev.value
            if ev.kind == "claim" and ev.t >= 0:  # in-task statements give the speaker no view of listeners
                assert after[ev.actor].nested == before[ev.actor].nested


def test_dev_v2_backstory_has_no_claim_events(traced):
    # Clause 5's "told someone before the task" wording relies on this: backstory statements are tell/assert.
    assert not any(ev.kind == "claim" and ev.t < 0 for _, _, trace in traced for ev, _, _ in trace)


def test_unknown_answer_is_a_statement_of_no_belief(traced):
    for _, _, trace in traced:
        for ev, _, after in trace:
            if ev.kind == "claim" and ev.text == "I don't know.":
                assert ev.value == UNKNOWN
