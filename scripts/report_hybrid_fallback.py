"""Hybrid block (D-019) fallback analysis, pre-declared in reports/hybrid-block/fallback-protocol.md.

    python3 scripts/report_hybrid_fallback.py RUN_DIR     # writes reports/hybrid-block/fallback-results.{json,md}
"""

from __future__ import annotations

import json
import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds import devgen3 as G  # noqa: E402
from officeminds.world import Action  # noqa: E402

OUT = ROOT / "reports" / "hybrid-block"
CONDS = ("direct", "checker_gate", "generic_gate", "ask_first")
B = 10_000


def parse(s: str) -> Action:
    m = re.match(r"(\w+)\((\w*)(?:,(\w+))?\)", s)
    return Action(m[1], m[2] or "", m[3] or "")


def tokens(e) -> int:
    return sum(u["prompt_tokens"] + u["completion_tokens"] for u in e["usage"].values())


def calls(e) -> int:
    return sum(u["attempts"] for u in e["usage"].values())


def commit_class(con: str, a: Action) -> str:
    return "social_belief" if a.kind == "give" else ("testimony_reliability" if con in ("4b", "4c") else "physical")


def unit_means(eps, key):
    units = {}
    for e in eps:
        units.setdefault((e["base"], e["condition"]), []).append(key(e))
    return {k: statistics.mean(v) for k, v in units.items()}


def paired(eps, a, b, key):
    """Per-base-scenario paired difference a - b with a construction-stratified bootstrap CI."""
    m = unit_means(eps, key)
    bases = sorted({e["base"] for e in eps if (e["base"], a) in m and (e["base"], b) in m})
    d = {u: m[(u, a)] - m[(u, b)] for u in bases}
    strata = {}
    for u in bases:
        strata.setdefault(u.split("-", 1)[1], []).append(u)
    rng = random.Random(0)
    boots = []
    for _ in range(B):
        s = [d[rng.choice(us)] for us in strata.values() for _ in us]
        boots.append(statistics.mean(s))
    boots.sort()
    return {"mean": round(statistics.mean(d.values()), 4), "ci95": [round(boots[int(0.025 * B)], 4),
                                                                  round(boots[int(0.975 * B) - 1], 4)],
            "units": len(bases)}


def replay_vetoes(eps):
    """EVALUATION ONLY: would each vetoed proposal have failed? (replay with the hidden draw)."""
    insts = {}
    for seed in sorted({e["seed"] for e in eps}):
        for inst in G.generate(seed):
            insts[f"s{seed}-{inst.instance_id}"] = inst
    out = []
    for e in eps:
        if e["condition"] not in ("checker_gate", "generic_gate", "ask_first"):
            continue
        inst = insts[e["state_id"]]
        w = inst.scenario.build(tuple(tuple(x) for x in e["privileged"]["hidden"]))
        w.reset()
        for k, log in enumerate(e["steps"]):
            prop = parse(log["proposal"])
            if log.get("veto") or log.get("substituted_ask"):
                c = w.clone()
                o = c.step(prop)
                out.append({"condition": e["condition"], "construction": e["construction"], "stakes": e["stakes"],
                            "class": commit_class(e["construction"], prop), "would_have": o.outcome,
                            "redecision": log.get("redecision"), "executed": log["executed"],
                            "scripted": "scripted_fallback" in log, "p": (log.get("check") or {}).get("p")})
            w.step(parse(log["executed"]))
    return out


def summarize(eps):
    res = {"per_condition": {}, "paired": {}, "criteria": {}}
    for c in CONDS:
        es = [e for e in eps if e["condition"] == c]
        n = len(es)
        steps = [s for e in es for s in e["steps"]]
        res["per_condition"][c] = {
            "episodes": n,
            "mean_return": round(statistics.mean(e["return_"] for e in es), 4),
            "success": round(sum(e["outcome"] == "success" for e in es) / n, 4),
            "error": round(sum(e["outcome"] == "error" for e in es) / n, 4),
            "timeout": round(sum(e["outcome"] == "timeout" for e in es) / n, 4),
            "mean_steps": round(statistics.mean(e["n_steps"] for e in es), 3),
            "mean_processed_tokens": round(statistics.mean(tokens(e) for e in es), 1),
            "mean_prompt_tokens": round(statistics.mean(sum(u["prompt_tokens"] for u in e["usage"].values()) for e in es), 1),
            "mean_completion_tokens": round(statistics.mean(sum(u["completion_tokens"] for u in e["usage"].values())
                                                            for e in es), 1),
            "mean_call_attempts": round(statistics.mean(calls(e) for e in es), 3),
            "calls_by_kind": {k: sum(e["usage"].get(k, {}).get("calls", 0) for e in es) for k in ("decision", "redecision", "check")},
            "failed_attempts": sum(u["attempts_failed"] for e in es for u in e["usage"].values()),
            "call_fallbacks": sum(u["fallbacks"] for e in es for u in e["usage"].values()),
            "mean_call_latency_s": round(statistics.mean(sum(u["latency_s"] for u in e["usage"].values()) for e in es), 3),
            "mean_wall_clock_s": round(statistics.mean(e["wall_clock_s"] for e in es), 3),
            "checker_cpu_ms_total": round(sum(e["checker_cpu_s"] for e in es) * 1000, 1),
            "triggers": sum(1 for s in steps if re.match(r"(give|drop)\(", s["proposal"])),
            "vetoes": sum(bool(s.get("veto")) for s in steps),
            "scripted_fallbacks": sum("scripted_fallback" in s for s in steps),
            "cache_hits": sum(bool((s.get("check") or {}).get("cache_hit")) for s in steps),
            "cap_hits": sum(bool((s.get("check") or {}).get("cap_reached")) for s in steps),
            "check_failures": sum(bool((s.get("check") or {}).get("failed")) for s in steps),
            "substituted_asks": sum("substituted_ask" in s for s in steps),
            "correct_commit_rate": round(sum(e["outcome"] == "success" and re.match(r"(give|drop)\(", e["actions"][-1] or "")
                                             is not None for e in es) / n, 4),
        }
    ret = lambda e: e["return_"]  # noqa: E731
    for a, b in (("checker_gate", "direct"), ("generic_gate", "direct"), ("ask_first", "direct"),
                 ("checker_gate", "generic_gate"), ("checker_gate", "ask_first"), ("generic_gate", "ask_first")):
        res["paired"][f"{a}-{b}"] = {"return": paired(eps, a, b, ret)}
    pc = res["per_condition"]
    prim = res["paired"]["checker_gate-direct"]["return"]
    crit_a = prim["mean"] >= 0.05
    crit_b = {}
    for comp in ("generic_gate", "ask_first"):
        d = res["paired"][f"checker_gate-{comp}"]["return"]
        ratio = pc["checker_gate"]["mean_processed_tokens"] / pc[comp]["mean_processed_tokens"]
        quality = d["mean"] >= 0.03 and ratio <= 1.10
        efficiency = ratio <= 0.80 and d["mean"] >= 0 and d["ci95"][0] > -0.05
        crit_b[comp] = {"delta_return": d, "token_ratio": round(ratio, 3), "quality_route": quality,
                        "efficiency_route": efficiency, "pass": quality or efficiency}
    crit_c = pc["checker_gate"]["success"] >= pc["direct"]["success"] - 0.05
    gd = res["paired"]["checker_gate-generic_gate"]["return"]
    res["criteria"] = {"a_gain_vs_direct": {"value": prim, "pass": crit_a},
                       "b_vs_comparators": crit_b,
                       "c_not_only_suppression": {"checker_success": pc["checker_gate"]["success"],
                                                  "direct_success": pc["direct"]["success"], "pass": crit_c},
                       "continue_concept2": crit_a and all(x["pass"] for x in crit_b.values()) and crit_c,
                       "generic_similar": abs(gd["mean"]) < 0.03 and gd["ci95"][0] <= 0 <= gd["ci95"][1]}
    # descriptive breakdowns
    res["by_construction"] = {}
    for con in sorted({e["construction"] for e in eps}):
        res["by_construction"][con] = {c: {"return": round(statistics.mean(e["return_"] for e in eps if e["construction"] == con
                                                                           and e["condition"] == c), 3),
                                           "error": round(statistics.mean(e["outcome"] == "error" for e in eps
                                                                          if e["construction"] == con and e["condition"] == c), 3)}
                                       for c in CONDS}
    res["by_stakes"] = {f"x{st:g}": {c: round(statistics.mean(e["return_"] for e in eps if e["stakes"] == st
                                                              and e["condition"] == c), 4) for c in CONDS}
                        for st in (1.0, 4.0)}
    return res


def interventions(rows):
    out = {}
    for c in ("checker_gate", "generic_gate", "ask_first"):
        rs = [r for r in rows if r["condition"] == c]
        out[c] = {"n": len(rs),
                  "would_have_failed": sum(r["would_have"] == "error" for r in rs),
                  "would_have_succeeded": sum(r["would_have"] == "success" for r in rs),
                  "by_class": {k: {"n": sum(r["class"] == k for r in rs),
                                   "would_fail": sum(r["class"] == k and r["would_have"] == "error" for r in rs),
                                   "would_succeed": sum(r["class"] == k and r["would_have"] == "success" for r in rs)}
                               for k in ("social_belief", "physical", "testimony_reliability")}}
    return out


def main():
    run = Path(sys.argv[1])
    raw = [json.loads(l) for l in (run / "episodes.jsonl").read_text().splitlines() if l.strip()]
    blocked = [e for e in raw if "blocked" in e]
    eps = [e for e in raw if "blocked" not in e]
    res = summarize(eps)
    rows = replay_vetoes(eps)
    res["interventions"] = interventions(rows)
    res["blocked_episodes"] = len(blocked)
    res["episodes"] = len(eps)
    res["seeds"] = sorted({e["seed"] for e in eps})
    res["run_dir"] = str(run)
    man = run / "manifest.json"
    if man.exists():
        res["manifest"] = json.loads(man.read_text())
    (OUT / "fallback-results.json").write_bytes(json.dumps(res, indent=1, default=str).encode("utf-8"))
    (OUT / "fallback-interventions.jsonl").write_bytes("".join(json.dumps(r) + "\n" for r in rows).encode("utf-8"))
    print(json.dumps({k: res[k] for k in ("per_condition", "paired", "criteria", "interventions", "by_stakes")}, indent=1))


if __name__ == "__main__":
    main()
