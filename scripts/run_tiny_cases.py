"""Tiny-case labels: legacy privileged reference (Stage 0) and grounded bounded-policy values (Stage 1).

Run (CPU only):
    python scripts/run_tiny_cases.py [--seed 0]

Writes $OFFICEMINDS_RUNS/tiny/<run_id>/{manifest.json,labels.json,episodes.jsonl}, the
human-readable reports/tiny-cases.md, and a small review bundle in reports/bundle/
(this run's manifest plus one paired visible/privileged/graph trace).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds.episode import (  # noqa: E402
    VisibleHistory, episode_record, fixed_policy, replay, run_episode, sample_params,
)
from officeminds.scenarios import ALL_CASES, GROUNDED_CASES, TINY_CASES  # noqa: E402
from vomi import runlog  # noqa: E402
from vomi.allocation import conditional_relevance, minimal_sufficient  # noqa: E402
from vomi.graph import PerspectiveGraph, visible_evidence  # noqa: E402
from vomi.oracle import GROUNDED, PRIVILEGED_BAYES, PRIVILEGED_BOUNDED, ExactOracle, brute_force_best_return  # noqa: E402
from vomi.theory import best_return_by_outcome  # noqa: E402
from vomi.units import generate_candidates  # noqa: E402

BUNDLE_CASE = "false_belief"


def first_hist(sc, params):
    w = sc.build(params)
    return VisibleHistory(sc.brief, [(None, w.reset())])


def legacy_row(case: str, seed: int) -> dict:
    """Stage 0 record (privileged perfect-content, Bayes-optimal actor), unchanged semantics."""
    sc = TINY_CASES[case]()
    hist = first_hist(sc, sample_params(sc, seed))
    o = ExactOracle(sc, hist)
    units = generate_candidates(sc.config, hist)
    labels = o.allocation_labels(units)
    reports = {c: [asdict(o.unit_report(u, continuation=c)) for u in units] for c in ("retain", "drop")}
    return {"case": case, "worlds": len(o.worlds), "labels": asdict(labels), "unit_reports": reports,
            "effective_depth": o.effective_depth(units),
            "full_information_bound": sum(p * brute_force_best_return(x, o.obs) for p, x in o.belief)}


def grounded_row(case: str, seed: int) -> tuple[dict, dict | None]:
    sc = ALL_CASES[case]()
    params = sample_params(sc, seed)
    hist = first_hist(sc, params)
    units = generate_candidates(sc.config, hist)
    row = {"case": case, "purpose": sc.purpose, "candidates": [str(u) for u in units], "records": {}}
    for record, testimony in ((GROUNDED, "face_value"), (GROUNDED, "hedged"), (PRIVILEGED_BOUNDED, "face_value")):
        o = ExactOracle(sc, hist, testimony=testimony)
        values = o.subset_values(units, record=record)
        gold = minimal_sufficient(values)
        row["records"][f"{record}/{testimony}"] = {
            "j_empty": values[frozenset()],
            "j_all": values[frozenset(units)],
            "base_action": str(o.evaluate(record=record).actions[0]) if record == GROUNDED else None,
            "minimal_sufficient": [sorted(map(str, g)) for g in gold],
            "d4_relevant_at_empty": sorted(map(str, conditional_relevance(frozenset(), values))),
            "effective_depth": o.effective_depth(units, record=record),
            "decomposition": [asdict(o.decompose(u, record=record)) for u in units],
        }
    audit = {}
    for p, _ in sc.prior:
        w = sc.build(p)
        audit[json.dumps(dict(p))] = best_return_by_outcome(w, w.reset())
    row["early_failure_incentive"] = any(
        any(v >= b["success"] for k, v in b.items() if k != "success") for b in audit.values())

    # One episode: the face-value grounded actor with the first gold allocation, retained in G_t.
    o = ExactOracle(sc, hist)
    values = o.subset_values(units, record=GROUNDED)
    S = minimal_sufficient(values)[0]
    i = next(k for k, pp in enumerate(o.params) if pp == params)
    actions, ret = o.actor_rollout(i, S, GROUNDED)
    ep_hist, trace, _ = run_episode(sc, params, fixed_policy(actions))
    rec = episode_record(ep_hist, trace)
    g = PerspectiveGraph()
    for u in sorted(S):
        g.instantiate(u, o.grounded_output(u), visible_evidence(hist, u.path), t=0)
    graph_trace = [{"t": 0, "units": {k: asdict(v) for k, v in g.units.items()}}]
    for k in range(2, len(ep_hist.steps) + 1):
        g.advance(VisibleHistory(ep_hist.brief, ep_hist.steps[:k]))
        graph_trace.append({"t": k - 1, "units": {n: {"status": v.status, "evidence": v.evidence} for n, v in g.units.items()}})
    rec["robot_graph"] = graph_trace  # robot-side: built from visible history + unit outputs only
    rec["allocation"] = sorted(map(str, S))
    row["episode"] = {"seed": seed, "params": dict(params), "allocation": rec["allocation"],
                      "actions": [str(a) for a in actions], "return": rec["return"],
                      "matches_label_rollout": abs(rec["return"] - ret) < 1e-12,
                      "replay_identical": replay(json.loads(json.dumps({k: rec[k] for k in ("agent_view", "privileged", "agent_view_sha256", "return")})), ALL_CASES)
                      == {k: rec[k] for k in ("agent_view", "privileged", "agent_view_sha256", "return")}}
    return row, rec


def fmt_sets(sets):
    return "; ".join("{" + ", ".join(s) + "}" for s in sets) or "—"


def markdown(legacy: list[dict], grounded: list[dict], run_id: str) -> str:
    L = [
        "# Tiny-case labels",
        "",
        f"Generated by `scripts/run_tiny_cases.py`, run `{run_id}` (manifest under `$OFFICEMINDS_RUNS/tiny/{run_id}/`; copy in `reports/bundle/`).",
        "All values are exact enumerations under the stated model. No LLM is involved. Records are kept separate on purpose.",
        "",
        "## Part A: legacy privileged perfect-content reference (Stage 0 values, relabeled)",
        "",
        "Record `privileged_bayes`: a Bayes-optimal actor over the raw history, with the TRUE contents of S revealed. **Not a training target** (D-001 outcome). "
        "The values are unchanged from Stage 0 (first reported in run `tiny-20261028-032629-565fb8`).",
        "",
        "| case | worlds | J(∅) | J(all) | full-info bound | ℓ* | minimal sufficient sets | LOO-necessary |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in legacy:
        lab = r["labels"]
        L.append(f"| {r['case']} | {r['worlds']} | {lab['j_empty']:.4f} | {lab['j_full']:.4f} | {r['full_information_bound']:.4f} | "
                 f"{r['effective_depth']} | {fmt_sets(lab['minimal_sufficient'])} | {', '.join(lab['loo_necessary']) or '—'} |")
    L += ["", "Legacy per-unit singleton reports (S = ∅):", "",
          "| case | unit | ΔJ retain | P(flip) | E[ΔQ\\|flip] | no-flip residual | ΔJ drop | H(c_u) bits |",
          "|---|---|---|---|---|---|---|---|"]
    for r in legacy:
        for a, b in zip(r["unit_reports"]["retain"], r["unit_reports"]["drop"]):
            L.append(f"| {r['case']} | {a['unit']} | {a['delta_j']:.4f} | {a['p_flip']:.3f} | {a['dq_given_flip']:.4f} | "
                     f"{a['no_flip_residual']:.4f} | {b['delta_j']:.4f} | {a['content_entropy_bits']:.3f} |")

    L += ["", "## Part B: grounded bounded-policy values (Stage 1 main symbolic target)", "",
          "Actor: face-value defaults (ε = 1e-6) or hedged (ε = 0.25); modeled units enter as evidence-grounded "
          "default-holds marginals (P(false belief / non-cooperation / mismodel | h), never content) by I-projection. `privileged_bounded` = the same bounded actor given TRUE contents "
          "(a reference, not a bound). Continuation: fixed (no new instantiations, retained content, exact observation updates).", "",
          "| case | record / testimony | base action | J(∅) | J(all) | ℓ* | minimal sufficient sets | D4-relevant at ∅ |",
          "|---|---|---|---|---|---|---|---|"]
    for r in grounded:
        for key, v in r["records"].items():
            L.append(f"| {r['case']} | {key} | {v['base_action'] or '(per world)'} | {v['j_empty']:.4f} | {v['j_all']:.4f} | "
                     f"{v['effective_depth']} | {fmt_sets(v['minimal_sufficient'])} | {', '.join(v['d4_relevant_at_empty']) or '—'} |")
    L += ["", "### D-002 decomposition per unit (S = ∅; nonzero rows only)", "",
          "VoMI_retained = D_action + D_memory (before λc). `carryover` = positive value with zero current-action flips.", "",
          "| case | record / testimony | unit | E[Q(m,a0)] | E[Q(m,ay)] | E[Q(my,ay)] | D_action | D_memory | total | residual | P(flip) | carryover |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in grounded:
        for key, v in r["records"].items():
            for d in v["decomposition"]:
                if abs(d["total"]) > 1e-12 or abs(d["d_action"]) > 1e-12:
                    L.append(f"| {r['case']} | {key} | {d['unit']} | {d['q_m_a0']:.4f} | {d['q_m_ay']:.4f} | {d['q_my_ay']:.4f} | "
                             f"{d['d_action']:+.4f} | {d['d_memory']:+.4f} | {d['total']:+.4f} | {d['residual']:.1e} | "
                             f"{d['p_flip']:.3f} | {'yes' if d['carryover'] else ''} |")
    L += ["", "### Episodes (face-value grounded actor, first gold allocation, retained in G_t) and audits", "",
          "| case | allocation | actions | return | equals label rollout | replay | early-failure incentive |",
          "|---|---|---|---|---|---|---|"]
    for r in grounded:
        e = r["episode"]
        L.append(f"| {r['case']} | {{{', '.join(e['allocation'])}}} | {' → '.join(e['actions'])} | {e['return']:+.2f} | "
                 f"{e['matches_label_rollout']} | {'identical' if e['replay_identical'] else 'MISMATCH'} | {r['early_failure_incentive']} |")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    manifest = runlog.new_manifest("tiny", {"legacy_cases": sorted(TINY_CASES), "grounded_cases": sorted(ALL_CASES),
                                            "seed": args.seed, "testimony_defaults": ["face_value", "hedged"]})
    out = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "tiny" / manifest["run_id"]
    out.mkdir(parents=True, exist_ok=True)
    legacy = [legacy_row(c, args.seed) for c in TINY_CASES]
    grounded, bundle_trace = [], None
    with (out / "episodes.jsonl").open("w") as f:
        for case in ALL_CASES:
            row, rec = grounded_row(case, args.seed)
            grounded.append(row)
            f.write(json.dumps(rec) + "\n")
            if case == BUNDLE_CASE:
                bundle_trace = rec
    (out / "labels.json").write_text(json.dumps({"legacy": legacy, "grounded": grounded}, indent=1, default=str))
    (ROOT / "reports" / "tiny-cases.md").write_text(markdown(legacy, grounded, manifest["run_id"]), encoding="utf-8")
    ok = all(r["episode"]["replay_identical"] and r["episode"]["matches_label_rollout"] for r in grounded)
    path = runlog.finish(manifest, out, all_replays_identical=ok,
                         any_early_failure_incentive=any(r["early_failure_incentive"] for r in grounded))
    bundle = ROOT / "reports" / "bundle"
    bundle.mkdir(exist_ok=True)
    shutil.copy(path, bundle / "tiny-manifest.json")
    (bundle / f"trace-{BUNDLE_CASE}.json").write_text(json.dumps(bundle_trace, indent=1))
    for r in grounded:
        v = r["records"]["grounded/face_value"]
        print(f"{r['case']:<22} J0={v['j_empty']:.4f} JU={v['j_all']:.4f} gold={v['minimal_sufficient']} ep={r['episode']['return']:+.2f}")
    print(f"replays+rollouts ok: {ok}; manifest: {path}")


if __name__ == "__main__":
    main()
