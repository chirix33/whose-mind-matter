"""Tiny-case labels: legacy privileged reference (Stage 0) and grounded bounded-policy references.

Run (CPU only):
    python scripts/run_tiny_cases.py [--seed 0]

Writes $OFFICEMINDS_RUNS/tiny/<run_id>/{manifest.json,labels.json,episodes.jsonl}, the
human-readable reports/tiny-cases.md (EVERY number and claim in it is generated from the
canonical records in labels.json), and a review bundle in reports/bundle/: this run's
manifest, one paired visible/privileged/graph trace, and one evidence-change trace.
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
from officeminds.scenarios import ALL_CASES, REVERSAL_WITNESS, TINY_CASES  # noqa: E402
from officeminds.world import Action  # noqa: E402
from vomi import runlog  # noqa: E402
from vomi.allocation import conditional_relevance, minimal_sufficient, reference_value, stop  # noqa: E402
from vomi.graph import PerspectiveGraph, visible_evidence  # noqa: E402
from vomi.oracle import (  # noqa: E402
    GROUNDED_SCALAR, GROUNDED_TYPED, PRIVILEGED_BOUNDED, ExactOracle, brute_force_best_return,
)
from vomi.theory import best_return_by_outcome, generator_audit  # noqa: E402
from vomi.units import K, generate_candidates  # noqa: E402

BUNDLE_CASE = "false_belief"
STOP_LAMBDA = 0.01  # illustrative price per one-call unit for the D-011 pair; NOT a measured cost
SETTINGS = ((GROUNDED_TYPED, "face_value"), (GROUNDED_SCALAR, "face_value"),
            (GROUNDED_SCALAR, "hedged"), (PRIVILEGED_BOUNDED, "face_value"))
TOL = 1e-9


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


def grounded_row(case: str, seed: int) -> tuple[dict, dict]:
    sc = ALL_CASES[case]()
    # The reversal pair is defined at one visible history (Bob says A, Carol says B).
    params = REVERSAL_WITNESS if case.startswith("reversal_") else sample_params(sc, seed)
    hist = first_hist(sc, params)
    units = generate_candidates(sc.config, hist)
    row = {"case": case, "purpose": sc.purpose, "candidates": [str(u) for u in units], "records": {}}
    for record, testimony in SETTINGS:
        o = ExactOracle(sc, hist, testimony=testimony)
        values = o.subset_values(units, record=record)
        decs = [asdict(o.decompose(u, record=record)) for u in units]
        pos = [d for d in decs if d["delta_j"] > TOL]
        row["records"][f"{record}/{testimony}"] = {
            "j_empty": values[frozenset()],
            "j_all_historical": values[frozenset(units)],
            "reference_best": reference_value(values),
            "base_action": str(o.evaluate(record=record).actions[0]) if record != PRIVILEGED_BOUNDED else None,
            "best_minimal_sets": [sorted(map(str, g)) for g in minimal_sufficient(values)],
            "j_all_minimal_sets_historical": [sorted(map(str, g)) for g in minimal_sufficient(values, reference="all")],
            "d4_relevant_at_empty": sorted(map(str, conditional_relevance(frozenset(), values))),
            "required_depth": o.effective_depth(units, record=record),
            "prefix_depth_historical": o.effective_depth_prefix(units, record=record),
            "decomposition": decs,
            "n_positive_units": len(pos),
            "n_carryover_units": sum(d["carryover"] for d in pos),
            "carryover_value_share": (sum(d["d_memory"] for d in pos) / sum(d["delta_j"] for d in pos)) if pos else None,
        }
    o = ExactOracle(sc, hist)
    row["generator_audit"] = generator_audit(sc, o)
    outcomes = {}
    for p, _ in sc.prior:
        w = sc.build(p)
        outcomes[json.dumps(dict(p))] = best_return_by_outcome(w, w.reset())
    row["early_failure_incentive"] = any(
        any(v >= b["success"] for k, v in b.items() if k != "success") for b in outcomes.values())

    # One episode: the face-value scalar-diagnostic actor with the first best-reference allocation.
    values = o.subset_values(units, record=GROUNDED_SCALAR)
    S = minimal_sufficient(values)[0]
    i = next(k for k, pp in enumerate(o.params) if pp == params)
    actions, ret = o.actor_rollout(i, S, GROUNDED_SCALAR)
    ep_hist, trace, _ = run_episode(sc, params, fixed_policy(actions))
    rec = episode_record(ep_hist, trace)
    g = PerspectiveGraph()
    for u in sorted(S):
        g.instantiate(u, o.grounded_output(u), visible_evidence(hist, u.path), t=0)
    graph_trace = [{"t": 0, "units": {k: asdict(v) for k, v in g.units.items()}}]
    for k in range(2, len(ep_hist.steps) + 1):
        g.advance(VisibleHistory(ep_hist.brief, ep_hist.steps[:k]))
        graph_trace.append({"t": k - 1, "policy_view": g.policy_view()})
    rec["robot_graph"] = graph_trace  # robot-side: built from visible history + unit outputs only
    rec["allocation"] = sorted(map(str, S))
    core = {k: rec[k] for k in ("agent_view", "privileged", "agent_view_sha256", "return")}
    row["episode"] = {"seed": seed, "params": dict(params), "allocation": rec["allocation"],
                      "actions": [str(a) for a in actions], "return": rec["return"],
                      "matches_label_rollout": abs(rec["return"] - ret) < 1e-12,
                      "replay_identical": replay(json.loads(json.dumps(core)), ALL_CASES) == core}
    return row, rec


def stop_pair() -> dict:
    """D-011 grounded unit-vs-STOP isolating pair with its posterior-to-outcome tables."""
    out = {}
    for m in (1, 4):
        sc = ALL_CASES[f"reversal_m{m}"]()
        hist = first_hist(sc, REVERSAL_WITNESS)
        o = ExactOracle(sc, hist)
        d = o.decompose(K("bob"), record=GROUNDED_SCALAR)
        v = o.subset_values([K("bob")], record=GROUNDED_SCALAR)
        out[f"x{m}"] = {"decomposition": asdict(d), "net_vomi": d.net_vomi(STOP_LAMBDA), "lambda": STOP_LAMBDA,
                        "stop_preferred": stop(frozenset(), v, lam=STOP_LAMBDA),
                        "candidates": [str(u) for u in generate_candidates(sc.config, hist)],
                        "unit_output": o.grounded_output(K("bob")),
                        "outcomes_without": o.outcome_table(frozenset(), GROUNDED_SCALAR),
                        "outcomes_with": o.outcome_table(frozenset({K("bob")}), GROUNDED_SCALAR)}
    return out


def evidence_change_trace() -> dict:
    """D-007: new visible evidence changes a previously useful inference (refresh is counted)."""
    sc = ALL_CASES["false_belief"]()
    params = (("initial", "office_a"), ("moved", "yes"))
    w = sc.build(params)
    h = VisibleHistory(sc.brief, [(None, w.reset())])
    h.steps.append((Action("ask", "rec", "alice_loc"), w.step(Action("ask", "rec", "alice_loc"))))
    g = PerspectiveGraph()
    g.instantiate(K("rec"), ExactOracle(sc, h).grounded_output(K("rec")), visible_evidence(h, ("rec",)), t=1)
    steps = [{"t": 1, "event": "instantiate K(rec) after rec says office_a", "policy_view": g.policy_view()}]
    for a in (Action("move", "hall"), Action("move", "office_a")):
        h.steps.append((a, w.step(a)))
        g.advance(h)
        steps.append({"t": h.last.t, "event": f"{a}", "policy_view": g.policy_view()})
    g.refresh(K("rec"), ExactOracle(sc, h).grounded_output(K("rec")), visible_evidence(h, ("rec",)), t=h.last.t)
    steps.append({"t": h.last.t, "event": "refresh K(rec) (counted call)", "policy_view": g.policy_view(),
                  "cost_calls": g.units["K(rec)"].cost_calls, "history": g.units["K(rec)"].history})
    return {"agent_view": h.to_agent_dict(), "privileged": {"scenario_id": sc.id, "params": [list(x) for x in params]},
            "robot_graph": steps}


def fmt_sets(sets):
    return "; ".join("{" + ", ".join(s) + "}" for s in sets) or "—"


def markdown(legacy, grounded, stop_res, run_id) -> str:
    L = [
        "# Tiny-case labels",
        "",
        f"Generated by `scripts/run_tiny_cases.py`, run `{run_id}` (manifest under `$OFFICEMINDS_RUNS/tiny/{run_id}/`; copy in `reports/bundle/`). "
        "Every number and claim below is rendered from the run's `labels.json`; no value is typed by hand.",
        "All values are exact enumerations under the stated model. No LLM is involved. "
        "**delta_J** = gross marginal task value J(S∪u) − J(S); **net VoMI** = delta_J − λ·c, shown only where λ is stated.",
        "",
        "## Part A: legacy privileged perfect-content reference (Stage 0 values)",
        "",
        "Record `privileged_bayes`: a Bayes-optimal actor with the TRUE contents of S revealed. A reference only, never a target (D-001). "
        "Gold sets here are J(all)-relative (historical definition; monotone in this record).",
        "",
        "| case | worlds | J(∅) | J(all) | full-info bound | required depth | minimal sufficient sets (J(all)) | LOO-necessary |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in legacy:
        lab = r["labels"]
        L.append(f"| {r['case']} | {r['worlds']} | {lab['j_empty']:.4f} | {lab['j_full']:.4f} | {r['full_information_bound']:.4f} | "
                 f"{r['effective_depth']} | {fmt_sets(lab['minimal_sufficient'])} | {', '.join(lab['loo_necessary']) or '—'} |")
    L += ["", "Legacy per-unit singleton reports (S = ∅):", "",
          "| case | unit | delta_J retain | P(flip) | E[ΔQ\\|flip] | no-flip residual | delta_J drop | H(c_u) bits |",
          "|---|---|---|---|---|---|---|---|"]
    for r in legacy:
        for a, b in zip(r["unit_reports"]["retain"], r["unit_reports"]["drop"]):
            L.append(f"| {r['case']} | {a['unit']} | {a['delta_j']:.4f} | {a['p_flip']:.3f} | {a['dq_given_flip']:.4f} | "
                     f"{a['no_flip_residual']:.4f} | {b['delta_j']:.4f} | {a['content_entropy_bits']:.3f} |")

    L += ["", "## Part B: grounded bounded-policy references", "",
          "Bounded actor: face-value defaults (ε = 1e-6, primary) or hedged (ε = 0.25, mandatory sensitivity). Unit outputs enter by I-projection:",
          "- `grounded_typed`: typed hypotheses over (content, default holds), the exact typed symbolic reference (D-007);",
          "- `grounded_scalar`: **diagnostic only**, `p_default_holds` = P(factor satisfies its face-value default | h); `unknown` content satisfies a Knowledge default;",
          "- `privileged_bounded`: the same actor given TRUE contents (a diagnostic, not a bound).",
          "",
          "Both grounded outputs are exact generator marginals: an offline reference, not a deployable or cheap computation. "
          "**Primary reference** = the best admissible subset (incl. ∅, λ = 0, no budget); J(all)-relative sets are a historical diagnostic.",
          "",
          "| case | record / testimony | base action | J(∅) | best J | J(all) (hist.) | required depth | best minimal sets | D4-relevant at ∅ |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in grounded:
        for key, v in r["records"].items():
            L.append(f"| {r['case']} | {key} | {v['base_action'] or '(per world)'} | {v['j_empty']:.4f} | {v['reference_best']:.4f} | "
                     f"{v['j_all_historical']:.4f} | {v['required_depth']} | {fmt_sets(v['best_minimal_sets'])} | "
                     f"{', '.join(v['d4_relevant_at_empty']) or '—'} |")

    keys = [f"{r}/{t}" for r, t in SETTINGS]
    L += ["", "### Required depth per setting (generated; consistency-tested against every best minimal set)", "",
          "| case | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
    for r in grounded:
        L.append(f"| {r['case']} | " + " | ".join(str(r["records"][k]["required_depth"]) for k in keys) + " |")

    L += ["", "### D-002 decomposition per unit (S = ∅; nonzero rows only)", "",
          "delta_J = D_action + D_memory. `carryover` = positive delta_J with zero current-action flips.", "",
          "| case | record / testimony | unit | a0 → ay | E[Q(m,a0)] | E[Q(m,ay)] | E[Q(my,ay)] | D_action | D_memory | delta_J | residual | P(flip) | carryover |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in grounded:
        for key, v in r["records"].items():
            for d in v["decomposition"]:
                if abs(d["delta_j"]) > 1e-12 or abs(d["d_action"]) > 1e-12:
                    L.append(f"| {r['case']} | {key} | {d['unit']} | {d['a0']} → {d['ay']} | {d['q_m_a0']:.4f} | {d['q_m_ay']:.4f} | "
                             f"{d['q_my_ay']:.4f} | {d['d_action']:+.4f} | {d['d_memory']:+.4f} | {d['delta_j']:+.4f} | "
                             f"{d['residual']:.1e} | {d['p_flip']:.3f} | {'yes' if d['carryover'] else ''} |")

    L += ["", "### Carryover share (D-012; positive-delta_J units only)", "",
          "| record / testimony | positive units | carryover units | D_memory share of positive delta_J |", "|---|---|---|---|"]
    for k in keys:
        n = sum(r["records"][k]["n_positive_units"] for r in grounded)
        c = sum(r["records"][k]["n_carryover_units"] for r in grounded)
        num = sum(d["d_memory"] for r in grounded for d in r["records"][k]["decomposition"] if d["delta_j"] > TOL)
        den = sum(d["delta_j"] for r in grounded for d in r["records"][k]["decomposition"] if d["delta_j"] > TOL)
        L.append(f"| {k} | {n} | {c} | {num / den:.3f} |" if den else f"| {k} | {n} | {c} | — |")

    L += ["", "### Generator audit (D-008; a diagnostic, not a filter)", "",
          "| case | prior / posterior support | all defaults jointly satisfiable at h | entailed by family support | entailed by visible evidence | possible violations |",
          "|---|---|---|---|---|---|"]
    for r in grounded:
        a = r["generator_audit"]
        L.append(f"| {r['case']} | {a['prior_support']} / {a['posterior_support']} | {a['all_defaults_jointly_satisfiable']} | "
                 f"{', '.join(a['entailed_by_family']) or '—'} | {', '.join(a['entailed_by_evidence']) or '—'} | {len(a['possible_violations'])} |")

    L += ["", f"### D-011 grounded unit-vs-STOP isolating pair (`reversal_m*`, `grounded_scalar`, face value; λ = {STOP_LAMBDA} illustrative)", "",
          "| stakes | unit | a0 → ay | delta_J | net VoMI (λ stated) | P(flip) | D_memory | STOP preferred | unit output |",
          "|---|---|---|---|---|---|---|---|---|"]
    for s, v in stop_res.items():
        d = v["decomposition"]
        L.append(f"| {s} | {d['unit']} | {d['a0']} → {d['ay']} | {d['delta_j']:+.8f} | {v['net_vomi']:+.5f} | {d['p_flip']:.0f} | "
                 f"{d['d_memory']:.1e} | {v['stop_preferred']} | p_default_holds = {v['unit_output']['p_default_holds']:.6f} |")
    L += ["", "Posterior-to-outcome table (x1 / x4 returns; same worlds, posteriors and actions at both stakes):", "",
          "| world (alice, bob, carol) | posterior | action without unit | return | action with K(bob) | return x1 | return x4 |",
          "|---|---|---|---|---|---|---|"]
    for a, b1, b4 in zip(stop_res["x1"]["outcomes_without"], stop_res["x1"]["outcomes_with"], stop_res["x4"]["outcomes_with"]):
        p = a["params"]
        L.append(f"| {p['alice_loc']}, {p['bob_type']}, {p['carol_type']} | {a['posterior']:.6f} | {a['action']} | {a['return']:+.2f} | "
                 f"{b1['action']} | {b1['return']:+.2f} | {b4['return']:+.2f} |")

    rev = {r["case"]: r["records"]["privileged_bounded/face_value"]["decomposition"] for r in grounded if r["case"].startswith("reversal_")}
    L += ["", "### Privileged two-unit ranking reversal (diagnostic only, NOT grounded evidence; D-011)", "",
          "| unit | stakes | delta_J | P(flip) | D_memory |", "|---|---|---|---|---|"]
    for case in sorted(rev):
        for d in rev[case]:
            if d["unit"] in ("R(bob)", "K(carol)"):
                L.append(f"| {d['unit']} | x{case[-1]} | {d['delta_j']:+.5f} | {d['p_flip']:.5f} | {d['d_memory']:.1e} |")

    L += ["", "### Episodes (face-value scalar actor, first best-reference allocation, retained in G_t) and audits", "",
          "| case | allocation | actions | return | equals label rollout | replay | early-failure incentive |", "|---|---|---|---|---|---|---|"]
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
                                            "seed": args.seed, "settings": [list(s) for s in SETTINGS],
                                            "stop_lambda": STOP_LAMBDA})
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
    stop_res = stop_pair()
    change = evidence_change_trace()
    labels = {"legacy": legacy, "grounded": grounded, "stop_pair": stop_res}
    (out / "labels.json").write_text(json.dumps(labels, indent=1, default=str))
    (ROOT / "reports" / "tiny-cases.md").write_text(markdown(legacy, grounded, stop_res, manifest["run_id"]), encoding="utf-8")
    ok = all(r["episode"]["replay_identical"] and r["episode"]["matches_label_rollout"] for r in grounded)
    path = runlog.finish(manifest, out, all_replays_identical=ok,
                         any_early_failure_incentive=any(r["early_failure_incentive"] for r in grounded))
    bundle = ROOT / "reports" / "bundle"
    bundle.mkdir(exist_ok=True)
    shutil.copy(path, bundle / "tiny-manifest.json")
    (bundle / f"trace-{BUNDLE_CASE}.json").write_text(json.dumps(bundle_trace, indent=1, default=str))
    (bundle / "trace-evidence-change.json").write_text(json.dumps(change, indent=1, default=str))
    (bundle / "stop-pair.json").write_text(json.dumps(stop_res, indent=1, default=str))
    for r in grounded:
        v = r["records"]["grounded_scalar/face_value"]
        print(f"{r['case']:<22} J0={v['j_empty']:.4f} best={v['reference_best']:.4f} depth={v['required_depth']} "
              f"gold={v['best_minimal_sets']} ep={r['episode']['return']:+.2f}")
    print(f"replays+rollouts ok: {ok}; manifest: {path}")


if __name__ == "__main__":
    main()
