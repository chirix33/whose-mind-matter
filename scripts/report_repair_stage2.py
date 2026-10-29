"""Repair block Stage 2 analysis (fixed before outcomes: experiment-plan.md Entry 2 + Entry 1a RC3/RC4/RC6/RC13/RC14).

    python3 scripts/report_repair_stage2.py <run_dir>   -> reports/repair-block/stage2-results.{json,md}

Unit: the base scenario (seed, construction); its value per condition = mean return over its x1/x4 variants x draws.
Estimand: equal-weight mean over the 12 constructions and x1/x4 of expected return (new draws of these constructions).
Decision statistic (RC3 rule i): Holm-adjusted two-sided sign-flip over base scenarios decides "> 0" (smaller p at
0.025, larger at 0.05); the point estimate decides ">= delta"; delta statements use the 95% stratified percentile
bootstrap CI (resampling base scenarios within construction, 10,000 resamples).
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from run_repair import BLOCK, NOTES, reference_note, score_row, stage2_states  # noqa: E402

DELTA = 0.05
BOOTS, FLIPS = 10000, 100000


def sign_flip_p(d, seed=20261101):
    n = len(d)
    obs = abs(sum(d) / n)
    if 2 ** n <= 10 ** 6:  # RC3: exact enumeration for small n
        import itertools
        hits = sum(abs(sum(x * s for x, s in zip(d, signs)) / n) >= obs - 1e-12
                   for signs in itertools.product((1, -1), repeat=n))
        return hits / 2 ** n
    rng = random.Random(seed)
    hits = 0
    for _ in range(FLIPS):
        if abs(sum(x if rng.random() < 0.5 else -x for x in d) / n) >= obs - 1e-12:
            hits += 1
    return (hits + 1) / (FLIPS + 1)


def strat_ci(d_by_cons, seed=20261102):
    rng = random.Random(seed)
    cons = sorted(d_by_cons)
    means = []
    for _ in range(BOOTS):
        means.append(statistics.mean(statistics.mean(rng.choices(d_by_cons[c], k=len(d_by_cons[c]))) for c in cons))
    means.sort()
    return means[int(0.025 * BOOTS)], means[int(0.975 * BOOTS) - 1]


def contrast(vals, a, b, keys):
    """Paired base-scenario differences a - b over `keys` (base scenarios having both)."""
    d_by = defaultdict(list)
    excluded = []
    for key in keys:
        if a in vals[key] and b in vals[key]:
            d_by[key[1]].append(vals[key][a] - vals[key][b])
        else:
            excluded.append({"base": list(key), "missing": [c for c in (a, b) if c not in vals[key]]})
    d = [x for v in d_by.values() for x in v]
    est = statistics.mean(statistics.mean(v) for v in d_by.values()) if d_by else None  # equal construction weight
    lo, hi = strat_ci(d_by) if d_by else (None, None)
    return {"n_base": len(d), "estimate": est, "ci95": [lo, hi], "d_by_construction_mean":
            {c: statistics.mean(v) for c, v in sorted(d_by.items())}, "excluded_base_scenarios": excluded, "_d": d}


def depth_diffs(sts, notes):
    """S7 / RC13(a): 3a and 3c reference K(F->R) vs K(R) rendered blocks; count states differing beyond the unit label
    and the 'estimate of ...' wording."""
    import re
    from run_repair import rendered
    out = {"states": 0, "differ_beyond_labels": 0, "examples": []}
    for sid, st in sts.items():
        if st["inst"].construction not in ("3a", "3c"):
            continue
        a, b = rendered(st, "reference", notes)[1], rendered(st, "reference_KR", notes)[1]
        norm = lambda t: re.sub(r"estimate of [^:]+:", "estimate of X:", re.sub(r"K\([^)]*\)", "K(.)", t))
        out["states"] += 1
        if norm(a) != norm(b):
            out["differ_beyond_labels"] += 1
            if len(out["examples"]) < 3:
                out["examples"].append({"state_id": sid, "reference": a, "reference_KR": b})
    return out


def main():
    run = Path(sys.argv[1])
    eps = [json.loads(l) for l in (run / "episodes.jsonl").read_text().splitlines() if l.strip()]
    manifest = json.loads((run / "manifest.json").read_text())
    blocks = set(manifest.get("completed_seed_blocks", []))
    eps = [e for e in eps if e["seed"] in blocks]
    blocked = [e for e in eps if "blocked" in e]
    good = [e for e in eps if "blocked" not in e]
    sts = {st["state_id"]: st for st in stage2_states(len(blocks))}
    qual = {r["state_id"]: r for r in json.loads((BLOCK / "stage2-qualification.json").read_text())["states"]}
    vals_raw = defaultdict(lambda: defaultdict(list))
    for e in good:
        st = sts[e["state_id"]]
        vals_raw[(st["seed"], st["inst"].construction)][e["condition"]].append(e["return_"])
    vals = {k: {c: statistics.mean(v) for c, v in cs.items()} for k, cs in vals_raw.items()}
    keys = sorted(vals)
    ref, inf = contrast(vals, "reference", "none", keys), contrast(vals, "inferred", "none", keys)
    ps = {"reference": sign_flip_p(ref["_d"]), "inferred": sign_flip_p(inf["_d"])}
    order = sorted(ps, key=ps.get)
    sig = {order[0]: ps[order[0]] < 0.025}
    sig[order[1]] = sig[order[0]] and ps[order[1]] < 0.05
    inf_ref = contrast(vals, "inferred", "reference", keys)

    def ref_class():
        if sig["reference"] and ref["estimate"] > 0 and ref["estimate"] >= DELTA:
            return "helps"
        if ref["ci95"][1] < DELTA:
            return "no practical value"
        return "unresolved"

    anomaly = inf_ref["ci95"][0] is not None and inf_ref["ci95"][0] > DELTA

    def inf_class():
        if anomaly:  # S5: precedence over "approximates"
            return "anomaly (inferred above reference)"
        if sig["inferred"] and inf["estimate"] > 0 and inf["estimate"] >= DELTA and inf_ref["ci95"][0] >= -DELTA:
            return "helps and approximates"
        if inf["ci95"][1] < DELTA or inf_ref["ci95"][1] < -DELTA:
            return "fails"
        return "unresolved"
    rc, ic = ref_class(), inf_class()
    table = {("helps", "helps and approximates"): "§5(1) propose a small allocation feasibility study",
             ("helps", "fails"): "§5(2) inference bottleneck",
             ("helps", "unresolved"): "§5(4) uncertainty too large (inferred)",
             ("no practical value", "helps and approximates"): "anomaly: mechanism check; §5(3)",
             ("no practical value", "fails"): "§5(3) reconsider method/environment fit",
             ("no practical value", "unresolved"): "§5(3) reconsider method/environment fit",
             ("unresolved", "helps and approximates"): "anomaly; §5(4)",
             ("unresolved", "fails"): "§5(4) uncertainty too large",
             ("unresolved", "unresolved"): "§5(4) uncertainty too large",
             ("helps", "anomaly (inferred above reference)"): "mechanism check; no §5(1)",
             ("no practical value", "anomaly (inferred above reference)"): "mechanism check; no §5(1)",
             ("unresolved", "anomaly (inferred above reference)"): "mechanism check; no §5(1)"}
    # secondary: per stratum, outcomes, by construction and stakes
    strata = {}
    for s in (1, 2, 3, 4):
        ks = [k for k in keys if k[1][0] == str(s)]
        strata[s] = {c: {k: v for k, v in contrast(vals, c, "none", ks).items() if k != "_d"} for c in ("reference", "inferred")}
    outc = defaultdict(lambda: defaultdict(int))
    steps = defaultdict(list)
    by_cs = defaultdict(list)
    for e in good:
        st = sts[e["state_id"]]
        outc[e["condition"]][e["outcome"]] += 1
        steps[e["condition"]].append(e["steps"])
        by_cs[(e["condition"], st["inst"].construction, st["inst"].variant.stakes)].append(e["return_"])
    # depth (RC13): stratum 3, K(F->R) vs K(R) notes, and the 3b - 3a difference-in-differences
    depth = {}
    for cond in ("reference", "inferred"):
        for c in ("3a", "3b", "3c"):
            ks = [k for k in keys if k[1] == c]
            depth[f"{cond}|{c}|K(F->R)-K(R)"] = {k: v for k, v in contrast(vals, cond, f"{cond}_KR", ks).items() if k != "_d"}
        did = []
        for seed in sorted({k[0] for k in keys}):
            a, b = vals.get((seed, "3a"), {}), vals.get((seed, "3b"), {})
            if all(x in a and x in b for x in (cond, "none")):
                did.append((b[cond] - b["none"]) - (a[cond] - a["none"]))
        lo, hi = strat_ci({"all": did}) if did else (None, None)
        depth[f"{cond}|DiD (cond-none)[3b]-(cond-none)[3a]"] = {"n": len(did), "estimate": statistics.mean(did) if did else None,
                                                              "ci95": [lo, hi]}
    # fidelity of inferred notes (all Stage 2 notes, incl. K(R))
    notes = json.loads(NOTES.read_text())
    fid = []
    for sid, row in notes["states"].items():
        if sid not in sts:
            continue
        st = sts[sid]
        for us, parsed in row["inferred"].items():
            u = next(u for cs in st["conds"].values() for u in cs if str(u) == us)
            _, dist = reference_note(st["inst"], u)
            r = score_row(st["inst"], u, parsed, dist)
            fid.append({"state_id": sid, "construction": st["inst"].construction, "unit": us, "ok": r["ok"],
                        "category": r["category"], "tv": r["tv_posterior"], "unsupported_mass": r["unsupported_mass"],
                        "status": r["status"], "prior_copy": r["prior_copy"], "distribution": r["distribution"],
                        "posterior": r["posterior"]})
    fid_by = defaultdict(list)
    for f in fid:
        fid_by[f["construction"]].append(f)
    fid_sum = {c: {"n": len(v), "valid": sum(f["ok"] for f in v),
                   "mean_tv": statistics.mean(f["tv"] for f in v if f["ok"]) if any(f["ok"] for f in v) else None,
                   "mean_unsupported_mass": statistics.mean(f["unsupported_mass"] for f in v if f["ok"]) if any(f["ok"] for f in v) else None,
                   "abstained": sum(f["status"] == "abstain" for f in v),
                   "categories": {k: sum(str(f["category"]) == k for f in v) for k in sorted({str(f["category"]) for f in v})},
                   # in 4c the posterior equals the prior, so a prior match there is CORRECT (S6)
                   ("matches_prior_correct_in_4c" if c == "4c" else "prior_copies"): sum(bool(f["prior_copy"]) for f in v),
                   **({"over_updates_4c": sum(f["ok"] and f["prior_copy"] is False for f in v)} if c == "4c" else {})}
               for c, v in sorted(fid_by.items())}
    (ROOT / "data" / "repair-block").mkdir(parents=True, exist_ok=True)
    (ROOT / "data" / "repair-block" / "stage2-fidelity-rows.json").write_text(json.dumps(fid, indent=1, default=str))
    # compute (RC14): notes charged to the inferred conditions that show them; decisions per condition
    comp = defaultdict(lambda: defaultdict(float))
    for sid, row in notes["states"].items():
        if sid not in sts:
            continue
        for us, call in row["calls"].items():
            cond = "inferred_KR" if us in [str(u) for u in sts[sid]["conds"].get("inferred_KR", [])] and \
                us not in [str(u) for u in sts[sid]["conds"]["inferred"]] else "inferred"
            for a in call["attempts"]:
                comp[cond]["note_attempts"] += 1
                comp[cond]["note_attempts_missing_usage"] += int(a.get("prompt_tokens") is None or a.get("completion_tokens") is None)
                if a.get("reasoning_tokens") is None:
                    comp[cond]["note_reasoning_tokens_unavailable_attempts"] += 1
                else:
                    comp[cond]["note_reasoning_tokens"] += a["reasoning_tokens"]
                comp[cond]["note_prompt_tokens"] += a.get("prompt_tokens") or 0
                comp[cond]["note_completion_tokens"] += a.get("completion_tokens") or 0
                comp[cond]["note_latency_s"] += a.get("latency_s") or 0
    for e in good:
        d = e["usage"].get("decision", {})
        c = comp[e["condition"]]
        c["episodes"] += 1
        c["decision_calls"] += d.get("calls", 0)
        c["decision_prompt_tokens"] += d.get("prompt_tokens", 0)
        c["decision_completion_tokens"] += d.get("completion_tokens", 0)
        c["decision_latency_s"] += d.get("latency_s", 0)
        c["failed_attempts"] += sum(v.get("attempts_failed", 0) for v in e["usage"].values())
        if d and d.get("reasoning_tokens_known"):
            c["decision_reasoning_tokens"] += d.get("reasoning_tokens", 0)
        else:
            c["decision_reasoning_tokens_unavailable_episodes"] += 1
        c["fallbacks"] += sum(v.get("fallbacks", 0) for v in e["usage"].values())
    headroom = {c: statistics.mean(qual[sid]["bayes_value_t0"] for sid in sts) - statistics.mean(
        e["return_"] for e in good if e["condition"] == c) for c in ("none", "inferred", "reference")}
    res = {"run_id": manifest["run_id"], "completed_seed_blocks": sorted(blocks), "base_scenarios": len(keys),
           "episodes": len(good), "blocked": len(blocked),
           "primary": {"reference_minus_none": {k: v for k, v in ref.items() if k != "_d"},
                       "inferred_minus_none": {k: v for k, v in inf.items() if k != "_d"},
                       "sign_flip_p": ps, "holm_significant": sig},
           "inferred_minus_reference": {k: v for k, v in inf_ref.items() if k != "_d"},
           "reference_class": rc, "inferred_class": ic, "outcome": table[(rc, ic)], "anomaly_inferred_above_reference": anomaly,
           "strata": strata, "outcomes": {c: dict(v) for c, v in outc.items()},
           "mean_steps": {c: statistics.mean(v) for c, v in steps.items()},
           "by_construction_stakes": {f"{c}|{k}|{s:g}": statistics.mean(v) for (c, k, s), v in sorted(by_cs.items())},
           "depth": depth, "fidelity_by_construction": fid_sum, "compute": {c: dict(v) for c, v in comp.items()},
           "headroom_bayes_minus_condition": headroom,
           "blocked_episodes": [{k: e[k] for k in ("state_id", "condition", "replicate", "blocked")} for e in blocked],
           "wall_clock": {"notes_stage_s": notes.get("wall_s"), "policy_stage_s": manifest.get("wall_clock_s"),
                          "concurrency": manifest.get("concurrency"),
                          "reference_oracle_cpu_s_not_deployable": notes.get("reference_oracle_s")},
           "depth_render_diffs_3a_3c": depth_diffs(sts, notes)}
    (BLOCK / "stage2-results.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    fmt = lambda c: f"{c['estimate']:+.4f} [{c['ci95'][0]:+.4f}, {c['ci95'][1]:+.4f}] (n={c['n_base']})"
    L = [f"# Stage 2 results — run `{manifest['run_id']}`", "",
         f"`scripts/report_repair_stage2.py` (frozen before outcomes). {len(keys)} base scenarios from "
         f"{len(blocks)} complete seed blocks; {len(good)} episodes, {len(blocked)} blocked. Development data, local backbone.", "",
         "## Primary (paired by base scenario; equal construction weight; 95% stratified bootstrap CI)", "",
         f"- reference − none: {fmt(ref)}; sign-flip p = {ps['reference']:.5f}; Holm-significant: {sig['reference']}",
         f"- inferred − none: {fmt(inf)}; sign-flip p = {ps['inferred']:.5f}; Holm-significant: {sig['inferred']}",
         f"- inferred − reference (secondary): {fmt(inf_ref)}", "",
         f"**Reference class: {rc}. Inferred class: {ic}. Pre-declared outcome: {table[(rc, ic)]}.**"
         + (" Anomaly: inferred − reference CI lower > +δ." if anomaly else ""), "",
         "## Per stratum (condition − none)", ""]
    for s, v in strata.items():
        L.append(f"- stratum {s}: " + "; ".join(f"{c} {fmt(x)}" for c, x in v.items()))
    L += ["", "## Outcomes and steps", ""] + [f"- {c}: {dict(v)}; mean steps {statistics.mean(steps[c]):.2f}" for c, v in outc.items()]
    L += ["", f"Headroom (Bayes V* − condition mean): { {k: round(v, 4) for k, v in headroom.items()} }", "",
          "## Depth (RC13; descriptive; 3a/3c are label-only controls)", ""]
    for k, v in depth.items():
        L.append(f"- {k}: " + (fmt(v) if "n_base" in v else f"{v['estimate']} {v['ci95']} (n={v['n']})"))
    L += ["", "## Inferred-note fidelity by construction", ""] + [f"- {c}: {v}" for c, v in fid_sum.items()]
    L += ["", f"Depth render diffs 3a/3c (reference K(F->R) vs K(R)): { {k: v for k, v in res['depth_render_diffs_3a_3c'].items() if k != 'examples'} }",
          "", f"Blocked episodes: {len(blocked)}; excluded base scenarios (reference−none / inferred−none): "
          f"{ref['excluded_base_scenarios']} / {inf['excluded_base_scenarios']}", "", f"Wall clock: {res['wall_clock']}"]
    L += ["", "## Compute (all attempts charged)", ""] + [f"- {c}: {dict(v)}" for c, v in res["compute"].items()]
    L += ["", "## By construction × stakes (mean return)", ""] + [f"- {k}: {v:.3f}" for k, v in res["by_construction_stakes"].items()]
    (BLOCK / "stage2-results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(rc, "|", ic, "|", table[(rc, ic)])


if __name__ == "__main__":
    main()
