"""Repair block Stage 1 (D-015): citable public model (r7), pilot-v2.2 validator, matched note renderer."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from officeminds.devgen3 import PURPOSE, STRATA, focal_units, generate
from officeminds.episode import VisibleHistory
from vomi.graph import PerspectiveGraph
from vomi.pilot import (PACKAGES, load_prompts, notes_text, numbered_public_model, policy_messages, task_card,
                        unit_messages)

ROOT = Path(__file__).resolve().parents[1]
INSTS = generate()


def t0(inst):
    w = inst.scenario.build(inst.hidden)
    return w, VisibleHistory(inst.scenario.brief, [(None, w.reset())])


def test_dev_v3_generator_unchanged_since_freeze():
    fz = json.loads((ROOT / "reports/dev-v3-block/dev-v3-freeze.json").read_text())
    for f in ("src/officeminds/devgen3.py", "src/officeminds/world.py"):
        assert hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == fz["source_sha256"][f]


def test_pm_ids_stable_and_sequential():
    for inst in INSTS:
        cfg = inst.scenario.config
        text, ids = numbered_public_model(cfg.public_model)
        assert ids == [f"PM{i}" for i in range(1, len(ids) + 1)] and len(ids) >= 3
        assert all(f"[{i}]" in text for i in ids)
        card7, card6 = task_card(cfg, inst.scenario.brief, rev=7), task_card(cfg, inst.scenario.brief, rev=6)
        assert "[PM1]" in card7 and "[PM1]" not in card6
        assert card7.replace("[PM", "").count("PUBLIC MODEL") == card6.count("PUBLIC MODEL")
        assert numbered_public_model(cfg.public_model) == (text, ids)  # deterministic


def _note(path, variable, hyps, status="grounded"):
    return json.dumps({"path": list(path), "variable": variable, "about": "x", "as_of_step": 0, "status": status,
                       "hypotheses": hyps, "unresolved": []})


def test_v22_validator_citations():
    inst = next(i for i in INSTS if i.construction == "4b")
    cfg = inst.scenario.config
    _, h = t0(inst)
    u = focal_units(inst)[0]
    msgs, domain, ids = unit_messages(load_prompts("pilot-v2.2"), cfg, inst.scenario.brief, h, u, "pilot-v2.2", 7)
    assert {"PM1", "PM2"} <= ids and "t0:note0" in ids
    v = PACKAGES["pilot-v2.2"].validate

    def hyp(eid, kind):
        return [{"value": "cooperative", "p": 0.9, "support": [{"evidence_id": eid, "kind": kind, "note": "n"}]},
                {"value": "obstructive", "p": 0.1, "support": [{"evidence_id": "t0:note0", "kind": "testimony", "note": "n"}]}]
    ok, err = v(_note(u.path, u.variable, hyp("PM3", "public_model")), u.path, u.variable, domain, ids)
    assert ok is not None and ok["public_model_ids"] == ["PM3"], err
    ok, err = v(_note(u.path, u.variable, hyp("RULE6", "public_rule")), u.path, u.variable, domain, ids)
    assert ok is not None, err
    for bad_id, kind, code in (("PUBLIC_MODEL", "public_model", "cites_non_visible_evidence"),
                               ("PM99", "public_model", "cites_non_visible_evidence"),
                               ("PM3", "testimony", "public_model_citation_mismatch"),
                               ("t0:note0", "public_model", "public_model_citation_mismatch")):
        ok, err = v(_note(u.path, u.variable, hyp(bad_id, kind)), u.path, u.variable, domain, ids)
        assert ok is None and code in err, (bad_id, kind, err)


def _render(inst, note):
    _, h = t0(inst)
    g = PerspectiveGraph(recipient=inst.scenario.config.recipient, refutation_mode="fact_only")
    u = focal_units(inst)[0]
    g.instantiate(u, note, note.get("evidence_ids", []), t=0, cost=0.0)
    return notes_text(g, h, rev=7, cfg=inst.scenario.config)


def test_matched_renderer_identical_for_equal_distributions_and_no_cues():
    inst = next(i for i in INSTS if i.construction == "2a")
    u = focal_units(inst)[0]
    inferred = {"path": list(u.path), "variable": u.variable, "about": "leo_loc", "as_of_step": 0, "status": "uncertain",
                "hypotheses": [{"value": "office_c", "p": 0.5, "support": [{"evidence_id": "t0:note3", "kind": "access_inference", "note": "q"}]},
                               {"value": "office_a", "p": 0.5, "support": [{"evidence_id": "PM1", "kind": "public_model", "note": "r"}]}],
                "unresolved": ["which office"], "evidence_ids": ["t0:note3"], "rule_ids": [], "source": "inferred"}
    reference = {"path": list(u.path), "variable": u.variable, "about": "leo_loc", "as_of_step": 0, "status": "uncertain",
                 "hypotheses": [{"value": "office_a", "p": 0.5}, {"value": "office_c", "p": 0.5}],
                 "unresolved": ["Under the public model, the probability that this belief is correct now is 1.00"],
                 "evidence_ids": [], "rule_ids": [], "source": "reference"}
    a, b = _render(inst, inferred), _render(inst, reference)
    assert a == b
    for cue in ("cited evidence", "unresolved", "reference", "inferred", "privileged", "excerpt", "correct now",
                "PM1", "t0:note3", "grounded", "uncertain"):
        assert cue not in a.lower()
    assert "confidence in this estimate" in a and "low (several values remain possible)" in a
    assert "can itself be false or outdated" in a
    # canonical form: order, zero handling, rounding, duplicate values summed, `about` from the unit definition
    messy = {**reference, "about": "WRONG", "hypotheses": [{"value": "office_c", "p": 0.3}, {"value": "unknown", "p": 0.001},
                                                           {"value": "office_a", "p": 0.5}, {"value": "office_c", "p": 0.199}]}
    assert _render(inst, messy) == a.replace("office_c: 0.50", "office_c: 0.50")  # 0.499 -> 0.50; unknown omitted
    assert "WRONG" not in _render(inst, messy)
    hi = _render(inst, {**reference, "hypotheses": [{"value": "office_b", "p": 0.8}, {"value": "office_a", "p": 0.2}]})
    assert "high (one value has probability at least 0.8)" in hi
    ab = _render(inst, {**inferred, "status": "abstain"})
    assert "INFERENCE ABSTAINED" in ab and "confidence in this estimate" not in ab and "office_a: 0.50" in ab
    # a model-chosen status never changes the rendering; only the distribution does
    assert _render(inst, {**inferred, "status": "grounded"}) == a


def test_r7_prompts_have_no_design_labels():
    prompts = load_prompts("pilot-v2.2")
    banned = [r"\bdev-v3\b", r"\b[1-4][abc]\b", r"\bfocal\b", r"\brelayed\b", r"\bstale\b", r"\buninformed\b",
              r"\bdeparted\b", r"\bdistractor\b", r"\bsuperset\b"] + [rf"\b{v}\b" for v in STRATA.values()]
    for inst in INSTS:
        _, h = t0(inst)
        cfg = inst.scenario.config
        texts = [policy_messages(prompts, cfg, inst.scenario.brief, h, None, 7)[0][1]["content"]]
        texts += [unit_messages(prompts, cfg, inst.scenario.brief, h, u, "pilot-v2.2", 7)[0][1]["content"]
                  for u in focal_units(inst)]
        for t in texts:
            assert inst.instance_id not in t and PURPOSE[inst.construction] not in t
            for b in banned:
                assert not re.search(b, t), (inst.instance_id, b)


def test_v22_prompt_is_v21_plus_one_section():
    v21 = (ROOT / "prompts/pilot-v2.1/unit_system.txt").read_text(encoding="utf-8").rstrip()
    v22 = (ROOT / "prompts/pilot-v2.2/unit_system.txt").read_text(encoding="utf-8").rstrip()
    end = "Respond with JSON only, matching the schema."
    assert v22.startswith(v21[: -len(end)]) and v22.endswith(end)
    added = v22[len(v21) - len(end): -len(end)]
    assert added.strip().startswith("Public model of the task") and "warehouse" in added
