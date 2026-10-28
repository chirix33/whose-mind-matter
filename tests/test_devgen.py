"""Pilot dev-set generator (dev-v1): determinism, public-prior discipline, balance, separation."""

import json
from collections import Counter

import pytest

from officeminds.devgen import (
    FAMILIES, GROUPS_PER_FAMILY, KNOBS, NAME_POOL, draw_group, generate, make_instance, registry,
    sample_hidden, variants_for,
)
from officeminds.episode import VisibleHistory, episode_record, fixed_policy, replay, run_episode
from officeminds.world import Action
from vomi.oracle import ExactOracle


@pytest.fixture(scope="module")
def instances():
    return generate()


def test_generation_is_deterministic(instances):
    again = generate()
    assert [(i.instance_id, i.hidden, i.scenario.prior) for i in instances] == \
           [(i.instance_id, i.hidden, i.scenario.prior) for i in again]


def test_public_prior_is_fixed_before_hidden_sampling():
    """The prior depends only on the public group draw; changing the hidden stream cannot change it."""
    g = draw_group("false_belief", 1)
    prior = make_instance(g, variants_for("false_belief")[0]).prior
    hiddens = {sample_hidden(prior, "false_belief", 1, seed=s) for s in range(40)}
    assert len(hiddens) > 1  # the hidden draw varies with its own seed ...
    assert make_instance(draw_group("false_belief", 1), variants_for("false_belief")[0]).prior == prior  # ... prior does not


def test_balance_and_grouping(instances):
    groups = {i.group_id for i in instances}
    assert len(groups) == len(FAMILIES) * GROUPS_PER_FAMILY == 36
    assert 30 <= len(groups) <= 50
    per_family = Counter(i.family for i in instances)
    for f in FAMILIES:
        assert per_family[f] == GROUPS_PER_FAMILY * 2 ** len(KNOBS[f])
    assert len({i.instance_id for i in instances}) == len(instances)
    by_group: dict[str, list] = {}
    for i in instances:
        by_group.setdefault(i.group_id, []).append(i)
    for members in by_group.values():  # variants are paired: one prior, one hidden world
        assert len({m.hidden for m in members}) == 1
        assert len({tuple(m.scenario.prior) for m in members}) == 1


def test_names_and_labels_vary_across_groups():
    draws = [draw_group(f, k) for f in FAMILIES for k in range(GROUPS_PER_FAMILY)]
    assert all(set(d.names) <= set(NAME_POOL) for d in draws)
    assert len({d.names[0] for d in draws}) > 10  # many different recipients
    assert len({d.offices for d in draws}) > 3  # several office label sets and orders


def test_agent_views_contain_no_hidden_parameters(instances):
    for inst in instances:
        w = inst.scenario.build(inst.hidden)
        view = json.dumps(VisibleHistory(inst.scenario.brief, [(None, w.reset())]).to_agent_dict())
        for key, _ in inst.hidden:
            assert f'"{key}"' not in view
        assert "bs-" not in view
        assert inst.scenario.brief.split()[-1].rstrip(".").lower() == w.config.recipient


def test_true_world_is_in_its_posterior_support(instances):
    for inst in instances:
        w = inst.scenario.build(inst.hidden)
        o = ExactOracle(inst.scenario, VisibleHistory(inst.scenario.brief, [(None, w.reset())]))
        assert inst.hidden in o.params


def test_one_instance_per_family_replays_through_the_registry(instances):
    reg = registry()
    for f in FAMILIES:
        inst = next(i for i in instances if i.family == f)
        hist, trace, _ = run_episode(inst.scenario, inst.hidden, fixed_policy([Action("wait")] * 8))
        rec = episode_record(hist, trace)
        assert replay(json.loads(json.dumps(rec)), reg) == rec


def test_stakes_variants_differ_only_in_stakes(instances):
    by_group: dict[str, list] = {}
    for i in instances:
        if "stakes" in KNOBS[i.family]:
            by_group.setdefault(i.group_id, []).append(i)
    for members in by_group.values():
        for a in members:
            for b in members:
                if a.variant.evidence == b.variant.evidence and a.variant.stakes != b.variant.stakes:
                    wa, wb = a.scenario.build(a.hidden), b.scenario.build(b.hidden)
                    assert wa.reset() == wb.reset()
                    assert {k: v for k, v in wa.config.__dict__.items() if k != "stakes"} == \
                           {k: v for k, v in wb.config.__dict__.items() if k != "stakes"}
