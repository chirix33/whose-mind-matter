"""Analyze a full pilot run: paired arm comparisons, symbolic-to-realized transfer, typed-unit fidelity,
router/STOP behavior, response to stakes/evidence variants, overhead, failures.

    python3 scripts/analyze_pilot.py <run_dir> [--version dev-v2]

Descriptive statistics on DEVELOPMENT data (exploratory pilot; no hypothesis tests). Writes
reports/pilot/pilot-analysis-<run_id>.md.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REC = "grounded_typed/face_value"


def load(run_dir: Path, version: str):
    eps = [json.loads(l) for l in (run_dir / "episodes.jsonl").open()]
    ivs = [json.loads(l) for l in (run_dir / "interventions.jsonl").open()] if (run_dir / "interventions.jsonl").exists() else []
    data = ROOT / "data" / "pilot" / version
    pub = {json.loads(l)["instance_id"]: json.loads(l) for l in (data / "public.jsonl").open()}
    priv = {json.loads(l)["instance_id"]: json.loads(l) for l in (data / "privileged.jsonl").open()}
    return eps, ivs, pub, priv


def category(p: dict) -> str:
    units = p["symbolic"][REC]["units"]
    if units and all(abs(u["delta_j"]) < 1e-12 for u in units):
        return "zero_value_stop"
    if any(u["carryover"] for u in units):
        return "carryover"
    if any(u["delta_j"] > 0.01 and abs(u["d_memory"]) < 1e-12 for u in units):
        return "useful_current_action"
    if any(u["delta_j"] > 0.01 for u in units):
        return "mixed_flip_and_carryover"
    return "other"


def utype(name: str) -> str:
    return f"{name[0]}{'2' if '->' in name else '1'}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--version", default="dev-v2")
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    eps, ivs, pub, priv = load(run_dir, args.version)
    arms = [a for a in ("direct", "dense", "random", "router", "symbolic") if any(e["arm"] == a for e in eps)]
    R = {(e["instance_id"], e["arm"]): e for e in eps}
    ids = sorted({e["instance_id"] for e in eps})
    L = [f"# Pilot analysis: `{run_dir.name}`", "",
         f"Descriptive statistics on development data (exploratory pilot; no hypothesis tests; n = {len(ids)} instances in "
         f"{len({pub[i]['group_id'] for i in ids})} groups, so instances within a group are not independent). "
         f"Symbolic categories are privileged evaluator annotations (`{REC}`).", ""]

    # Paired comparisons
    L += ["## Paired per-instance return differences", "", "| comparison | mean diff | wins | losses | ties |", "|---|---|---|---|---|"]
    for a, b in (("dense", "direct"), ("random", "direct"), ("router", "direct"), ("symbolic", "direct"), ("router", "random"), ("dense", "router")):
        if a in arms and b in arms:
            d = [R[(i, a)]["return_"] - R[(i, b)]["return_"] for i in ids]
            L.append(f"| {a} − {b} | {statistics.mean(d):+.3f} | {sum(x > 1e-9 for x in d)} | {sum(x < -1e-9 for x in d)} | {sum(abs(x) <= 1e-9 for x in d)} |")

    # By symbolic category
    cats = {i: category(priv[i]) for i in ids}
    L += ["", "## Mean return by symbolic category (does the symbolic category transfer?)", "",
          "| category | n | " + " | ".join(arms) + " |", "|---|---|" + "---|" * len(arms)]
    for c in sorted(set(cats.values())):
        sel = [i for i in ids if cats[i] == c]
        L.append(f"| {c} | {len(sel)} | " + " | ".join(f"{statistics.mean(R[(i, a)]['return_'] for i in sel):+.3f}" for a in arms) + " |")
    L += ["", "| category | n | success rate: " + " | ".join(arms) + " |", "|---|---|" + "---|" * len(arms)]
    for c in sorted(set(cats.values())):
        sel = [i for i in ids if cats[i] == c]
        L.append(f"| {c} | {len(sel)} | " + " | ".join(f"{statistics.mean(R[(i, a)]['outcome'] == 'success' for i in sel):.2f}" for a in arms) + " |")

    # Typed-unit fidelity
    fid = [f for e in eps for f in e["privileged"]["unit_fidelity"]]
    conf = {}
    for e in eps:
        for c in e["calls"]:
            if c["kind"] in ("unit", "refresh") and c["ok"]:
                conf[(e["instance_id"], e["arm"], c["target"], c["step"])] = max(h["p"] for h in c["parsed"]["hypotheses"])
    L += ["", "## Typed-unit fidelity (LLM top hypothesis vs true content; privileged scoring)", "",
          "| unit type | calls | valid | top = truth | mean top-p (valid) | top=truth when top-p ≥ 0.8 | top = unknown |", "|---|---|---|---|---|---|---|"]
    by_t = defaultdict(list)
    for e in eps:
        for f in e["privileged"]["unit_fidelity"]:
            by_t[utype(f["unit"])].append((e, f))
    for t, xs in sorted(by_t.items()):
        ok = [(e, f) for e, f in xs if f["ok"]]
        ps = [conf.get((e["instance_id"], e["arm"], f["unit"], f["step"])) for e, f in ok]
        hi = [(e, f) for (e, f), p in zip(ok, ps) if p is not None and p >= 0.8]
        L.append(f"| {t} | {len(xs)} | {len(ok)} | {sum(f['top_matches_truth'] for _, f in ok) / max(len(ok), 1):.2f} | "
                 f"{statistics.mean(p for p in ps if p is not None) if ps else 0:.2f} | "
                 f"{(sum(f['top_matches_truth'] for _, f in hi) / len(hi)) if hi else float('nan'):.2f} (n={len(hi)}) | "
                 f"{sum(f['top'] == 'unknown' for _, f in ok) / max(len(ok), 1):.2f} |")
    L.append("")
    L.append("Unit types: K1 = K(j), K2 = K(j→k), R1 = R(j), R2 = R(j→k).")

    # Router behaviour
    if "router" in arms:
        rcalls = [c for i in ids for c in R[(i, "router")]["calls"] if c["kind"] == "router"]
        stops = sum(1 for c in rcalls if c["ok"] and not c["parsed"]["select"])
        jac = []
        for i in ids:
            ref = set((priv[i]["symbolic"][REC]["best_minimal_sets"] or [[]])[0])
            got = {f["unit"] for f in R[(i, "router")]["privileged"]["unit_fidelity"]}
            jac.append(1.0 if not ref and not got else len(ref & got) / len(ref | got))
        zero = [i for i in ids if cats[i] == "zero_value_stop"]
        L += ["", "## Router / STOP behaviour", "",
              f"- Router calls: {len(rcalls)}; STOP decisions: {stops} ({stops / max(len(rcalls), 1):.2f}).",
              f"- Mean units per episode: router {statistics.mean(R[(i, 'router')]['privileged']['units_instantiated'] for i in ids):.2f}, "
              f"random {statistics.mean(R[(i, 'random')]['privileged']['units_instantiated'] for i in ids):.2f}, "
              f"dense {statistics.mean(R[(i, 'dense')]['privileged']['units_instantiated'] for i in ids):.2f}.",
              f"- Router instantiated zero units in {sum(R[(i, 'router')]['privileged']['units_instantiated'] == 0 for i in zero)}/{len(zero)} "
              f"symbolic zero-value instances and in {sum(R[(i, 'router')]['privileged']['units_instantiated'] == 0 for i in ids if i not in zero)}/"
              f"{len(ids) - len(zero)} others.",
              f"- Mean Jaccard(router allocation, symbolic reference set): {statistics.mean(jac):.2f}."]

    # Response to stakes / evidence variants
    L += ["", "## Do decisions respond to variant knobs? (first action differs within a single-knob pair)", "",
          "| knob | pairs | " + " | ".join(arms) + " |", "|---|---|" + "---|" * len(arms)]
    groups = defaultdict(list)
    for i in ids:
        groups[pub[i]["group_id"]].append(i)
    for knob in ("stakes", "evidence"):
        pairs = []
        for g, members in groups.items():
            for a in members:
                for b in members:
                    va, vb = pub[a]["variant"], pub[b]["variant"]
                    if a < b and va[knob] != vb[knob] and all(va[k] == vb[k] for k in va if k != knob):
                        pairs.append((a, b))
        if pairs:
            L.append(f"| {knob} | {len(pairs)} | " + " | ".join(
                f"{sum(R[(a, arm)]['actions'][0] != R[(b, arm)]['actions'][0] for a, b in pairs)}" for arm in arms) + " |")

    # Overhead
    L += ["", "## Overhead share of tokens (prompt + completion, means per episode)", "",
          "| arm | decision | unit | refresh | router | router+unit share |", "|---|---|---|---|---|---|"]
    for a in arms:
        tot = defaultdict(float)
        for i in ids:
            for k, v in R[(i, a)]["usage"].items():
                tot[k] += (v["prompt_tokens"] + v["completion_tokens"]) / len(ids)
        s = sum(tot.values())
        L.append(f"| {a} | {tot['decision']:.0f} | {tot['unit']:.0f} | {tot['refresh']:.0f} | {tot['router']:.0f} | "
                 f"{(tot['unit'] + tot['router'] + tot['refresh']) / s if s else 0:.2f} |")

    # Failures
    fails = [(e["arm"], e["instance_id"], c["kind"], c["target"], [a["validation_errors"] or a["error"] for a in c["attempts"]])
             for e in eps for c in e["calls"] if any(a["validation_errors"] or a["error"] for a in c["attempts"])]
    kinds = Counter(err for *_, errs in fails for es in errs for err in (es if isinstance(es, list) else [es]) if err)
    L += ["", "## Invalid outputs and retries", "",
          f"- Calls with at least one failed attempt: {len(fails)}; failure reasons: {dict(kinds) or 'none'}.",
          f"- Calls that exhausted all attempts (fallback/abstain): {sum(1 for e in eps for c in e['calls'] if not c['ok'])}."]
    for f in fails[:8]:
        L.append(f"  - {f[0]} / {f[1]} / {f[2]} {f[3]}: {f[4]}")

    if ivs:
        same = sum(iv["a0_without"] == iv["a0_with"] for iv in ivs)
        L += ["", "## Paired interventions: symbolic vs realized", "",
              f"- {len(ivs)} states; first action changed in {len(ivs) - same}; sign agreement between symbolic delta_J and realized "
              f"return difference (non-zero cases): "
              f"{sum((iv['symbolic_delta_j'] > 0) == (iv['return_with'] - iv['return_without'] > 0) for iv in ivs if abs(iv['return_with'] - iv['return_without']) > 1e-9 and abs(iv['symbolic_delta_j']) > 1e-9)}"
              f"/{sum(1 for iv in ivs if abs(iv['return_with'] - iv['return_without']) > 1e-9 and abs(iv['symbolic_delta_j']) > 1e-9)}."]
    out = ROOT / "reports" / "pilot" / f"pilot-analysis-{run_dir.name}.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
