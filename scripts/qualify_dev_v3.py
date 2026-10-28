"""dev-v3 Round A qualification (reports/dev-v3-block/experiment-plan.md, Entry 1 A.3 + Entry 1a). Symbolic only.

    python3 scripts/qualify_dev_v3.py            # writes reports/dev-v3-block/qualification.{json,md}
    python3 scripts/qualify_dev_v3.py --freeze   # also writes reports/dev-v3-block/dev-v3-freeze.json

Every value is exact under the declared public model: ExactOracle's plain posterior b_h over the group prior
conditioned on the visible t0 history, with belief-space expectimax and every legal action (ask, move/search, drop,
give, deliver, wait). These are symbolic references for an ideal Bayes actor, not LLM values. Privileged quantities
(true content revealed) are labeled as such.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds import devgen3 as G  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.scenarios import Scenario  # noqa: E402
from officeminds.world import legal_actions  # noqa: E402
from vomi.oracle import PRIVILEGED_BAYES, ExactOracle  # noqa: E402
from vomi.pilot import (PEOPLE_RULES_R6, load_prompts, policy_messages, prompt_hashes, task_card,  # noqa: E402
                        unit_messages)
from vomi.units import K, R as Rel, content, default_holds, generate_candidates  # noqa: E402

OUT = ROOT / "reports" / "dev-v3-block"
TOL = 1e-9
FAMILY = {"ask": "ask", "move": "move", "drop": "chute", "give": "handoff", "deliver": "deliver", "wait": "wait"}


def t0(scenario: Scenario, hidden):
    w = scenario.build(hidden)
    return w, VisibleHistory(scenario.brief, [(None, w.reset())])


def q_table(o: ExactOracle) -> dict[str, float]:
    return {str(a): round(q, 10) for a, q in o.ranked_actions(o.belief, o.obs)}


def opt_set(qs: dict[str, float]) -> list[str]:
    best = max(qs.values())
    return sorted(a for a, q in qs.items() if q >= best - TOL)


def families(qs):
    out = {}
    for a, q in qs.items():
        f = FAMILY[a.split("(")[0]]
        out[f] = max(out.get(f, -9), q)
    return out


def unit_posterior(o: ExactOracle, u):
    dist, correct = {}, 0.0
    for p, w in o.belief:
        v = content(w, u)[0]
        dist[v] = dist.get(v, 0.0) + p
        correct += p * default_holds(w, u)
    return {k: round(v, 10) for k, v in sorted(dist.items())}, round(correct, 10)


def stripped(scenario: Scenario) -> Scenario:
    def build(p):
        w = scenario.build(p)
        w.timed_events = tuple(replace(e, visible_as=None) for e in w.timed_events)
        return w
    return Scenario(scenario.id + "-cardonly", scenario.brief, "card-only", scenario.prior, build)


def with_chute(scenario: Scenario) -> Scenario:
    def build(p):
        w = scenario.build(p)
        w.config = replace(w.config, chute_room="lobby")
        return w
    return Scenario(scenario.id + "-chute", scenario.brief, "with-chute counterfactual", scenario.prior, build)


def all_shallow_units(world):
    people = sorted(world.minds)
    return [u for j in people for u in (K(j), Rel(j))]


def instance_record(inst) -> dict:
    sc = inst.scenario
    t = time.monotonic()
    w, h = t0(sc, inst.hidden)
    o = ExactOracle(sc, h)
    qs = q_table(o)
    rec = {"instance_id": inst.instance_id, "group_id": inst.group_id, "stratum": inst.stratum,
           "construction": inst.construction, "distractor": inst.distractor, "stakes": inst.variant.stakes,
           "permuted": inst.variant.permuted, "hypothesis_worlds_consistent": len(o.worlds),
           "prior_worlds": len(sc.prior), "q_first_actions": qs, "optimal_first_actions": opt_set(qs),
           "bayes_value_t0": max(qs.values()), "best_by_family": families(qs), "focal": []}
    for u in G.focal_units(inst):
        dist, correct = unit_posterior(o, u)
        ur = o.unit_report(u, record=PRIVILEGED_BAYES)  # PRIVILEGED: true content revealed to the Bayes actor
        rec["focal"].append({
            "unit": str(u), "self_location": u.depth == 1 and u.path[0] == sc.config.recipient,
            "reference_content_posterior": dist, "reference_p_correct_now": correct,
            "access_status_set": sorted({G.access_status(x, u) for x in o.worlds}),
            "privileged_true_content": list(content(w, u)), "privileged_true_correct": default_holds(w, u),
            "privileged_bayes_delta_j": round(ur.delta_j, 10), "privileged_p_flip": round(ur.p_flip, 10),
            "content_entropy_bits": round(ur.content_entropy_bits, 10)})
    cands = generate_candidates(sc.config, h)
    rec["candidates"] = [str(u) for u in cands]
    rec["self_location_candidates"] = [str(u) for u in cands if u.depth == 1 and u.path[0] == sc.config.recipient]
    rec["focal_in_candidates"] = all(str(u) in rec["candidates"] for u in G.focal_units(inst))
    # card-only triviality (R1b): the construction prior with every prologue notice removed
    co = ExactOracle(stripped(sc), t0(stripped(sc), inst.hidden)[1])
    rec["card_only_optimal"] = opt_set(q_table(co))
    rec["card_only_fixes_best_action"] = rec["card_only_optimal"] == rec["optimal_first_actions"]
    if inst.stratum in (2, 3):  # superset public model (R1a) and its card-only version
        n = inst.role
        ss = G.superset_scenario(inst.spec, n, inst.variant.stakes)
        truth = (("pattern", f"{inst.construction}:0"),) + inst.hidden
        so = ExactOracle(ss, t0(ss, truth)[1])
        sq = q_table(so)
        diffs = [abs(sq[a] - qs[a]) for a in qs] + [abs(len(sq) - len(qs))]
        post = {str(u): unit_posterior(so, u) for u in G.focal_units(inst)}
        rec["superset"] = {
            "patterns": len(G.SUPERSET_PATTERNS[inst.stratum]), "prior_worlds": len(ss.prior),
            "consistent_worlds": len(so.worlds),
            "consistent_patterns": sorted({dict(p)["pattern"] for p in so.params}),
            "max_abs_q_diff": max(diffs),
            "focal_posterior_equal": all(post[f["unit"]][0] == f["reference_content_posterior"]
                                         and abs(post[f["unit"]][1] - f["reference_p_correct_now"]) < TOL
                                         for f in rec["focal"])}
        sco = ExactOracle(stripped(ss), t0(stripped(ss), truth)[1])
        rec["superset"]["card_only_optimal"] = opt_set(q_table(sco))
        rec["superset"]["card_only_fixes_best_action"] = rec["superset"]["card_only_optimal"] == rec["optimal_first_actions"]
    if inst.stratum == 3:
        ch = with_chute(sc)
        cq = q_table(ExactOracle(ch, t0(ch, inst.hidden)[1]))
        rec["with_chute_counterfactual"] = {"optimal": opt_set(cq), "value": max(cq.values()),
                                            "best_by_family": families(cq)}
    rec["oracle_seconds"] = round(time.monotonic() - t, 3)
    return rec


def pair(spec, n, stakes, hidden, pa, pb, kind):
    """Two patterns of one superset (shared names, labels, distractor and hidden draw)."""
    ss = G.superset_scenario(spec, n, stakes)
    res = {"kind": kind, "patterns": [pa, pb], "group_spec": spec.group_id}
    worlds = {}
    for pat in (pa, pb):
        truth = (("pattern", pat),) + hidden
        w, h = t0(ss, truth)
        o = ExactOracle(ss, h)
        qs = q_table(o)
        worlds[pat] = w
        res[pat] = {"optimal": opt_set(qs), "value": max(qs.values()), "q": qs,
                    "rooms": dict(sorted(w.people_rooms.items()))}
    res["same_physical_state"] = worlds[pa].people_rooms == worlds[pb].people_rooms
    res["optimal_sets_differ"] = res[pa]["optimal"] != res[pb]["optimal"]
    best_a = res[pa]["optimal"][0]
    res["gap_if_a_best_used_in_b"] = (round(res[pb]["value"] - res[pb]["q"][best_a], 10) if best_a in res[pb]["q"]
                                      else "n/a: action illegal in b")
    if spec.stratum == 3:  # R3: depth certification relative to the shallow class
        wa, wb = worlds[pa], worlds[pb]
        res["pi_le1_inputs_equal"] = (
            all(content(wa, u) == content(wb, u) for u in all_shallow_units(wa))
            and t0(ss, (("pattern", pa),) + hidden)[1].last.people_present
            == t0(ss, (("pattern", pb),) + hidden)[1].last.people_present)
        res["depth2_contents"] = {
            pat: {str(u): list(content(worlds[pat], u)) for u in
                  (K(n["F"], n["R"]), K(n["R"], n["F"]), K(n["A"], n["R"]), K(n["F"]), K(n["R"]))}
            for pat in (pa, pb)}
    return res


def pairs(insts):
    by = {(i.construction, i.variant.stakes, i.variant.permuted): i for i in insts}
    out = []
    i2a = by[("2a", 1.0, False)]
    out.append(pair(i2a.spec, i2a.role, 1.0, i2a.hidden, "2a:0", "2a:1", "same-physical-state social pair (holder swap)"))
    out.append(pair(i2a.spec, i2a.role, 1.0, i2a.hidden, "2a:0", "2b:0", "physical availability contrast (H departed)"))
    i3a = by[("3a", 1.0, False)]
    out.append(pair(i3a.spec, i3a.role, 1.0, i3a.hidden, "3a:0", "3b:0", "same-physical-state social pair (depth-2)"))
    out.append(pair(i3a.spec, i3a.role, 1.0, i3a.hidden, "3a:0", "3c:0",
                    "same courier belief, different recipient belief (not same physical state)"))
    stakes = []
    for c in ("4a", "4b", "4c"):
        a, b = by[(c, 1.0, False)], by[(c, 4.0, False)]
        qa, qb = (q_table(ExactOracle(x.scenario, t0(x.scenario, x.hidden)[1])) for x in (a, b))
        stakes.append({"construction": c, "rates": {k: float(v) for k, v in a.spec.rates},
                       "x1": {"optimal": opt_set(qa), "q": qa}, "x4": {"optimal": opt_set(qb), "q": qb},
                       "flip": opt_set(qa) != opt_set(qb)})
    return out, stakes


def round_b_selection():
    return {f"stratum{s}": G.CONSTRUCTIONS[s][int(hashlib.sha256(f"dev-v3:roundB:stratum{s}".encode()).hexdigest(), 16) % 3]
            for s in (1, 2, 3, 4)}


def sha_text(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def sha_file(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def write_md(q, path):
    L = ["# dev-v3 Round A qualification (symbolic, exact; no LLM)", "",
         f"Generated by `scripts/qualify_dev_v3.py` at commit `{q['git_commit'][:10]}`"
         f"{' (dirty)' if q['dirty_paths'] else ''}. Values are exact Bayes (plain posterior, asks legal) under each "
         "group's declared public model. Privileged columns reveal true content.", "",
         "## Instances (stakes ×1, unpermuted; all 48 in qualification.json)", "",
         "| group | distr. | worlds | optimal first action(s) | V* | best first ask / move / drop / give (any continuation) | focal: reference P(content), P(correct) | privileged ex-ante ΔJ | card-only fixes? | superset ok |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in q["instances"]:
        if r["stakes"] != 1.0 or r["permuted"]:
            continue
        fam = r["best_by_family"]
        fams = " / ".join(f"{fam.get(k, float('nan')):.3f}" if k in fam else "–" for k in ("ask", "move", "chute", "handoff"))
        foc = "; ".join(f"{f['unit']}: {f['reference_content_posterior']}, {f['reference_p_correct_now']:.2f}" for f in r["focal"])
        dj = "; ".join(f"{f['privileged_bayes_delta_j']:+.3f}" for f in r["focal"])
        ss = r.get("superset")
        sso = "–" if not ss else ("yes" if ss["max_abs_q_diff"] < TOL and ss["focal_posterior_equal"] else "NO")
        co = ("yes" if r["card_only_fixes_best_action"] else "no") + (
            f" (superset: {'yes' if ss['card_only_fixes_best_action'] else 'no'})" if ss else "")
        L.append(f"| {r['construction']} | {r['distractor']} | {r['hypothesis_worlds_consistent']} | "
                 f"{', '.join(r['optimal_first_actions'])} | {r['bayes_value_t0']:.3f} | {fams} | {foc} | {dj} | {co} | {sso} |")
    L += ["", "## Pairs (shared names, labels and hidden draw)", ""]
    for p in q["pairs"]:
        a, b = p["patterns"]
        L.append(f"- **{p['kind']}** ({p['group_spec']}: {a} vs {b}): same physical state: {p['same_physical_state']}; "
                 f"optimal {p[a]['optimal']} ({p[a]['value']:.3f}) vs {p[b]['optimal']} ({p[b]['value']:.3f}); "
                 f"loss of using {a}'s best action in {b}: {p['gap_if_a_best_used_in_b']}"
                 + (f"; Π≤1 inputs equal: {p['pi_le1_inputs_equal']}; depth-2 contents: {p['depth2_contents']}"
                    if "pi_le1_inputs_equal" in p else ""))
    L += ["", "## Stakes pairs (stratum 4)", ""]
    for s in q["stakes_pairs"]:
        L.append(f"- {s['construction']} rates {s['rates']}: ×1 {s['x1']['optimal']} vs ×4 {s['x4']['optimal']}; "
                 f"flip: {s['flip']}")
    L += ["", "## With-chute counterfactual (stratum 3)", ""]
    for r in q["instances"]:
        if r["stratum"] == 3 and r["stakes"] == 1.0 and not r["permuted"]:
            c = r["with_chute_counterfactual"]
            L.append(f"- {r['construction']}: as built {r['optimal_first_actions']} ({r['bayes_value_t0']:.3f}); "
                     f"with a chute {c['optimal']} ({c['value']:.3f})")
    L += ["", "## Reading notes (Entry 1b)", "",
          "- Card-only 'fixes?' = the Bayes optimal first-action set with every prologue notice removed equals the full "
          "optimal set. Under the construction-specific prior this can hold because that prior encodes the role pattern "
          "(not disclosed by the card text); under the card-consistent superset prior (strata 2-3) no group is fixed. "
          "Set equality does not detect containment.",
          "- Stratum-3 superset: 3 patterns without an A<->F swap (the courier is named publicly, so a swap would change "
          "the public action set). Stratum 2: 6 patterns (H<->N swap; both are couriers).",
          "- Strata 1-3 labels and the 3a/3b Pi<=1 certification are evidence-resolved GIVEN the declared rules (everyone "
          "cooperative; quiet-conversation content; rule 5 bystander clause; rule 2 lobby-sighting clause), not without them.",
          "- 'move' includes walking back to the lobby; privileged ΔJ is ex-ante (expected over the posterior)."]
    L += ["", "## Checks", ""] + [f"- {k}: {v}" for k, v in q["checks"].items()]
    L += ["", f"Round B selection: {q['round_b_selection']}", ""]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", action="store_true")
    args = ap.parse_args()
    insts = G.generate()
    head = os.popen(f'git -C "{ROOT}" rev-parse HEAD').read().strip()
    dirty = [x for x in os.popen(f'git -C "{ROOT}" status --porcelain').read().split("\n") if x.strip()]
    recs = [instance_record(i) for i in insts]
    prs, stakes = pairs(insts)
    by_id = {r["instance_id"]: r for r in recs}
    checks = {
        "instances": len(recs), "groups": len({r["group_id"] for r in recs}),
        "superset_q_and_posterior_match_all": all(r["superset"]["max_abs_q_diff"] < TOL and r["superset"]["focal_posterior_equal"]
                                                  for r in recs if "superset" in r),
        "evidence_resolved_access_status_unique_strata_1_3": all(len(f["access_status_set"]) == 1 for r in recs
                                                                if r["stratum"] < 4 for f in r["focal"]),
        "stratum4_stakes_flip_all": all(s["flip"] for s in stakes),
        "focal_units_in_visible_candidates_all": all(r["focal_in_candidates"] for r in recs),
        "permuted_variant_same_optimal_value": all(
            abs(by_id[r["instance_id"]]["bayes_value_t0"] - by_id[r["instance_id"].replace("perm0", "perm1")]["bayes_value_t0"]) < TOL
            for r in recs if not r["permuted"]),
        "card_only_fixes_best_action": sorted(r["instance_id"] for r in recs if r["card_only_fixes_best_action"]),
        "superset_card_only_fixes_best_action": sorted(r["instance_id"] for r in recs
                                                       if r.get("superset", {}).get("card_only_fixes_best_action")),
        "self_location_candidates_present": sorted({r["instance_id"] for r in recs if r["self_location_candidates"]}),
        "max_oracle_seconds": max(r["oracle_seconds"] for r in recs),
    }
    q = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "git_commit": head, "dirty_paths": dirty,
         "instances": recs, "pairs": prs, "stakes_pairs": stakes, "checks": checks,
         "round_b_selection": round_b_selection()}
    (OUT / "qualification.json").write_text(json.dumps(q, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    write_md(q, OUT / "qualification.md")
    print(json.dumps(checks, indent=1))
    if args.freeze:
        freeze(insts, q)


def freeze(insts, q):
    prompts = load_prompts("pilot-v2.1")
    inst_rows = {}
    for inst in insts:
        w, h = t0(inst.scenario, inst.hidden)
        cfg = inst.scenario.config
        card = task_card(cfg, inst.scenario.brief, rev=6)
        pol = policy_messages(prompts, cfg, inst.scenario.brief, h, None, 6)[0][1]["content"]
        inst_rows[inst.instance_id] = {
            "group_id": inst.group_id, "stratum": inst.stratum, "construction": inst.construction,
            "distractor": inst.distractor, "variant": inst.variant.tag, "hidden_sha256": sha_text(json.dumps(inst.hidden)),
            "agent_view_t0_sha256": sha_text(json.dumps(h.to_agent_dict(), sort_keys=True)),
            "card_sha256": sha_text(card), "public_model_sha256": sha_text(cfg.public_model),
            "policy_prompt_t0_direct_sha256": sha_text(pol),
            "focal_units": [str(u) for u in G.focal_units(inst)],
            "unit_prompt_sha256": {str(u): sha_text(unit_messages(prompts, cfg, inst.scenario.brief, h, u, "pilot-v2.1", 6)[0][1]["content"])
                                   for u in G.focal_units(inst)}}
    src = ["src/officeminds/devgen3.py", "src/officeminds/world.py", "src/officeminds/scenarios.py",
           "src/officeminds/episode.py", "src/vomi/oracle.py", "src/vomi/units.py", "src/vomi/pilot.py",
           "src/vomi/fidelity.py", "src/vomi/unit_schema.py", "src/vomi/graph.py", "src/vomi/clients.py",
           "scripts/qualify_dev_v3.py", "scripts/run_dev_v3_notes.py", "scripts/report_dev_v3.py",
           "prompts/pilot-v1/policy_system.txt", "prompts/pilot-v2.1/unit_system.txt"]
    model = json.loads((ROOT / "configs" / "models" / "local_gpt_oss_20b.json").read_text())
    fz = {"version": G.DEV_VERSION, "base_seed": G.BASE_SEED, "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
          "git_commit": q["git_commit"], "dirty_paths": q["dirty_paths"],
          "source_sha256": {f: sha_file(f) for f in src}, "people_rules_r6_sha256": sha_text(PEOPLE_RULES_R6),
          "prompt_sha256": prompt_hashes("pilot-v2.1"), "render_revision": 6, "package": "pilot-v2.1",
          "strata": G.STRATA, "constructions": G.CONSTRUCTIONS, "distractor_rule": "LEVELS[(g + stratum) % 3]",
          "round_b_selection": q["round_b_selection"],
          "round_b_model": {"config": "configs/models/local_gpt_oss_20b.json", "model": model["model"],
                            "hf_snapshot": model["hf_snapshot"], "notes_decoding": model["decoding"],
                            "policy_decoding": {**model["decoding"], "temperature": 1.0}},
          "qualification_sha256": sha_file("reports/dev-v3-block/qualification.json"),
          "instances": inst_rows}
    (OUT / "dev-v3-freeze.json").write_text(json.dumps(fz, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("freeze written", OUT / "dev-v3-freeze.json")


if __name__ == "__main__":
    main()
