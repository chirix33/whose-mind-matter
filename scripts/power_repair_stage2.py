"""Repair block Stage 2 precision simulation (experiment-plan.md Entry 1a RC2/RC3/RC4/RC5). PLANNING ONLY.

    ~/venvs/vllm/bin/python scripts/power_repair_stage2.py   # numpy (planning tool only; not the project stack)

Planning input: dev-v3 Round B `none` episode returns (reports/dev-v3-block/evidence/episodes-roundB-local.csv), pooled by
stratum (1c->1, 2a->2, 3c->3, 4b->4) and stakes. These are exploratory planning inputs, not known rates. Writes
reports/repair-block/power.json and power.md.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "repair-block"
DELTA = 0.05
KS = (3, 4, 5, 6, 8, 12, 16, 20, 24)
EFFECTS = (0.0, 0.05, 0.10)
RHO = 0.5
SIMS, FLIPS, BOOTS = 400, 2000, 1000
MIN_PER_SEED = 8.0  # estimated wall-clock minutes per seed (Round B: 192 episodes in ~8 min; one seed ~168 + notes)
LIMIT_MIN = 240.0
STRATUM = {"1c": 1, "2a": 2, "3c": 3, "4b": 4}


def pools():
    rows = list(csv.DictReader((ROOT / "reports/dev-v3-block/evidence/episodes-roundB-local.csv").open()))
    p = {}
    for r in rows:
        if r["condition"] != "none":
            continue
        c = r["state_id"].split("-")[2]
        st = 4.0 if "stakes4" in r["state_id"] else 1.0
        p.setdefault((STRATUM[c], st), []).append((float(r["return"]), r["outcome"]))
    return p


def condition_sampler(pool, target, scale):
    vals = np.array([v for v, _ in pool])
    bad = np.array([o != "success" for _, o in pool])
    mu = vals.mean()
    vals = mu + scale * (vals - mu)
    succ = vals[~bad] if (~bad).any() else vals
    gain = RHO * np.mean(np.where(bad, succ.mean() - vals, 0.0))
    rho, shift = RHO, 0.0
    if target <= 0:
        rho, shift = 0.0, 0.0
    elif gain > target:
        rho, shift = RHO * target / gain, 0.0
    else:
        shift = target - gain

    def none(rng, n):
        return vals[rng.integers(0, len(vals), n)]

    def cond(rng, n):
        idx = rng.integers(0, len(vals), n)
        x = vals[idx].copy()
        repl = bad[idx] & (rng.random(n) < rho)
        x[repl] = succ[rng.integers(0, len(succ), repl.sum())]
        return x + shift
    return none, cond


def simulate(K, effect, scale, rng, pl):
    n = 12 * K
    strata = np.repeat([1, 2, 3, 4], 3 * K)  # 3 constructions per stratum, K bases each
    cons = np.repeat(np.arange(12), K)
    samplers = {(s, st): condition_sampler(pl[(s, st)], 0.0 if s == 1 else effect * 4 / 3, scale)
                for s in (1, 2, 3, 4) for st in (1.0, 4.0)}
    classes = {"helps": 0, "no practical value": 0, "unresolved": 0}
    halfw = []
    signs = rng.choice([-1.0, 1.0], size=(FLIPS, n))
    for _ in range(SIMS):
        d = np.zeros(n)
        for s in (1, 2, 3, 4):
            m = strata == s
            k = m.sum()
            tot_n = np.zeros(k)
            tot_c = np.zeros(k)
            for st in (1.0, 4.0):
                none, cond = samplers[(s, st)]
                tot_n += none(rng, 2 * k).reshape(k, 2).sum(1)
                tot_c += cond(rng, 2 * k).reshape(k, 2).sum(1)
            d[m] = (tot_c - tot_n) / 4.0
        obs = abs(d.mean())
        p = (np.abs((signs * d).mean(1)) >= obs - 1e-12).mean()
        dk = d.reshape(12, K)  # bases are grouped by construction (cons = repeat(arange(12), K))
        pick = rng.integers(0, K, size=(BOOTS, 12, K))
        boots = np.take_along_axis(np.broadcast_to(dk, (BOOTS, 12, K)), pick, axis=2).mean(axis=2).mean(axis=1)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        halfw.append((hi - lo) / 2)
        if p < 0.025 and d.mean() >= DELTA:
            classes["helps"] += 1
        elif hi < DELTA:
            classes["no practical value"] += 1
        else:
            classes["unresolved"] += 1
    return {k: v / SIMS for k, v in classes.items()}, float(np.mean(halfw))


def main():
    rng = np.random.default_rng(20261100)
    pl = pools()
    res = {}
    for K in KS:
        feasible = K * MIN_PER_SEED <= LIMIT_MIN
        for var, scale in (("A", 1.0), ("B", 1.5)):
            for eff in EFFECTS:
                probs, hw = simulate(K, eff, scale, rng, pl)
                res[f"K{K}|{var}|{eff}"] = {"K": K, "feasible": feasible, "variance": var, "effect": eff,
                                             "probs": probs, "ci_halfwidth": hw}
                print(K, var, eff, probs, round(hw, 4), flush=True)
    ok = [K for K in KS if K * MIN_PER_SEED <= LIMIT_MIN
          and res[f"K{K}|B|0.1"]["probs"]["helps"] >= 0.8 and res[f"K{K}|B|0.0"]["probs"]["no practical value"] >= 0.8]
    feas = [K for K in KS if K * MIN_PER_SEED <= LIMIT_MIN]
    chosen = min(ok) if ok else max(feas)
    out = {"label": "PLANNING ONLY (Round B none returns as exploratory input)", "delta": DELTA, "rho": RHO,
           "sims": SIMS, "flips": FLIPS, "boots": BOOTS, "minutes_per_seed_estimate": MIN_PER_SEED,
           "limit_minutes": LIMIT_MIN, "criterion_met": ok, "chosen_K": chosen, "cells": res}
    (OUT / "power.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    L = ["# Stage 2 precision simulation (planning only)", "",
         f"Rule (Entry 1a RC5): smallest feasible K with P(helps | Δ=0.10) ≥ 0.8 and P(no practical value | Δ=0) ≥ 0.8 under "
         f"variance B; otherwise the largest feasible K. Criterion met for K = {ok or 'none'}; **chosen K = {chosen}** "
         f"({12 * chosen} base scenarios).", "",
         "| K | var | Δ | P(helps) | P(no practical value) | P(unresolved) | CI half-width |", "|---|---|---|---|---|---|---|"]
    for v in res.values():
        p = v["probs"]
        L.append(f"| {v['K']} | {v['variance']} | {v['effect']} | {p['helps']:.2f} | {p['no practical value']:.2f} | "
                 f"{p['unresolved']:.2f} | {v['ci_halfwidth']:.3f} |")
    (OUT / "power.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("chosen K", chosen)


if __name__ == "__main__":
    main()
