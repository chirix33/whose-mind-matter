"""Hybrid block (D-019) CPU gate: qualification, information boundary, joint-vs-marginal contrasts, cheap-compiler costs,
decision-value structure, and the branch decision. CPU only; no model calls.

    python3 scripts/hybrid_cpu_gate.py        # writes reports/hybrid-block/cpu-gate.{json,md}
"""

from __future__ import annotations

import json
import re
import statistics
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds import devgen3 as G  # noqa: E402
from officeminds import hybridfam as F  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.world import Action  # noqa: E402
from vomi.oracle import ExactOracle  # noqa: E402
from vomi.relational import (ProvenanceIndex, RelationCache, ReferentEngine, SPECS, j_commit,  # noqa: E402
                             search_value, term_label)

OUT = ROOT / "reports" / "hybrid-block"
QUAL_SEEDS = range(20261500, 20261504)  # qualification seeds (public draws only; every hidden world is enumerated)
SCRIPTS = {"seq": [[], ["wait()"], ["wait()", "wait()"], ["move(hall)"], ["move(hall)", "move(lobby)"]]}


def act(s: str) -> Action:
    m = re.match(r"(\w+)\((\w*)(?:,(\w+))?\)", s)
    return Action(m[1], m[2] or "", m[3] or "")


def history(sc, params, acts):
    w = sc.build(params)
    h = VisibleHistory(sc.brief, [(None, w.reset())])
    for a in acts:
        h.steps.append((act(a), w.step(act(a))))
    return w, h


def enum_route_p(o: ExactOracle, courier: str, cfg) -> float:
    """Independent calculation (public-model world enumeration): P(courier's route == recipient's room | h)."""
    other, fact = cfg.handoff_routes[courier]
    tot = 0.0
    for w, x in o.belief:
        m = x.minds[courier]
        d = m.beliefs.get(fact, "unknown") if not other else m.nested.get((other, fact), "unknown")
        tot += w * (d == x.people_rooms[cfg.recipient])
    return tot


def enum_loc(o: ExactOracle, cfg) -> dict:
    out = {}
    for w, x in o.belief:
        r = x.people_rooms[cfg.recipient]
        out[r] = out.get(r, 0.0) + w
    return out


def obs_key(h) -> str:
    return json.dumps(h.to_agent_dict(), sort_keys=True)


def timed(fn, reps=200):
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t)
    return statistics.median(ts) * 1e6  # microseconds


# ----------------------------------------------------------------------------- interface decision values
def options(eng: ReferentEngine, cfg, h, known: set, exact: bool):
    """Interface option values using only the computations in `known` ("L" = recipient-location marginal, courier
    names = relations). exact=True returns the true expected value of every option under the full posterior."""
    o = h.last
    room, remaining = o.room, cfg.horizon - o.t
    loc_t = eng.pm.recipient_loc(eng)
    loc = {k: float(v) for k, v in eng.dist(loc_t).items()}
    uniform = {x: 1 / len(cfg.offices) for x in cfg.offices}
    use_loc = exact or "L" in known
    opts = {"search": search_value(loc if use_loc else uniform, room, remaining, tuple(cfg.offices))}
    if exact:  # the declared search policy's true value is its value under the exact location posterior
        opts["search"] = search_value(loc, room, remaining, tuple(cfg.offices))
    if cfg.recipient in o.people_present:
        opts["deliver()"] = -0.05 + 1.0
    for c in cfg.handoff_routes:
        if c in o.people_present and (exact or c in known):
            opts[f"give({c})"] = j_commit(float(eng.p_equal(eng.route(c), loc_t)), cfg.stakes)
    if cfg.chute_room == room and use_loc:
        for x in cfg.offices:
            opts[f"drop({x})"] = j_commit(loc.get(x, 0.0), cfg.stakes)
    return opts


def choose(opts: dict) -> str:
    best = max(opts.values())
    return "search" if opts["search"] >= best - 1e-12 else max(opts, key=lambda k: (opts[k], k))


def voc_table(eng, cfg, h):
    """Exact decision value of each candidate computation for the shared interface, for two defaults:
    safe   - without a computation the interface cannot value that commitment, so it is not considered;
    commit - a proposed give(c) executes unless rel(c) is computed (the value of a check that can veto)."""
    exact = options(eng, cfg, h, set(), exact=True)
    base_known = set()
    cands = ["L"] + [c for c in cfg.handoff_routes if c in h.last.people_present]
    v0 = exact[choose(options(eng, cfg, h, base_known, False))]
    rows = {}
    for q in cands:
        v1 = exact[choose(options(eng, cfg, h, {q}, False))]
        rows[q] = {"safe_default_gain": round(v1 - v0, 6)}
        if q != "L":
            j = exact[f"give({q})"]
            alt = max(v for k, v in exact.items() if k != f"give({q})")
            rows[q]["commit_default_gain"] = round(max(0.0, alt - j), 6)
    vL = exact[choose(options(eng, cfg, h, {"L"}, False))]
    for q in cands[1:]:  # conditional marginal value of a relation once the location marginal is known
        rows[q]["safe_gain_given_L"] = round(exact[choose(options(eng, cfg, h, {"L", q}, False))] - vL, 6)
    allk = set(cands)
    rows["all"] = {"safe_default_gain": round(exact[choose(options(eng, cfg, h, allk, False))] - v0, 6)}
    return rows, {k: round(v, 6) for k, v in exact.items()}


# ----------------------------------------------------------------------------- main checks
def qualification():
    checks, mismatches, rows = 0, [], []
    boundary = {"history_equivalence_pairs": 0, "history_equivalence_violations": 0}
    for seed in QUAL_SEEDS:
        for case in F.cases(seed):
            sc, cfg_c = case.scenario, case.scenario.config
            for acts in SCRIPTS.get(case.construction, [[]]):
                by_hist = {}
                for params, _w in sc.prior:  # EVERY positive-prior hidden world, not one draw
                    try:
                        _, h = history(sc, params, acts)
                    except Exception:
                        continue
                    by_hist.setdefault(obs_key(h), (h, []))[1].append(params)
                for key, (h, plist) in by_hist.items():
                    o = ExactOracle(sc, h)
                    eng = ReferentEngine(SPECS[case.construction](cfg_c), ProvenanceIndex.build(h))
                    # boundary: every world with this visible history yields the identical engine output
                    out0 = None
                    for params in plist:
                        _, h2 = history(sc, params, acts)
                        e2 = ReferentEngine(SPECS[case.construction](cfg_c), ProvenanceIndex.build(h2))
                        sig = tuple((c, str(e2.p_equal(e2.route(c), e2.pm.recipient_loc(e2)))) for c in cfg_c.handoff_routes)
                        boundary["history_equivalence_pairs"] += 1
                        if out0 is None:
                            out0 = sig
                        elif sig != out0:
                            boundary["history_equivalence_violations"] += 1
                    loc_e = {k: float(v) for k, v in eng.dist(eng.pm.recipient_loc(eng)).items()}
                    loc_r = enum_loc(o, cfg_c)
                    checks += 1
                    if any(abs(loc_e.get(k, 0) - loc_r.get(k, 0)) > 1e-9 for k in set(loc_e) | set(loc_r)):
                        mismatches.append({"case": case.case_id, "acts": acts, "what": "loc", "engine": loc_e, "enum": loc_r})
                    for c in cfg_c.handoff_routes:
                        rt, lt = eng.route(c), eng.pm.recipient_loc(eng)
                        pj, pr = float(eng.p_equal(rt, lt)), enum_route_p(o, c, cfg_c)
                        checks += 1
                        if abs(pj - pr) > 1e-9:
                            mismatches.append({"case": case.case_id, "acts": acts, "courier": c, "engine": pj, "enum": pr})
                        if seed == QUAL_SEEDS[0] and case.stakes == 1.0:
                            lo, hi = eng.frechet(rt, lt)
                            rows.append({"construction": case.construction, "acts": acts, "courier": c,
                                         "route": term_label(rt), "recipient_loc": term_label(lt),
                                         "route_marginal": {k: str(v) for k, v in eng.dist(rt).items()},
                                         "loc_marginal": {k: str(v) for k, v in eng.dist(lt).items()},
                                         "p_joint": str(eng.p_equal(rt, lt)),
                                         "p_product": str(eng.p_equal_product(rt, lt)),
                                         "frechet": [str(lo), str(hi)], "hidden": dict(plist[0]),
                                         "provenance": list(eng.provenance(c, cfg_c.handoff_routes[c][1],
                                                                           cfg_c.handoff_routes[c][0]))})
    return checks, mismatches, rows, boundary


def static_boundary_scan():
    src = (ROOT / "src" / "vomi" / "relational.py").read_text(encoding="utf-8")
    code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
    code = re.sub(r'"""[\s\S]*?"""', "", code)
    banned = [r"\.minds\b", r"people_rooms", r"\.hidden\b", r"\bWorld\(", r"ExactOracle", r"\boracle\b", r"PersonMind",
              r"\.facts\b", r"timed_events", r"\bw(?:orld)?\.log\b", r"\bprivileged\b"]
    return {b: len(re.findall(b, code)) for b in banned}


def contrasts():
    """Representation necessity and evidence/consequence separation on fixed draws."""
    out = {}
    seed = QUAL_SEEDS[0]
    cs = {(c.construction, c.stakes): c for c in F.cases(seed)}
    for (con, st), case in sorted(cs.items()):
        if con == "seq":
            continue
        sc, cfg = case.scenario, case.scenario.config
        _, h = history(sc, case.hidden, [])
        eng = ReferentEngine(SPECS[con](cfg), ProvenanceIndex.build(h))
        o = ExactOracle(sc, h)
        lt = eng.pm.recipient_loc(eng)
        row = {"bayes_action": str(o.best_action(o.belief, h.last))}
        for c in cfg.handoff_routes:
            if c not in h.last.people_present:
                continue
            rt = eng.route(c)
            pj, pp = float(eng.p_equal(rt, lt)), float(eng.p_equal_product(rt, lt))
            loc = {k: float(v) for k, v in eng.dist(lt).items()}
            v_alt = search_value(loc, "lobby", cfg.horizon, tuple(cfg.offices))
            row[c] = {"p_joint": round(pj, 4), "p_product": round(pp, 4), "J_joint": round(j_commit(pj, st), 4),
                      "J_product": round(j_commit(pp, st), 4), "V_alt": round(v_alt, 4),
                      "gate_joint": "allow" if j_commit(pj, st) >= v_alt else "veto",
                      "gate_product": "allow" if j_commit(pp, st) >= v_alt else "veto"}
        out[f"{con}-x{st:g}"] = row
    # evidence-only vs person-state updates
    case = cs[("2d", 1.0)]
    sc, cfg = case.scenario, case.scenario.config
    H, N = case.names["H"], case.names["N"]
    _, h0 = history(sc, case.hidden, [])
    e0 = ReferentEngine(SPECS["2d"](cfg), ProvenanceIndex.build(h0))
    _, h1 = history(sc, case.hidden, [f"ask({H},{cfg.query_facts[0]})"])
    e1 = ReferentEngine(SPECS["2d"](cfg), ProvenanceIndex.build(h1))
    lt0, lt1 = e0.pm.recipient_loc(e0), e1.pm.recipient_loc(e1)
    out["evidence_only_update"] = {
        "event": f"robot asks {H} (answer heard)",
        "H_term_before": term_label(e0.route(H)), "H_term_after": term_label(e1.route(H)),
        "H_route_marginal_before": {k: str(v) for k, v in e0.dist(e0.route(H)).items()},
        "H_route_marginal_after": {k: str(v) for k, v in e1.dist(e1.route(H)).items()},
        "p_rel_N_before": str(e0.p_equal(e0.route(N), lt0)), "p_rel_N_after": str(e1.p_equal(e1.route(N), lt1)),
        "p_rel_H_before": str(e0.p_equal(e0.route(H), lt0)), "p_rel_H_after": str(e1.p_equal(e1.route(H), lt1)),
        "recipient_marginal_after": {k: str(v) for k, v in e1.dist(lt1).items()}}
    # person-state change (seq, return observed) vs reuse (seq, no return) vs unobserved interval
    seqs = {}
    for case in [c for c in F.cases(seed) if c.construction == "seq" and c.stakes == 1.0]:
        sc, cfg = case.scenario, case.scenario.config
        for ret in ("yes", "no"):
            params = tuple((k, ret if k == "ret" else v) for k, v in case.hidden)
            for label, acts in (("watch", ["wait()", "wait()"]), ("away_t1", ["move(hall)", "move(lobby)"])):
                cache = RelationCache()
                ops = []
                for k in range(len(acts) + 1):
                    _, h = history(sc, params, acts[:k])
                    eng = ReferentEngine(SPECS["seq"](cfg), ProvenanceIndex.build(h))
                    for c in sorted(cfg.handoff_routes):
                        rec, op = cache.get(c, eng)
                        fresh = eng.p_equal(eng.route(c), eng.pm.recipient_loc(eng))
                        ops.append({"t": k, "courier": c, "op": op, "p": str(rec.p), "route": rec.route_term,
                                    "loc": rec.loc_term, "reused_equals_fresh": rec.p == fresh})
                o = ExactOracle(sc, h)
                seqs[f"ret={ret}/{label}"] = {"ops": ops, "bayes_action_t2": str(o.best_action(o.belief, h.last)),
                                              "present_t2": list(h.last.people_present)}
    out["reuse_refresh"] = seqs
    return out


def voc_structure():
    rows = []
    seed = QUAL_SEEDS[0]
    for case in F.cases(seed):
        sc, cfg = case.scenario, case.scenario.config
        for acts in ([["wait()", "wait()"], ["move(hall)", "move(lobby)"]] if case.construction == "seq" else [[]]):
            for params in ([tuple((k, r if k == "ret" else v) for k, v in case.hidden) for r in ("yes", "no")]
                           if case.construction == "seq" else [case.hidden]):
                _, h = history(sc, params, acts)
                eng = ReferentEngine(SPECS[case.construction](cfg), ProvenanceIndex.build(h))
                table, exact = voc_table(eng, cfg, h)
                rows.append({"construction": case.construction, "stakes": case.stakes, "acts": acts,
                             "hidden": dict(params), "present": list(h.last.people_present), "voc": table,
                             "exact_option_values": exact})
    return rows


def costs():
    seed = QUAL_SEEDS[0]
    out = {}
    for case in F.cases(seed):
        if case.stakes != 1.0:
            continue
        sc, cfg = case.scenario, case.scenario.config
        _, h = history(sc, case.hidden, [])
        spec = SPECS[case.construction]
        couriers = list(cfg.handoff_routes)

        def one():
            e = ReferentEngine(spec(cfg), ProvenanceIndex.build(h))
            e.p_equal(e.route(couriers[0]), e.pm.recipient_loc(e))

        def dense():
            e = ReferentEngine(spec(cfg), ProvenanceIndex.build(h))
            lt = e.pm.recipient_loc(e)
            e.dist(lt)
            for c in couriers:
                e.p_equal(e.route(c), lt)

        def enum():
            o = ExactOracle(sc, h)
            for c in couriers:
                enum_route_p(o, c, cfg)

        out[case.construction] = {"index_us": round(timed(lambda: ProvenanceIndex.build(h)), 1),
                                  "one_relation_us": round(timed(one), 1), "dense_all_us": round(timed(dense), 1),
                                  "world_enumeration_us": round(timed(enum, 50), 1), "n_worlds": len(sc.prior)}
    # the fallback's deployed checker on the 12 dev-v3 constructions (public-model enumeration at t0)
    dev = {}
    for inst in G.generate(20261500):
        if inst.variant.permuted or inst.variant.stakes != 1.0:
            continue
        w = inst.scenario.build(inst.hidden)
        h = VisibleHistory(inst.scenario.brief, [(None, w.reset())])
        dev[inst.construction] = {"world_enumeration_us": round(timed(lambda: ExactOracle(inst.scenario, h), 30), 1),
                                  "n_worlds": len(inst.scenario.prior)}
    return out, dev


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    checks, mism, rows, boundary = qualification()
    scan = static_boundary_scan()
    con = contrasts()
    voc = voc_structure()
    cost, devcost = costs()
    res = {"qualification": {"checks": checks, "mismatches": mism, "rows_seed0": rows, "seeds": list(QUAL_SEEDS)},
           "boundary": {**boundary, "static_scan_relational_py": scan}, "contrasts": con, "voc": voc,
           "costs_family_us": cost, "costs_devv3_checker_us": devcost, "wall_s": round(time.monotonic() - t0, 1)}
    (OUT / "cpu-gate.json").write_bytes(json.dumps(res, indent=1, default=str).encode("utf-8"))
    print(json.dumps({"checks": checks, "mismatches": len(mism), "boundary": boundary, "scan": scan,
                      "wall_s": res["wall_s"]}, indent=1))


if __name__ == "__main__":
    main()
