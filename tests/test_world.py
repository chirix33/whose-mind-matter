import json

import pytest

from officeminds.episode import episode_record, fixed_policy, replay, run_episode, sample_params
from officeminds.scenarios import TINY_CASES, depth1_knowledge, depth2_handoff
from officeminds.world import (
    Action,
    Event,
    PersonMind,
    World,
    legal_actions,
)
from officeminds.scenarios import _config


def _replay_script():
    return [Action("ask", "rec", "alice_loc"), Action("move", "hall"), Action("move", "office_a"),
            Action("deliver"), Action("move", "hall"), Action("move", "office_b"), Action("deliver")]


@pytest.mark.parametrize("seed", range(6))
def test_replay_reproduces_observations_and_rewards(seed):
    sc = depth1_knowledge()
    params = sample_params(sc, seed)

    def walker(hist):  # simple deterministic visible-only policy
        script = _replay_script()
        return script[len(hist.steps) - 1]

    hist, trace, _ = run_episode(sc, params, walker)
    rec = episode_record(hist, trace)
    again = replay(json.loads(json.dumps(rec)), TINY_CASES)
    assert again == rec
    assert sample_params(sc, seed) == params  # seeded sampling is deterministic


def test_rewards_follow_outline_defaults():
    sc = depth1_knowledge()
    params = (("alice_loc", "office_b"), ("rec_saw", "yes"))
    hist, _, _ = run_episode(sc, params, fixed_policy([Action("drop", "office_b")]))
    assert hist.last.outcome == "success" and hist.last.reward == pytest.approx(0.95)
    hist, _, _ = run_episode(sc, params, fixed_policy([Action("drop", "office_a")]))
    assert hist.last.outcome == "error" and hist.last.reward == pytest.approx(-0.55)
    # Horizon cap: timeout without success.
    hist, _, _ = run_episode(sc, params, fixed_policy([Action("wait")] * 8))
    assert hist.last.outcome == "timeout" and len(hist.steps) == 9


def test_stakes_scale_only_the_irreversible_error():
    from officeminds.scenarios import reliability_stakes
    p = (("alice_loc", "office_b"), ("bob_intent", "obstructive"))
    for m, expected in ((1.0, -0.55), (4.0, -2.05)):
        hist, _, _ = run_episode(reliability_stakes(m, 0.9), p, fixed_policy([Action("drop", "office_a")]))
        assert hist.last.reward == pytest.approx(expected)


def test_invisible_events_never_reach_agent_inputs():
    cfg = _config(["alice", "rec", "dave"], ["alice_loc"])
    secret = Event("t1-secret", 1, "tell", "office_a", "dave", "alice_loc", "office_b", text="SECRET: alice_loc = office_b")
    world_args = dict(
        robot_room="lobby",
        people_rooms={"alice": "office_b", "rec": "lobby", "dave": "office_a"},
        backstory=(Event("bs-hidden", -1, "witness", "hall", "alice", "alice_loc", "office_b", text="BACKSTORY", present=("alice",)),),
        timed_events=(secret,),
    )
    w = World(cfg, minds={p: PersonMind() for p in ("alice", "rec", "dave")}, **world_args)
    o0 = w.reset()
    o1 = w.step(Action("wait"))
    blob = json.dumps([o0.to_dict(), o1.to_dict()])
    assert "SECRET" not in blob and "BACKSTORY" not in blob and "dave" not in blob
    # Same event IS visible when the robot is in that room.
    w2 = World(cfg, minds={p: PersonMind() for p in ("alice", "rec", "dave")}, **(world_args | {"robot_room": "office_a"}))
    w2.reset()
    assert ("dave", secret.text) in w2.step(Action("wait")).utterances


def test_belief_updates_respect_access_and_communication():
    sc = depth2_handoff()
    p = dict((("alice_heard_move", "yes"), ("initial", "office_b"), ("rec_heard_move", "no")))
    w = sc.build(p)
    alice, rec = w.minds["alice"], w.minds["rec"]
    assert alice.beliefs["meeting_room"] == "office_a"  # heard the move
    assert rec.beliefs["meeting_room"] == "office_b"  # absent when the move was announced
    assert rec.nested[("alice", "meeting_room")] == "office_b"  # rec's (now false) belief about Alice
    assert alice.nested[("rec", "meeting_room")] == "office_b"  # Alice knows what she told rec
    assert "bs-move-announced" not in rec.perceived
    assert w.people_rooms["alice"] == "office_a"
    # Regression: a sincere teller holds the belief she tells (else K(alice)=unknown leaks hidden state).
    w = sc.build(p | {"alice_heard_move": "no"})
    assert w.minds["alice"].beliefs["meeting_room"] == "office_b"


def test_ask_answers_follow_belief_and_intent():
    from officeminds.scenarios import reliability_stakes
    sc = reliability_stakes(1.0, 0.5)
    w = sc.build((("alice_loc", "office_a"), ("bob_intent", "obstructive")))
    w.reset()
    o = w.step(Action("ask", "bob", "alice_loc"))
    assert o.utterances == (("bob", "alice_loc = office_b"),)  # an intentional lie
    sc = depth1_knowledge()
    w = sc.build((("alice_loc", "office_a"), ("rec_saw", "no")))
    w.reset()
    assert w.step(Action("ask", "rec", "alice_loc")).utterances == (("rec", "I don't know."),)


def test_legal_actions_use_visible_information_only():
    sc = depth1_knowledge()
    obs = {}
    for params, _ in sc.prior:  # every hidden world yields the same visible menu
        w = sc.build(params)
        obs[params] = [str(a) for a in legal_actions(w.config, w.reset())]
    assert len({tuple(v) for v in obs.values()}) == 1
