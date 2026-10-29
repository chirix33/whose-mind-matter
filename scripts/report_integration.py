"""Integration diagnostic analysis (frozen before outputs; experiment-plan.md Entry 1 §E + Entry 1a RC5/RC6).

    python3 scripts/report_integration.py   -> reports/integration-block/results.{json,md}

Unit: base unit = (seed, construction); its value per condition and context = mean over x1/x4 x 3 draws. Contrasts are
paired within base units; 95% bootstrap CI resampling seeds within construction (10,000) plus an exact paired sign-flip
p (2^n enumeration). Negative pair = 2b+3b; positive pair = 2a+3a. Descriptive diagnostic (8 seeds per construction).
"""

from __future__ import annotations

import itertools
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCK = ROOT / "reports" / "integration-block"
DATA = ROOT / "data" / "integration-block"
NEG, POS = ("2b", "3b"), ("2a", "3a")
GAP_TOL = 0.10  # RC5(b): positive-pair gap increase tolerance


def boot(d_by, seed=20261201, n=10000):
    rng = random.Random(seed)
    cons = sorted(d_by)
    ms = sorted(statistics.mean(statistics.mean(rng.choices(d_by[c], k=len(d_by[c]))) for c in cons) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n) - 1]


def signflip(d):
    n = len(d)
    if n == 0:
        return None
    obs = abs(sum(d) / n)
    if 2 ** n > 2 ** 20:
        rng = random.Random(7)
        hits = sum(abs(sum(x if rng.random() < .5 else -x for x in d) / n) >= obs - 1e-12 for _ in range(200000))
        return (hits + 1) / 200001
    return sum(abs(sum(x * s for x, s in zip(d, sg)) / n) >= obs - 1e-12 for sg in itertools.product((1, -1), repeat=n)) / 2 ** n


def main(api_only=False):
    rows = [json.loads(l) for l in (DATA / "local-decisions.jsonl").read_text().splitlines() if l.strip()]
    q = {r["state_id"]: r for r in json.loads((BLOCK / "qualification.json").read_text())["states"]}
    cons_of = {sid: r["construction"] for sid, r in q.items()}
    role_of = {sid: r["ask_subject_role"] for sid, r in q.items()}

    def values(ctx, metric, keep=lambda r: True):
        v = defaultdict(lambda: defaultdict(list))
        for r in rows:
            if r["context"] == ctx and keep(r):
                v[(q[r["state_id"]]["seed"], cons_of[r["state_id"]])][r["condition"]].append(float(r[metric]))
        return {k: {c: statistics.mean(x) for c, x in cs.items()} for k, cs in v.items()}

    def contrast(vals, f, cons):
        d_by = defaultdict(list)
        for (seed, c), cs in vals.items():
            if c in cons:
                try:
                    d_by[c].append(f(cs))
                except KeyError:
                    pass
        d = [x for v in d_by.values() for x in v]
        if not d:
            return None
        est = statistics.mean(statistics.mean(v) for v in d_by.values())
        lo, hi = boot(d_by)
        return {"estimate": round(est, 4), "ci95": [round(lo, 4), round(hi, 4)], "n": len(d), "signflip_p": signflip(d)}

    C = {"t0": {"content-none": lambda c: c["content"] - c["none"], "impl-none": lambda c: c["impl"] - c["none"],
                "impl-content": lambda c: c["impl"] - c["content"]},
         "post": {**{f"{k}-none": (lambda k: lambda c: c[k] - c["none"])(k) for k in
                     ("content|shown", "content|omitted", "impl|shown", "impl|omitted")},
                  "impl_main": lambda c: (c["impl|shown"] + c["impl|omitted"] - c["content|shown"] - c["content|omitted"]) / 2,
                  "omit_main": lambda c: (c["content|omitted"] + c["impl|omitted"] - c["content|shown"] - c["impl|shown"]) / 2,
                  "interaction": lambda c: (c["impl|omitted"] - c["impl|shown"]) - (c["content|omitted"] - c["content|shown"]),
                  "impl_avg-none": lambda c: (c["impl|shown"] + c["impl|omitted"]) / 2 - c["none"],
                  "omit_avg-none": lambda c: (c["content|omitted"] + c["impl|omitted"]) / 2 - c["none"]}}
    res = {"decisions": len(rows), "contrasts": {}, "rates": {}, "fallbacks": {}, "readings": {}}
    for sens, keep in (("primary", lambda r: True), ("excl_fallbacks", lambda r: not r["fallback"])):
        for ctx, fs in C.items():
            for metric in ("wrong", "gap", "correct_handoff", "handoff"):
                vals = values(ctx, metric, keep)
                for group, cons in (("negative", NEG), ("positive", POS), *((c, (c,)) for c in NEG + POS)):
                    for name, f in fs.items():
                        res["contrasts"][f"{sens}|{ctx}|{metric}|{group}|{name}"] = contrast(vals, f, cons)
    # per-condition raw rates by construction x stakes x context; 2a post-ask split by asked role (RC1)
    agg = defaultdict(list)
    for r in rows:
        st = r["state_id"]
        key = f"{r['context']}|{cons_of[st]}|{'x4' if 'stakes4' in st else 'x1'}|{r['condition']}"
        agg[key].append(r)
        if cons_of[st] == "2a" and r["context"] == "post":
            agg[f"post|2a-asked-{role_of[st]}|{r['condition']}"].append(r)
    res["rates"] = {k: {"n": len(v), "wrong": statistics.mean(x["wrong"] for x in v),
                        "correct_handoff": statistics.mean(x["correct_handoff"] for x in v),
                        "gap": statistics.mean(x["gap"] for x in v), "fallbacks": sum(x["fallback"] for x in v),
                        "actions": dict(sorted({a: sum(x["action"] == a for x in v) for a in {x["action"] for x in v}}.items()))}
                    for k, v in sorted(agg.items())}
    fb = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        k = f"{r['context']}|{r['condition']}"
        fb[k][0] += r["fallback"]
        fb[k][1] += 1
        fb[k][2] += sum(bool(a.get("validation_errors")) for a in r["call"]["attempts"])
    res["fallbacks"] = {k: {"fallbacks": a, "decisions": b, "failed_attempts": c} for k, (a, b, c) in sorted(fb.items())}
    flag = []
    for ctx, conds in (("t0", ("none", "content", "impl")), ("post", ("none", "content|shown", "content|omitted",
                                                                      "impl|shown", "impl|omitted"))):
        rates = {c: res["fallbacks"].get(f"{ctx}|{c}", {"fallbacks": 0, "decisions": 1}) for c in conds}
        r_ = {c: v["fallbacks"] / v["decisions"] for c, v in rates.items()}
        if max(r_.values()) - min(r_.values()) > 0.05:
            flag.append(ctx)
    res["fallback_rate_flag_contexts"] = flag

    # pre-declared reading (Entry 1 §E as amended by RC5), separately for t0 and post-ask
    def X(ctx, metric, group, name):
        return res["contrasts"][f"primary|{ctx}|{metric}|{group}|{name}"]

    def reading(ctx, factor, vs_none):
        w_f, w_n = X(ctx, "wrong", "negative", factor), X(ctx, "wrong", "negative", vs_none)
        c_n = X(ctx, "correct_handoff", "positive", vs_none)
        c_f = X(ctx, "correct_handoff", "positive", factor)
        g_f, g_p = X(ctx, "gap", "negative", factor), X(ctx, "gap", "positive", factor)
        if (w_f["ci95"][0] > 0) or (c_f["ci95"][1] < 0):
            return "harm"
        helps = (w_f["ci95"][1] < 0 and w_n["estimate"] < 0 and c_n["estimate"] >= -0.10 and c_f["estimate"] >= -0.10
                 and g_f["estimate"] <= 0 and g_p["estimate"] <= GAP_TOL)
        if helps:
            return "helps (preserving positive controls)"
        if w_f["ci95"][1] < 0 and w_n["estimate"] >= 0:
            return "repairs note-induced harm only"
        if w_f["estimate"] >= -0.05 and (w_f["ci95"][0] <= 0 <= w_f["ci95"][1] or w_f["estimate"] >= 0):
            return "neither (practically small)"
        return "uncertain"
    rd = {"t0|implication": reading("t0", "impl-content", "impl-none"),
          "post|implication": reading("post", "impl_main", "impl_avg-none"),
          "post|omission": reading("post", "omit_main", "omit_avg-none")}
    post_impl, post_omit = rd["post|implication"], rd["post|omission"]
    if post_impl.startswith("helps") and post_omit.startswith("helps"):
        rd["post|both"] = "both factors help"
    res["readings"] = rd
    api = BLOCK / "api-check.json"
    res["api_check"] = json.loads(api.read_text()) if api.exists() else None
    (BLOCK / "results.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    fmt = lambda c: "n/a" if not c else f"{c['estimate']:+.3f} [{c['ci95'][0]:+.3f}, {c['ci95'][1]:+.3f}] p={c['signflip_p']:.3f} (n={c['n']})"
    L = ["# Integration diagnostic results (local probe; single decisions; development data)", "",
         f"`scripts/report_integration.py` (frozen before outputs). {len(rows)} decisions. Descriptive: 8 seeds per construction; "
         "the CI resamples seeds within construction; p = exact paired sign-flip. Not a return estimate.", "",
         f"**Pre-declared readings:** {json.dumps(rd)}", "", "## Key contrasts (primary, including fallbacks)", ""]
    for ctx, names in (("t0", ("content-none", "impl-none", "impl-content")),
                       ("post", ("content|shown-none", "impl|shown-none", "impl_main", "omit_main", "interaction",
                                 "impl_avg-none", "omit_avg-none"))):
        for metric in ("wrong", "correct_handoff", "gap"):
            for group in ("negative", "positive"):
                L.append(f"- {ctx} | {metric} | {group} | " + "; ".join(f"{n}: {fmt(X(ctx, metric, group, n))}" for n in names))
    L += ["", "## Raw rates (context | construction | stakes | condition)", ""]
    L += [f"- {k}: n={v['n']} wrong={v['wrong']:.2f} correct={v['correct_handoff']:.2f} gap={v['gap']:.3f} fb={v['fallbacks']} {v['actions']}"
          for k, v in res["rates"].items()]
    L += ["", f"Fallbacks: {json.dumps(res['fallbacks'])}; contexts with >5-point fallback-rate spread: {flag or 'none'}"]
    if res["api_check"]:
        L += ["", "## API policy check (descriptive; not pooled)", "",
              f"Worst case {res['api_check']['worst_case_usd']}, incremental USD {res['api_check']['incremental_usd']}.", ""]
        L += [f"- {d['state_id']} {d['context']} {d['condition']}: {d['action']} wrong={d['wrong']} gap={d['gap']:.3f} "
              f"fallback={d['fallback']} finish={d['finish_reason']}" for d in res["api_check"]["decisions"]]
    (BLOCK / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps(rd))


if __name__ == "__main__":
    main()
