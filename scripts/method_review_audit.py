"""Method review (D-017) CPU-only symbolic audit. No model calls, no new seeds.

    python scripts/method_review_audit.py    # writes reports/method-review/audit.{json,md}

Uses only the dev-v3 base draw (seed 20261029, already-inspected development data), perm0 variants, at t0.
Strata 2 and 3 (the constructions with a handoff route; 2a/2b/3a/3b are the D-016 probe constructions).

Part 1  relationship audit under the declared public model: for every courier, the robot's marginal over the
        courier's forwarding destination (= the routing unit's typed content), the recipient's location marginal
        (= K(R)'s content), the true joint P(destination = location | h), the Frechet bounds implied by the two
        marginals alone, and the independence (product-of-marginals) reading.
Part 2  unit values J(S) over subsets of {routing units, K(R)} for three actor definitions:
        (a) Bayes over the full visible history h, notes I-projected (eps = 1): notes are functions of h, so every
            J(S) must equal V*(h) (checked numerically);
        (b) the existing grounded_typed face-value bounded actor (eps = 1e-6);
        (c) the same actor, hedged (eps = 0.25).
Part 3  a context-bounded Bayes actor: its decision context has the stratum's public process (superset model) and
        the physical observations, but NOT the prologue notices; mental information reaches it only through
        content-only note marginals (r7 shows content values only), I-projected onto its prior. Realized return is
        evaluated in the true posterior worlds. This is a symbolic check of what a representation must carry; it
        is not an LLM result.
Part 4  decision-prompt composition at t0 (characters) and measured per-episode token costs from the repair block.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds import devgen3 as G  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from vomi.oracle import GROUNDED_TYPED, ExactOracle, _normalize, _obs_key  # noqa: E402
from vomi.pilot import implication_line, ledger, load_prompts, matched_notes_text, physical_summary, task_card  # noqa: E402
from vomi.units import K, content, default_holds  # noqa: E402

OUT = ROOT / "reports" / "method-review"
TOL = 1e-9
CONSTRUCTIONS = ("2a", "2b", "2c", "3a", "3b", "3c")


def t0(scenario, hidden):
    w = scenario.build(hidden)
    return w, VisibleHistory(scenario.brief, [(None, w.reset())])


def marginal(items, f) -> dict:
    out: dict = {}
    for p, x in items:
        v = f(x)
        out[v] = out.get(v, 0.0) + p
    return {k: round(v, 10) for k, v in sorted(out.items()) if v > 1e-12}


def frechet_equal(p: dict, q: dict) -> tuple[float, float]:
    """Bounds on P(X = Y) over all couplings with marginals p, q (finite support)."""
    vals = set(p) | set(q)
    upper = sum(min(p.get(v, 0.0), q.get(v, 0.0)) for v in vals)
    lower = max(0.0, max(p.get(v, 0.0) + q.get(v, 0.0) for v in vals) - 1.0)
    return round(lower, 10), round(upper, 10)


def couriers(cfg):
    for c, (other, fact) in sorted(cfg.handoff_routes.items()):
        unit = K(c) if not other else K(c, other)
        dest = (lambda x, c=c, fact=fact: x.minds[c].beliefs.get(fact, "unknown")) if not other else \
            (lambda x, c=c, o=other, fact=fact: x.minds[c].nested.get((o, fact), "unknown"))
        yield c, unit, dest


def unit_set(inst) -> list:
    n, cfg = inst.role, inst.scenario.config
    units = [u for _, u, _ in couriers(cfg)] + [K(n["R"])]
    return sorted(set(units))


def subsets(units):
    return [frozenset(c) for r in range(len(units) + 1) for c in itertools.combinations(sorted(units), r)]


def label(S) -> str:
    return "{" + ",".join(sorted(str(u) for u in S)) + "}"


def interactions(values: dict, units) -> dict:
    out = {}
    for u, v in itertools.combinations(sorted(units), 2):
        e, a, b, ab = frozenset(), frozenset({u}), frozenset({v}), frozenset({u, v})
        out[f"I({u},{v})"] = round(values[ab] - values[a] - values[b] + values[e], 10)
    return out


# ----------------------------------------------------------------------------- Part 3: context-bounded actor
def bounded_context_values(inst, o_full: ExactOracle, units) -> dict:
    n, stakes = inst.role, inst.variant.stakes
    ss = G.superset_scenario(inst.spec, n, stakes, strip_notices=True)
    truth = (("pattern", f"{inst.construction}:0"),) + inst.hidden
    _, hs = t0(ss, truth)
    ao = ExactOracle(ss, hs)  # the actor's own model: worlds consistent with the stripped t0 observation
    prior = [p for p, _ in ao.belief]
    res = {"actor_model_worlds": len(ao.worlds),
           "actor_patterns": sorted({dict(p)["pattern"] for p in ao.params}), "J": {}, "first_actions": {},
           "projection_residual": {}, "failures": {}}
    for S in subsets(units):
        targets = {u: marginal(o_full.belief, lambda x, u=u: content(x, u)[0]) for u in S}
        cells = {u: [content(x, u)[0] for x in ao.worlds] for u in S}
        wts, worst = list(prior), 0.0
        feasible = all(all(any(c == v for c in cells[u]) for v in targets[u]) for u in S)
        if feasible:
            for _ in range(2000):
                worst = 0.0
                for u in S:
                    tot = sum(wts)
                    cur: dict = {}
                    for wt, c in zip(wts, cells[u]):
                        cur[c] = cur.get(c, 0.0) + wt / tot
                    worst = max(worst, max(abs(cur.get(c, 0.0) - targets[u].get(c, 0.0)) for c in set(cur) | set(targets[u])))
                    wts = [wt * targets[u].get(c, 0.0) / cur[c] if cur[c] > 0 else 0.0 for wt, c in zip(wts, cells[u])]
                if worst < 1e-13:
                    break
        res["projection_residual"][label(S)] = worst if feasible else None
        if not feasible or sum(wts) <= 0:
            res["failures"][label(S)] = "note value outside the actor's support"
            continue
        items0 = _normalize([(wt, x) for wt, x in zip(wts, ao.worlds) if wt > 0])
        total, firsts, fail, traces = 0.0, {}, 0, []
        for p, w in o_full.belief:
            world, obs, items, ret = w.clone(), o_full.obs, items0, 0.0
            first, acts = None, []
            while not obs.done:
                a = ao.best_action(items, obs)
                first = first or str(a)
                obs = world.step(a)
                acts.append(str(a) + (f"->{obs.outcome}" if obs.outcome else ""))
                ret += obs.reward
                nxt = ao._transition(items, a).get(_obs_key(obs))
                if nxt is None:  # the actor assigned zero probability to what happened
                    fail += 1
                    items = items  # keep acting on the old belief (recorded)
                else:
                    items = _normalize(nxt[1])
            total += p * ret
            firsts[first] = firsts.get(first, 0.0) + p
            traces.append({"p": round(p, 10), "actions": acts, "return": round(ret, 10)})
        res["J"][label(S)] = round(total, 10)
        res.setdefault("traces", {})[label(S)] = traces
        res["first_actions"][label(S)] = {k: round(v, 10) for k, v in sorted(firsts.items())}
        if fail:
            res["failures"][label(S)] = f"{fail} zero-probability observation(s)"
    vals = {S: res["J"][label(S)] for S in subsets(units) if label(S) in res["J"]}
    res["interactions"] = interactions(vals, units) if len(vals) == 2 ** len(units) else "incomplete"
    return res


# ----------------------------------------------------------------------------- per instance
def record(inst) -> dict:
    sc, n = inst.scenario, inst.role
    cfg, R = sc.config, sc.config.recipient
    w, h = t0(sc, inst.hidden)
    o = ExactOracle(sc, h)
    qs = {str(a): round(q, 10) for a, q in o.ranked_actions(o.belief, o.obs)}
    vstar = max(qs.values())
    loc = marginal(o.belief, lambda x: x.people_rooms[R])
    rec = {"instance_id": inst.instance_id, "construction": inst.construction, "stakes": inst.variant.stakes,
           "roles": {k: v for k, v in sorted(n.items())}, "consistent_worlds": len(o.worlds),
           "bayes_v_t0": vstar, "bayes_optimal_first": sorted(a for a, q in qs.items() if q >= vstar - TOL),
           "q_t0": qs, "recipient_location_marginal": loc, "couriers": []}
    kr = K(R)
    kr_m = marginal(o.belief, lambda x: content(x, kr)[0])
    rec["K(R)_content_marginal"] = kr_m
    rec["K(R)_equals_location_everywhere"] = all(content(x, kr)[0] == x.people_rooms[R] for x in o.worlds)
    for c, u, dest in couriers(cfg):
        dm = marginal(o.belief, dest)
        um = marginal(o.belief, lambda x, u=u: content(x, u)[0])
        lo, hi = frechet_equal(dm, loc)
        p_succ = round(sum(p for p, x in o.belief if dest(x) == x.people_rooms[R]), 10)
        p_holds = round(sum(p for p, x in o.belief if default_holds(x, u)), 10)  # the typed record's second field
        give = f"give({c})"
        rec["couriers"].append({
            "courier": c, "routing_unit": str(u), "present_at_t0": give in qs,
            "routing_unit_marginal": um, "destination_marginal": dm, "unit_equals_destination": um == dm,
            "robot_destination_confidence": max(dm.values()),
            "person_holds_categorical_value_everywhere": all(dest(x) != "unknown" for x in o.worlds),
            "p_success_true_joint": p_succ, "typed_p_default_holds": p_holds,
            "default_holds_equals_success": abs(p_holds - p_succ) < 1e-9, "frechet_from_marginals": [lo, hi],
            "marginals_determine_success": abs(hi - lo) < 1e-9,
            "independence_reading": round(sum(dm.get(v, 0) * loc.get(v, 0) for v in dm), 10),
            "q_give": qs.get(give)})
    units = unit_set(inst)
    rec["units"] = [str(u) for u in units]
    part2 = {}
    for name, eps, testimony in (("bayes_full_history_eps1", 1.0, "face_value"),
                                 ("grounded_typed_face_value", None, "face_value"),
                                 ("grounded_typed_hedged", None, "hedged")):
        oo = ExactOracle(sc, h, testimony=testimony)
        if eps is not None:
            oo.eps = eps
        vals = oo.subset_values(units, record=GROUNDED_TYPED)
        part2[name] = {"J": {label(S): round(v, 10) for S, v in vals.items()},
                       "max_abs_J_minus_Vstar": round(max(abs(v - vstar) for v in vals.values()), 10),
                       "interactions": interactions(vals, units),
                       "first_action_empty": sorted({str(a) for a in oo.evaluate(frozenset(), record=GROUNDED_TYPED).actions})}
    rec["unit_values"] = part2
    rec["bounded_context_actor"] = bounded_context_values(inst, o, units)
    return rec


# ----------------------------------------------------------------------------- Part 4: prompt composition
def prompt_composition(inst) -> dict:
    sc = inst.scenario
    cfg = sc.config
    w, h = t0(sc, inst.hidden)
    o = ExactOracle(sc, h)
    view = []
    for _, u, _ in couriers(cfg):
        m = marginal(o.belief, lambda x, u=u: content(x, u)[0])
        view.append({"unit": str(u), "as_of": 0, "status": "fresh",
                     "output": {"hypotheses": [{"value": v, "p": p} for v, p in m.items()]}})
    prompts = load_prompts("pilot-v2.2")
    parts = {"policy_system": prompts.get("policy_system", ""), "task_card_incl_public_model": task_card(cfg, sc.brief, 7),
             "history_ledger": ledger(h)[0], "physical_summary": physical_summary(h),
             "reference_notes_content_only": matched_notes_text(view, cfg),
             "reference_notes_with_implication": matched_notes_text(view, cfg, implication=True)}
    return {"instance_id": inst.instance_id, "chars": {k: len(v) for k, v in parts.items()},
            "history_ledger_text": parts["history_ledger"], "notes_text": parts["reference_notes_with_implication"]}


def repair_compute() -> dict:
    d = json.loads((ROOT / "reports/repair-block/stage2-results.json").read_text(encoding="utf-8"))["compute"]
    out = {}
    for arm in ("none", "reference", "inferred"):
        v = d[arm]
        e = v["episodes"]
        row = {"episodes": e, "decision_calls_per_episode": v["decision_attempts"] / e,
               "decision_prompt_tokens_per_episode": v["decision_prompt_tokens"] / e,
               "decision_completion_tokens_per_episode": v["decision_completion_tokens"] / e,
               "decision_reasoning_tokens_per_episode": v["decision_reasoning_tokens"] / e,
               "decision_prompt_tokens_per_call": v["decision_prompt_tokens"] / v["decision_attempts"],
               "decision_completion_tokens_per_call": v["decision_completion_tokens"] / v["decision_attempts"]}
        if "note_attempts" in v:
            row.update({"note_attempts": v["note_attempts"],
                        "note_prompt_tokens_per_attempt": v["note_prompt_tokens"] / v["note_attempts"],
                        "note_completion_tokens_per_attempt": v["note_completion_tokens"] / v["note_attempts"],
                        "note_reasoning_tokens_per_attempt": v["note_reasoning_tokens"] / v["note_attempts"]})
        out[arm] = {k: round(x, 1) for k, x in row.items()}
    return out


# ----------------------------------------------------------------------------- report
def fmt_m(m: dict) -> str:
    return ", ".join(f"{k} {v:.2f}" for k, v in m.items())


def write_md(res: dict) -> str:
    L = ["# Method review: CPU-only symbolic audit (development data; no model calls)", "",
         f"Generated by `scripts/method_review_audit.py` at commit `{res['commit']}`"
         f"{' (dirty tree)' if res['dirty'] else ''}. Seed: dev-v3 base draw 20261029 (already-inspected development "
         "data), perm0 variants, t0. Exact enumeration under the declared public model; nothing here is an LLM "
         "result.", "",
         "## Part 1: what the forwarding decision depends on", "",
         "give(c) succeeds iff c's forwarding destination equals the recipient's location. The routing unit's typed "
         "content IS the robot's marginal over that destination; K(R)'s content equals the recipient's location in "
         "every world. The success probability is a property of their JOINT distribution.", "",
         "| construction | courier (unit) | robot's destination marginal | recipient location marginal | robot confidence in destination | P(success) true joint | bounds from the two marginals | independence reading | Q*(give) | V*(h) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["records"]:
        if r["stakes"] != 1.0:
            continue
        for c in r["couriers"]:
            L.append(f"| {r['construction']} | {c['courier']} ({c['routing_unit']}){'' if c['present_at_t0'] else ' — absent'} | "
                     f"{fmt_m(c['destination_marginal'])} | {fmt_m(r['recipient_location_marginal'])} | "
                     f"{c['robot_destination_confidence']:.2f} | **{c['p_success_true_joint']:.2f}** | "
                     f"[{c['frechet_from_marginals'][0]:.2f}, {c['frechet_from_marginals'][1]:.2f}] | "
                     f"{c['independence_reading']:.2f} | {c['q_give'] if c['q_give'] is not None else '—'} | {r['bayes_v_t0']:.3f} |")
    L += ["", "Checks: routing-unit content equals the destination marginal in every row: "
          f"**{res['checks']['unit_equals_destination_all']}**; K(R) content equals the location in every world: "
          f"**{res['checks']['kr_equals_location_all']}**; every courier holds a categorical value in every world "
          f"(the person is never uncertain; only the robot is): **{res['checks']['person_categorical_all']}**; the typed "
          "record's P(default holds) for the routing unit equals P(success of give) in every row: "
          f"**{res['checks']['typed_default_holds_equals_give_success_all']}**.", "",
          "## Part 2: unit values J(S) at t0 (stakes x1 and x4)", "",
          "| construction | stakes | actor | J(∅) | max over S of abs(J(S) − V*) | interactions I(u,v) |", "|---|---|---|---|---|---|"]
    for r in res["records"]:
        for name, v in r["unit_values"].items():
            inter = "; ".join(f"{k} = {x:+.3f}" for k, x in v["interactions"].items() if abs(x) > 1e-9) or "all 0"
            L.append(f"| {r['construction']} | x{r['stakes']:g} | {name} | {v['J']['{}']:.3f} | "
                     f"{v['max_abs_J_minus_Vstar']:.3f} | {inter} |")
    L += ["", "## Part 3: context-bounded Bayes actor (no prologue notices in its decision context; content-only notes)", "",
          "| construction | stakes | V*(full h) | subset values J_B(S) | interactions | first action under the best set | failures |",
          "|---|---|---|---|---|---|---|"]
    for r in res["records"]:
        b = r["bounded_context_actor"]
        js = "; ".join(f"{k} {v:.3f}" for k, v in b["J"].items())
        inter = ("; ".join(f"{k} = {x:+.3f}" for k, x in b["interactions"].items())
                 if isinstance(b["interactions"], dict) else b["interactions"])
        best = max(b["J"], key=b["J"].get) if b["J"] else None
        fa = fmt_m(b["first_actions"][best]) if best else "—"
        L.append(f"| {r['construction']} | x{r['stakes']:g} | {r['bayes_v_t0']:.3f} | {js} | {inter} | {best}: {fa} | "
                 f"{'; '.join(f'{k}: {v}' for k, v in b['failures'].items()) or 'none'} |")
    L += ["", "## Part 4: decision-prompt composition at t0 (characters) and measured token costs", "",
          "| instance | " + " | ".join(res["prompt_composition"][0]["chars"]) + " |",
          "|---|" + "---|" * len(res["prompt_composition"][0]["chars"])]
    for p in res["prompt_composition"]:
        L.append(f"| {p['instance_id']} | " + " | ".join(str(v) for v in p["chars"].values()) + " |")
    L += ["", "Measured per-episode costs (repair block Stage 2, local gpt-oss-20b, 1,152 episodes per arm):", "",
          "| arm | decision calls/ep | decision prompt tok/ep | decision completion tok/ep | prompt tok/call | note prompt tok/attempt | note completion tok/attempt |",
          "|---|---|---|---|---|---|---|"]
    for arm, v in res["repair_compute"].items():
        L.append(f"| {arm} | {v['decision_calls_per_episode']} | {v['decision_prompt_tokens_per_episode']} | "
                 f"{v['decision_completion_tokens_per_episode']} | {v['decision_prompt_tokens_per_call']} | "
                 f"{v.get('note_prompt_tokens_per_attempt', '—')} | {v.get('note_completion_tokens_per_attempt', '—')} |")
    L += ["", f"Runtime: {res['seconds']} s CPU wall clock."]
    return "\n".join(L) + "\n"


def main():
    t = time.monotonic()
    insts = [i for i in G.generate(G.BASE_SEED) if i.construction in CONSTRUCTIONS and not i.variant.permuted]
    records = [record(i) for i in insts]
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, capture_output=True, text=True).stdout.strip())
    cs = [c for r in records for c in r["couriers"]]
    res = {"commit": commit, "dirty": dirty, "seed": G.BASE_SEED, "constructions": CONSTRUCTIONS,
           "checks": {"unit_equals_destination_all": all(c["unit_equals_destination"] for c in cs),
                      "kr_equals_location_all": all(r["K(R)_equals_location_everywhere"] for r in records),
                      "person_categorical_all": all(c["person_holds_categorical_value_everywhere"] for c in cs),
                      "typed_default_holds_equals_give_success_all": all(c["default_holds_equals_success"] for c in cs),
                      "bayes_eps1_all_J_equal_Vstar": all(r["unit_values"]["bayes_full_history_eps1"]["max_abs_J_minus_Vstar"] < 1e-9
                                                          for r in records)},
           "records": records,
           "prompt_composition": [prompt_composition(i) for i in insts if i.variant.stakes == 1.0],
           "repair_compute": repair_compute()}
    res["seconds"] = round(time.monotonic() - t, 2)
    OUT.mkdir(parents=True, exist_ok=True)
    js = json.dumps(res, indent=1, sort_keys=False, default=str) + "\n"
    (OUT / "audit.json").write_bytes(js.encode("utf-8"))
    (OUT / "audit.md").write_bytes(write_md(res).encode("utf-8"))
    print(json.dumps(res["checks"]), res["seconds"], "s", hashlib.sha256(js.encode()).hexdigest()[:12])


if __name__ == "__main__":
    main()
