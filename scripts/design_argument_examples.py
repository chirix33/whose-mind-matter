"""D-021 design argument: exact worked examples for "cheap provenance, costly content" (CPU only; no model calls).

Tiny case (all numbers exact under the stated model):
  - Offices a, b, c. R publicly announced a, then in transcript t3 told courier F (only) the office m in {b, c} R was
    moving to (uniform). F forwards to m.
  - Provenance (cheap; message headers / presence): the robot knows WHO talked to WHOM and WHEN, not WHAT was said.
  - Optionally R later had transcript t7 with X (header visible). Under the public model, t7 states either "staying"
    (prob 1-q) or "moving to <the other of b, c>" (prob q); R then goes there. F did not hear t7.
  - N_other transcripts among other people carry no information about R under the public model.
  - Reading a transcript's CONTENT costs one model extraction call (cost c tokens); headers cost ~0.
  - The robot is in the lobby with F, holding the package; actions after reading: give(F), or search in person
    (declared search: most probable office first), horizon 8, stakes s.
For each case: exact value of the best interface action for every read set, the decision value (VOI) of each read,
the read chosen by decision value vs by content entropy vs by a structural rule, and what dense reading costs.

    python3 scripts/design_argument_examples.py
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vomi.relational import j_commit, search_value  # noqa: E402

OFFICES = ("a", "b", "c")


def worlds(q: float, has_t7: bool):
    """(prob, m, final location, content_t3, content_t7)."""
    out = []
    for m in ("b", "c"):
        other = "c" if m == "b" else "b"
        if not has_t7:
            out.append((0.5, m, m, m, None))
            continue
        out.append((0.5 * (1 - q), m, m, m, "stay"))
        if q > 0:
            out.append((0.5 * q, m, other, m, f"move:{other}"))
    return out


def best_value(ws, stakes):
    """Expected return of the best interface action given the (sub)posterior ws (list of (w, m, loc, ...))."""
    tot = sum(w for w, *_ in ws)
    p_align = sum(w for w, m, loc, *_ in ws if m == loc) / tot
    loc = {}
    for w, m, l, *_ in ws:
        loc[l] = loc.get(l, 0.0) + w / tot
    give = j_commit(p_align, stakes)
    search = search_value(loc, "lobby", 8, OFFICES)
    return max(give, search), ("give(F)" if give > search else "search")


def value_of_reads(q, stakes, reads, has_t7):
    ws = worlds(q, has_t7)
    key = lambda x: tuple(x[3] if r == "t3" else x[4] for r in reads)  # noqa: E731
    groups = {}
    for x in ws:
        groups.setdefault(key(x), []).append(x)
    v = 0.0
    acts = {}
    for k, g in groups.items():
        bv, a = best_value(g, stakes)
        v += sum(w for w, *_ in g) * bv
        acts[str(k)] = a
    return v, acts


def entropy(ws, idx):
    d = {}
    for x in ws:
        d[x[idx]] = d.get(x[idx], 0.0) + x[0]
    return -sum(p * math.log2(p) for p in d.values() if p > 0)


def case(name, q, stakes, has_t7, lam_c, n_other=8):
    ws = worlds(q, has_t7)
    avail = ["t3"] + (["t7"] if has_t7 else [])
    vals = {}
    for k in range(len(avail) + 1):
        for S in itertools.combinations(avail, k):
            vals[",".join(S) or "none"] = value_of_reads(q, stakes, list(S), has_t7)
    v0 = vals["none"][0]
    voi = {r: round(vals[r][0] - v0, 4) for r in avail}
    ent = {"t3": round(entropy(ws, 3), 4)}
    if has_t7:
        ent["t7"] = round(entropy(ws, 4), 4)
    net = {r: voi[r] - lam_c for r in avail}
    best = max(net, key=net.get)
    dv_choice = best if net[best] > 1e-12 else "STOP"
    return {"case": name, "q_change": q, "stakes": stakes, "t7_header_present": has_t7,
            "lambda_times_c": lam_c, "values_by_read_set": {k: round(v[0], 4) for k, v in vals.items()},
            "actions_by_read_set": {k: v[1] for k, v in vals.items()},
            "voi": voi, "content_entropy_bits": ent,
            "decision_value_choice": dv_choice,
            "entropy_choice": max(ent, key=ent.get),
            "structural_rule_reads": avail,  # "read every transcript involving R or a courier"
            "dense_reads": len(avail) + n_other,
            "reads_by_decision_value": 0 if dv_choice == "STOP" else 1}


def main():
    LC = 0.04  # planning operating point: one extraction call priced at 0.04 return units (see DESIGN_ARGUMENT §2)
    cases = [case("E1 later conversation, uncertain change", 0.5, 1.0, True, LC),
             case("E1 later conversation, uncertain change", 0.5, 4.0, True, LC),
             case("E2 no later conversation (provenance settles it)", 0.0, 1.0, False, LC),
             case("E3 rare change: stakes decide READ vs STOP", 0.02, 1.0, True, LC),
             case("E3 rare change: stakes decide READ vs STOP", 0.02, 4.0, True, LC),
             case("E4 decision value vs entropy", 0.2, 1.0, True, LC)]
    # E5: amortization kill case. A day of K tasks over one fixed log of T transcripts; task k needs transcript set N_k.
    T = 10
    needs = [{"t7"}, {"t7", "t9"}, {"t2"}, {"t4", "t5"}, {"t1", "t3", "t6", "t8", "t10"}]
    union = set().union(*needs)
    e5 = {"case": "E5 dense amortizes when relevance covers the log", "transcripts": T,
          "reads_selective_union": len(union), "reads_dense_once": T, "saving": round(1 - len(union) / T, 3),
          "note": "with encode-once caching, selective saves only transcripts never needed during the episode"}
    out = {"cases": cases, "amortization": e5}
    (ROOT / "reports" / "design-argument").mkdir(parents=True, exist_ok=True)
    (ROOT / "reports" / "design-argument" / "examples.json").write_bytes(json.dumps(out, indent=1).encode("utf-8"))
    for c in cases:
        print(f"{c['case'][:48]:48s} s={c['stakes']:g} values={c['values_by_read_set']} voi={c['voi']} "
              f"H={c['content_entropy_bits']} DV={c['decision_value_choice']} entropy={c['entropy_choice']}")
    print(e5)


if __name__ == "__main__":
    main()
