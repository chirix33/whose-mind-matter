"""D-006: search the conflicting-reports family for a verified stakes RANKING REVERSAL.

Isolating criteria, checked by exact enumeration for each config, record and testimony default:
  - same visible history (Bob says office_a, Carol says office_b) at stakes x1 and x4;
  - the base action a(∅) is identical across stakes in every world;
  - for both units U and V: same per-world current-action flip pattern and the same target
    actions across stakes, and P(flip) > 0;
  - zero carryover (D_memory = 0) for U and V at both stakes;
  - VoMI(U) - VoMI(V) changes sign between x1 and x4, with |difference| > 1e-6;
  - no actor ties: the actor's own decision margin > 1e-6 for every compared decision.

Run:  python scripts/search_stakes_reversal.py [--samples 300] [--seed 0]
Writes $OFFICEMINDS_RUNS/search/<run_id>/{manifest.json,hits.json} and prints the hits.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.scenarios import REPORTER_TYPES, conflicting_reports  # noqa: E402
from vomi import runlog  # noqa: E402
from vomi.oracle import GROUNDED_SCALAR, PRIVILEGED_BOUNDED, ExactOracle  # noqa: E402
from vomi.units import generate_candidates  # noqa: E402

WITNESS = (("alice_loc", "office_a"), ("bob_type", "accurate"), ("carol_type", "mistaken"))


def oracle_for(bob, carol, stakes, testimony):
    sc = conflicting_reports(bob, carol, stakes)
    w = sc.build(WITNESS)
    hist = VisibleHistory(sc.brief, [(None, w.reset())])
    return sc, hist, ExactOracle(sc, hist, testimony=testimony)


def unit_profile(o, u, record):
    d = o.decompose(u, record=record)
    base = [o.best_action(o.actor_items(frozenset(), record, i), o.obs) for i in range(len(o.worlds))]
    tgt = [o.best_action(o.actor_items(frozenset({u}), record, i), o.obs) for i in range(len(o.worlds))]
    margins = [o.decision_margin(o.actor_items(frozenset({u}), record, i), o.obs) for i in range(len(o.worlds))]
    return {"delta_j": d.delta_j, "d_action": d.d_action, "d_memory": d.d_memory, "p_flip": d.p_flip,
            "flips": tuple(a != b for a, b in zip(base, tgt)), "targets": tuple(map(str, tgt)),
            "base": tuple(map(str, base)), "min_margin": min(margins)}


def diagnose(bob, carol, record, testimony, counts):
    """For every unit pair whose VoMI ordering reverses across stakes, record the FIRST isolating
    criterion it fails (explains infeasibility instead of only reporting 'no hits')."""
    prof = {}
    for m in (1.0, 4.0):
        sc, hist, o = oracle_for(bob, carol, m, testimony)
        prof[m] = {str(u): unit_profile(o, u, record) for u in generate_candidates(sc.config, hist)}
    p1, p4 = prof[1.0], prof[4.0]
    for U, V in itertools.permutations(sorted(p1), 2):
        a1, a4, b1, b4 = p1[U], p4[U], p1[V], p4[V]
        if not (a1["delta_j"] - b1["delta_j"] < -1e-6 and a4["delta_j"] - b4["delta_j"] > 1e-6):
            continue
        counts["reversals"] += 1
        if a1["base"] != a4["base"]:
            counts["base_action_changes_with_stakes"] += 1
        elif not (a1["flips"] == a4["flips"] and b1["flips"] == b4["flips"]):
            counts["flip_pattern_changes"] += 1
        elif not (a1["p_flip"] > 0 and b1["p_flip"] > 0):
            counts["a_unit_never_flips"] += 1
        elif not (a1["targets"] == a4["targets"] and b1["targets"] == b4["targets"]):
            counts["targets_change"] += 1
        elif max(abs(x["d_memory"]) for x in (a1, a4, b1, b4)) > 1e-9:
            counts["nonzero_carryover"] += 1
        elif min(x["min_margin"] for x in (a1, a4, b1, b4)) <= 1e-6:
            counts["actor_tie"] += 1
        else:
            counts["passes_all"] += 1


def check(bob, carol, record, testimony):
    prof = {}
    for m in (1.0, 4.0):
        sc, hist, o = oracle_for(bob, carol, m, testimony)
        units = generate_candidates(sc.config, hist)
        base_margin = min(o.decision_margin(o.actor_items(frozenset(), record, i), o.obs) for i in range(len(o.worlds)))
        prof[m] = ({str(u): unit_profile(o, u, record) for u in units}, base_margin)
    (p1, bm1), (p4, bm4) = prof[1.0], prof[4.0]
    if min(bm1, bm4) <= 1e-6:
        return []
    hits = []
    for U, V in itertools.permutations(sorted(p1), 2):
        a1, a4, b1, b4 = p1[U], p4[U], p1[V], p4[V]
        if a1["base"] != a4["base"]:
            continue
        if not (a1["flips"] == a4["flips"] and b1["flips"] == b4["flips"] and a1["p_flip"] > 0 and b1["p_flip"] > 0):
            continue
        if not (a1["targets"] == a4["targets"] and b1["targets"] == b4["targets"]):
            continue
        if max(abs(x["d_memory"]) for x in (a1, a4, b1, b4)) > 1e-9:
            continue
        if min(x["min_margin"] for x in (a1, a4, b1, b4)) <= 1e-6:
            continue
        d1, d4 = a1["delta_j"] - b1["delta_j"], a4["delta_j"] - b4["delta_j"]
        if d1 < -1e-6 and d4 > 1e-6:  # U below V at x1, above V at x4 (the review's direction)
            hits.append({"U": U, "V": V, "x1": {"U": a1, "V": b1}, "x4": {"U": a4, "V": b4}})
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--diagnose", action="store_true", help="count which criterion each reversal fails")
    args = ap.parse_args()
    rng = random.Random(args.seed)
    levels = (0.02, 0.1, 0.25, 0.5, 0.8)
    kind = "search-diagnose" if args.diagnose else "search"
    manifest = runlog.new_manifest(kind, {"samples": args.samples, "seed": args.seed, "levels": levels})
    out = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "search" / manifest["run_id"]
    if args.diagnose:
        from collections import Counter
        by_key = {}
        for _ in range(args.samples):
            bob = dict(zip(REPORTER_TYPES, (rng.choice(levels) for _ in REPORTER_TYPES)))
            carol = dict(zip(REPORTER_TYPES, (rng.choice(levels) for _ in REPORTER_TYPES)))
            for record in (GROUNDED_SCALAR, PRIVILEGED_BOUNDED):
                for testimony in ("face_value", "hedged"):
                    diagnose(bob, carol, record, testimony, by_key.setdefault(f"{record}/{testimony}", Counter()))
        out.mkdir(parents=True, exist_ok=True)
        (out / "diagnosis.json").write_text(json.dumps(by_key, indent=1))
        runlog.finish(manifest, out, diagnosis=by_key)
        print(json.dumps(by_key, indent=1))
        print(f"out: {out}")
        return
    found, tried = [], 0
    for _ in range(args.samples):
        bob = dict(zip(REPORTER_TYPES, (rng.choice(levels) for _ in REPORTER_TYPES)))
        carol = dict(zip(REPORTER_TYPES, (rng.choice(levels) for _ in REPORTER_TYPES)))
        for record in (GROUNDED_SCALAR, PRIVILEGED_BOUNDED):
            for testimony in ("face_value", "hedged"):
                tried += 1
                for h in check(bob, carol, record, testimony):
                    h.update(bob=bob, carol=carol, record=record, testimony=testimony)
                    found.append(h)
                    print(json.dumps({k: h[k] for k in ("U", "V", "bob", "carol", "record", "testimony")}), flush=True)
    out.mkdir(parents=True, exist_ok=True)
    (out / "hits.json").write_text(json.dumps(found, indent=1, default=str))
    runlog.finish(manifest, out, configs_checked=tried, hits=len(found))
    print(f"checked {tried} (config, record, testimony) combinations; hits: {len(found)}; out: {out}")


if __name__ == "__main__":
    main()
