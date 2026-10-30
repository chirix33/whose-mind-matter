"""G1 symbolic twin of "cheap provenance, costly content" (D-023; protocol reports/g1/G1_PROTOCOL.md). CPU only.

    python3 scripts/g1_symbolic_twin.py freeze    # g1-freeze.json (clean tree): code + protocol hashes
    python3 scripts/g1_symbolic_twin.py run       # the ONE evaluation pass -> reports/g1/g1-results.json
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import random
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vomi.relational import j_commit, search_value  # noqa: E402

OUT = ROOT / "reports" / "g1"
OFFICES = ("o1", "o2", "o3")
COURIERS = ("c1", "c2")
HORIZON = 8
STAKES = (1.0, 4.0)
Q_SET = (0.1, 0.3, 0.5)
L_SET = (0, 1, 2, 3)
CONDITIONS = {"sparse": {"others": 8, "K": 3}, "dense": {"others": 3, "K": 4}}
DAYS = 2000
SEED0, PSEED0 = 20261600, 20262600
PERSP_CHAINS, PERSP_VARIANTS = 500, 4
LAMBDAS = (0.005, 0.01, 0.02, 0.04, 0.08, 0.16)
LAMBDA_OP = 0.04
THETAS = (0.05, 0.1, 0.2, 0.4, 0.8, 1.6)
BOOT = 2000
TOL = 1e-12


# ----------------------------------------------------------------------------- world
@dataclass
class Person:
    name: str
    a: str  # public announcement
    q: float  # public change rate
    listeners: list  # PUBLIC provenance: listener of message j (1-based order)
    contents: list  # PRIVATE: Y_1..Y_L

    @property
    def L(self) -> int:
        return len(self.listeners)

    def loc(self) -> str:
        return self.contents[-1] if self.contents else self.a


@dataclass
class Day:
    people: dict
    recipients: list
    messages: list = field(default_factory=list)  # (speaker, j, listener) for every message of the day

    def __post_init__(self):
        self.messages = [(p.name, j + 1, p.listeners[j]) for p in self.people.values() for j in range(p.L)]


def next_content(rng, prev, q):
    if rng.random() < 1 - q:
        return prev
    return rng.choice([o for o in OFFICES if o != prev])


def make_person(rng, name, cast, L=None):
    a = rng.choice(OFFICES)
    q = rng.choice(Q_SET)
    L = rng.choice(L_SET) if L is None else L
    listeners = [rng.choice([x for x in cast if x != name]) for _ in range(L)]
    contents, prev = [], a
    for _ in range(L):
        prev = next_content(rng, prev, q)
        contents.append(prev)
    return Person(name, a, q, listeners, contents)


def make_day(cond: str, d: int) -> Day:
    rng = random.Random(f"G1:{cond}:{SEED0 + d}")
    n, K = CONDITIONS[cond]["others"], CONDITIONS[cond]["K"]
    others = [f"p{i}" for i in range(n)]
    cast = list(COURIERS) + others
    people = {p: make_person(rng, p, cast) for p in others}
    recipients = [rng.choice(others) for _ in range(K)]
    return Day(people, recipients)


def heard_index(p: Person, x: str) -> int:
    """Index (1-based) of the latest p-message x heard; 0 = only the public announcement (PUBLIC provenance)."""
    js = [j + 1 for j, lis in enumerate(p.listeners) if lis == x]
    return max(js) if js else 0


# ----------------------------------------------------------------------------- posterior (public model + reads)
def chain_worlds(p: Person, known: dict) -> list:
    """Exact posterior over p's contents given the public model and read contents {j: value}."""
    rows = [((), 1.0)]
    for j in range(1, p.L + 1):
        new = []
        for ys, w in rows:
            prev = ys[-1] if ys else p.a
            for y in OFFICES:
                pw = (1 - p.q) if y == prev else p.q / 2
                if j in known and known[j] != y:
                    continue
                new.append((ys + (y,), w * pw))
        rows = new
    tot = sum(w for _, w in rows)
    return [(ys, w / tot) for ys, w in rows]


def value(p: Person, known: dict, stakes: float, couriers=COURIERS):
    """Interface value and chosen option under the posterior (exact)."""
    ws = chain_worlds(p, known)
    loc = {}
    for ys, w in ws:
        l = ys[-1] if ys else p.a
        loc[l] = loc.get(l, 0.0) + w
    best, opt = search_value(loc, "lobby", HORIZON, OFFICES), "search"
    for c in couriers:
        jc = heard_index(p, c)
        pc = sum(w for ys, w in ws if (ys[jc - 1] if jc else p.a) == (ys[-1] if ys else p.a))
        jv = j_commit(pc, stakes)
        if jv > best + TOL:
            best, opt = jv, f"give({c})"
    return best, opt, loc


def voi(p: Person, known: dict, S: tuple, stakes: float) -> float:
    base, _, _ = value(p, known, stakes)
    ws = chain_worlds(p, known)
    groups = {}
    for ys, w in ws:
        groups[tuple(ys[j - 1] for j in S)] = groups.get(tuple(ys[j - 1] for j in S), 0.0) + w
    tot = 0.0
    for vals, w in groups.items():
        k2 = dict(known)
        k2.update(dict(zip(S, vals)))
        tot += w * value(p, k2, stakes)[0]
    return tot - base


def realized(p: Person, known: dict, stakes: float) -> tuple[float, str]:
    _, opt, loc = value(p, known, stakes)
    true = p.loc()
    if opt.startswith("give"):
        c = opt[5:-1]
        jc = heard_index(p, c)
        dest = p.contents[jc - 1] if jc else p.a
        return (-0.05 + 1.0, opt) if dest == true else (-0.05 - 0.5 * stakes, opt)
    order = sorted(OFFICES, key=lambda o: (-loc.get(o, 0.0), OFFICES.index(o)))
    steps = 2 + 2 * order.index(true) + 1
    return (1 - 0.05 * steps if steps <= HORIZON else -0.05 * HORIZON), opt


def entropy_of(ws, j):
    d = {}
    for ys, w in ws:
        d[ys[j - 1]] = d.get(ys[j - 1], 0.0) + w
    return -sum(x * math.log2(x) for x in d.values() if x > 0)


# ----------------------------------------------------------------------------- selectors -> reads of p's chain
def sel_dv(p, known, stakes, lam):
    known = dict(known)
    bought = []
    while True:
        unread = [j for j in range(1, p.L + 1) if j not in known]
        opts = [(j,) for j in unread] + list(itertools.combinations(unread, 2))
        best = None
        for S in opts:
            net = voi(p, known, S, stakes) - lam * len(S)
            key = (-net, len(S), S)
            if net > TOL and (best is None or key < best[0]):
                best = (key, S)
        if best is None:
            return bought
        for j in best[1]:
            known[j] = p.contents[j - 1]  # reading reveals the true content
            bought.append(j)


def sel_latest(p, known, stakes):
    return [p.L] if p.L and p.L not in known else []


def sel_action_prov(p, known, stakes):
    if p.L == 0:
        return []
    hs = {c: heard_index(p, c) for c in COURIERS}
    if any(h == p.L for h in hs.values()):
        return []  # provenance establishes alignment without revealing the value
    cstar = max(COURIERS, key=lambda c: (hs[c], c == "c1"))
    want = [p.L] + ([hs[cstar]] if hs[cstar] >= 1 else [])
    return [j for j in want if j not in known]


def sel_risk(p, known, stakes, theta):
    if p.L == 0:
        return []
    n = p.L - max(heard_index(p, c) for c in COURIERS)
    risk = (1 - (1 - p.q) ** n) * (1 + 0.5 * stakes)
    return [p.L] if risk > theta and p.L not in known else []


def sel_entropy(p, known, stakes, B):
    known = dict(known)
    out = []
    for _ in range(B):
        unread = [j for j in range(1, p.L + 1) if j not in known]
        if not unread:
            break
        ws = chain_worlds(p, known)
        j = max(unread, key=lambda j: (round(entropy_of(ws, j), 12), j))
        known[j] = p.contents[j - 1]
        out.append(j)
    return out


def sel_random(p, known, stakes, B, rng):
    unread = [j for j in range(1, p.L + 1) if j not in known]
    return rng.sample(unread, min(B, len(unread)))


SELECTORS = (["none", "dense", "structural", "latest", "action_prov"] + [f"risk:{t}" for t in THETAS]
             + ["entropy:1", "entropy:2", "random:1", "random:2"] + [f"dv:{l}" for l in LAMBDAS])


def run_day(day: Day, cond: str, d: int, stakes: float, sel: str) -> dict:
    """One day under one selector at one stakes level: per-task realized return, reads, first-task flags."""
    cache = {}  # (speaker, j) -> content
    if sel == "dense":
        for s, j, _ in day.messages:
            cache[(s, j)] = day.people[s].contents[j - 1]
    tasks = []
    seen = set()
    for t, R in enumerate(day.recipients):
        p = day.people[R]
        if sel == "structural":
            for s, j, lis in day.messages:
                if s == R or lis == R or lis in COURIERS:
                    cache[(s, j)] = day.people[s].contents[j - 1]
        known = {j: v for (s, j), v in cache.items() if s == R}
        first = R not in seen
        seen.add(R)
        if sel.startswith("dv:"):
            reads = sel_dv(p, known, stakes, float(sel[3:]))
        elif sel == "latest":
            reads = sel_latest(p, known, stakes)
        elif sel == "action_prov":
            reads = sel_action_prov(p, known, stakes)
        elif sel.startswith("risk:"):
            reads = sel_risk(p, known, stakes, float(sel[5:]))
        elif sel.startswith("entropy:"):
            reads = sel_entropy(p, known, stakes, int(sel[8:]))
        elif sel.startswith("random:"):
            reads = sel_random(p, known, stakes, int(sel[7:]), random.Random(f"G1:rand:{cond}:{d}:{t}:{sel}:{stakes}"))
        else:
            reads = []
        new_reads = [j for j in reads if j not in known]
        for j in reads:
            cache[(R, j)] = p.contents[j - 1]
            known[j] = p.contents[j - 1]
        ret, opt = realized(p, known, stakes)
        tasks.append({"R": R, "first": first, "new_reads": len(new_reads), "return": ret, "option": opt})
    return {"reads": len(cache), "tasks": tasks}


# ----------------------------------------------------------------------------- evaluation
def evaluate_condition(cond: str) -> dict:
    days = [make_day(cond, d) for d in range(DAYS)]
    n_msgs = [len(day.messages) for day in days]
    per = {}  # sel -> stakes -> list of day records
    for sel in SELECTORS:
        per[sel] = {s: [run_day(day, cond, d, s, sel) for d, day in enumerate(days)] for s in STAKES}
    # initial-state values for G1c (first task of each recipient), exact
    init = []
    for d, day in enumerate(days):
        seen = set()
        for t, R in enumerate(day.recipients):
            if R in seen:
                continue
            seen.add(R)
            p = day.people[R]
            for s in STAKES:
                v_none = value(p, {}, s)[0]
                v_full = value(p, {j: p.contents[j - 1] for j in range(1, p.L + 1)}, s)[0]
                init.append({"day": d, "task": t, "stakes": s, "gap": v_full - v_none})
    return {"days": days, "n_msgs": n_msgs, "per": per, "init": init}


def day_return(rec_by_stakes, d):
    vals = [t["return"] for s in STAKES for t in rec_by_stakes[s][d]["tasks"]]
    return statistics.mean(vals)


def day_reads(rec_by_stakes, d):
    return statistics.mean(rec_by_stakes[s][d]["reads"] for s in STAKES)


def summarize(ev: dict) -> dict:
    D = len(ev["days"])
    out = {}
    for sel, rec in ev["per"].items():
        rets = [day_return(rec, d) for d in range(D)]
        reads = [day_reads(rec, d) for d in range(D)]
        out[sel] = {"return": statistics.mean(rets), "reads_per_day": statistics.mean(reads),
                    "U": sum(reads) / sum(ev["n_msgs"]),
                    "by_stakes": {f"x{s:g}": {"return": statistics.mean(t["return"] for d in range(D)
                                                                      for t in rec[s][d]["tasks"]),
                                              "reads_per_day": statistics.mean(rec[s][d]["reads"] for d in range(D))}
                                  for s in STAKES},
                    "_day_returns": rets}
    return out


def paired_ci(a, b, seed=0):
    rng = random.Random(seed)
    diff = [x - y for x, y in zip(a, b)]
    n = len(diff)
    bs = sorted(statistics.mean(diff[rng.randrange(n)] for _ in range(n)) for _ in range(BOOT))
    return statistics.mean(diff), bs[int(0.025 * BOOT)], bs[int(0.975 * BOOT) - 1]


def perspective_set() -> dict:
    rows = []
    for i in range(PERSP_CHAINS):
        rng = random.Random(f"G1:persp:{PSEED0 + i}")
        cast = list(COURIERS) + [f"p{k}" for k in range(8)]
        base = make_person(rng, "p0", cast, L=rng.choice((1, 2, 3)))
        variants = []
        for v in range(PERSP_VARIANTS):
            vr = random.Random(f"G1:persp:{PSEED0 + i}:aud:{v}")
            lis = [vr.choice([x for x in cast if x != "p0"]) for _ in range(base.L)]
            variants.append(Person("p0", base.a, base.q, lis, list(base.contents)))
        rec = {"chain": i, "L": base.L, "variants": []}
        for p in variants:
            vrec = {"listeners": p.listeners}
            for s in STAKES:
                for name, f in (("dv", lambda p, known, s: sel_dv(p, known, s, LAMBDA_OP)), ("latest", sel_latest),
                                ("action_prov", sel_action_prov)):
                    reads = f(p, {}, s)
                    known = {j: p.contents[j - 1] for j in reads}
                    vrec[f"{name}@x{s:g}"] = {"reads": sorted(reads), "return": realized(p, known, s)[0]}
            rec["variants"].append(vrec)
        rec["dv_set_differs"] = any(len({tuple(v[f"dv@x{s:g}"]["reads"]) for v in rec["variants"]}) > 1
                                    for s in STAKES)
        rows.append(rec)
    agg = {}
    for name in ("dv", "latest", "action_prov"):
        vals = [v[f"{name}@x{s:g}"] for r in rows for v in r["variants"] for s in STAKES]
        agg[name] = {"return": statistics.mean(x["return"] for x in vals),
                     "reads_per_task": statistics.mean(len(x["reads"]) for x in vals)}
    return {"rows": rows, "share_dv_set_differs": statistics.mean(r["dv_set_differs"] for r in rows), "agg": agg}


def gates(sp: dict, ev_sparse: dict, persp: dict) -> dict:
    op = sp[f"dv:{LAMBDA_OP}"]
    g = {}
    # G1a
    U, ret_ok = op["U"], op["return"] >= sp["dense"]["return"] - 0.02
    g["G1a"] = {"U": U, "return_dv": op["return"], "return_dense": sp["dense"]["return"],
                "verdict": "pass" if U <= 0.35 and ret_ok else ("stop" if U > 0.60 else "inconclusive")}
    # G1b
    cheap = [k for k in sp if k != "dense" and not k.startswith("dv:")]
    rows, match, all_ok = [], [], True
    for b in cheap:
        mean, lo, hi = paired_ci(op["_day_returns"], sp[b]["_day_returns"])
        fewer = sp[b]["reads_per_day"] <= 1.1 * op["reads_per_day"]
        m = fewer and sp[b]["return"] >= op["return"] - 0.02
        ok = (lo > 0.02) if fewer else (sp[b]["return"] <= op["return"] + 0.02)
        rows.append({"selector": b, "reads_per_day": sp[b]["reads_per_day"], "return": sp[b]["return"],
                     "dv_minus_b": mean, "ci95": [lo, hi], "reads_le_1.1x_dv": fewer, "matches_dv": m, "dv_ok": ok})
        if m:
            match.append(b)
        all_ok &= ok
    g["G1b"] = {"rows": rows, "matching_rules": match,
                "verdict": "stop" if match else ("pass" if all_ok else "inconclusive")}
    # G1c / G1d over comparable initial states (first task of each recipient)
    init = ev_sparse["init"]
    share_gap = statistics.mean(x["gap"] >= 0.10 for x in init)
    g["G1c"] = {"share_gap_ge_0.10": share_gap, "states": len(init), "verdict": "pass" if share_gap >= 0.30 else "stop"}
    recs = ev_sparse["per"][f"dv:{LAMBDA_OP}"]
    stop_flags, flips = [], []
    for d, day in enumerate(ev_sparse["days"]):
        for t, R in enumerate(day.recipients):
            first = recs[STAKES[0]][d]["tasks"][t]["first"]
            if not first:
                continue
            reads_s = [recs[s][d]["tasks"][t]["new_reads"] > 0 for s in STAKES]
            stop_flags += [not r for r in reads_s]
            flips.append(reads_s[0] != reads_s[1])
    stop_share, flip_share = statistics.mean(stop_flags), statistics.mean(flips)
    reuse = [t for s in STAKES for dd in recs[s] for t in dd["tasks"] if not t["first"]]
    g["G1d"] = {"stop_share": stop_share, "stakes_flip_share": flip_share, "states": len(stop_flags),
                "repeat_recipient_tasks": len(reuse),
                "verdict": "pass" if 0.20 <= stop_share <= 0.90 and flip_share >= 0.05 else "stop"}
    # G1e
    a = persp["agg"]
    dret = a["dv"]["return"] - a["latest"]["return"]
    rr = a["dv"]["reads_per_task"] / a["latest"]["reads_per_task"] if a["latest"]["reads_per_task"] else float("inf")
    beat = (dret >= 0.02 and rr <= 1.1) or (rr <= 0.6 and dret >= -0.01)
    g["G1e"] = {"share_dv_set_differs": persp["share_dv_set_differs"], "dv_minus_latest_return": dret,
                "dv_over_latest_reads": rr,
                "verdict": "pass" if persp["share_dv_set_differs"] >= 0.20 and beat else "stop"}
    vs = [g[k]["verdict"] for k in ("G1a", "G1b", "G1c", "G1d", "G1e")]
    g["overall"] = "PASS" if all(v == "pass" for v in vs) else ("STOP" if "stop" in vs else "INCONCLUSIVE")
    return g


# ----------------------------------------------------------------------------- stages
CODE_FILES = ("scripts/g1_symbolic_twin.py", "src/vomi/relational.py", "reports/g1/G1_PROTOCOL.md")


def sha_file(f):
    return hashlib.sha256((ROOT / f).read_bytes()).hexdigest()


def stage_freeze():
    dirty = [x for x in os.popen(f'git -C "{ROOT}" status --porcelain').read().split("\n") if x.strip()]
    if dirty:
        raise SystemExit(f"freeze needs a clean tree: {dirty}")
    fz = {"block": "D-023 G1", "git_commit": os.popen(f'git -C "{ROOT}" rev-parse HEAD').read().strip(),
          "sha256": {f: sha_file(f) for f in CODE_FILES}, "conditions": CONDITIONS, "days": DAYS, "seed0": SEED0,
          "persp": [PSEED0, PERSP_CHAINS, PERSP_VARIANTS], "lambdas": LAMBDAS, "lambda_op": LAMBDA_OP,
          "thetas": THETAS, "selectors": SELECTORS, "bootstrap": BOOT}
    (OUT / "g1-freeze.json").write_bytes(json.dumps(fz, indent=1).encode("utf-8"))
    print(json.dumps(fz, indent=1))


def stage_run():
    fz = json.loads((OUT / "g1-freeze.json").read_text())
    bad = {f: h for f, h in fz["sha256"].items() if sha_file(f) != h}
    if bad:
        raise SystemExit(f"code differs from freeze: {bad}")
    if (OUT / "g1-results.json").exists():
        raise SystemExit("g1-results.json exists: one evaluation pass only")
    t0 = time.process_time()
    w0 = time.monotonic()
    evs = {c: evaluate_condition(c) for c in CONDITIONS}
    sums = {c: summarize(evs[c]) for c in CONDITIONS}
    persp = perspective_set()
    g = gates(sums["sparse"], evs["sparse"], persp)
    strip = lambda s: {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in s.items()}  # noqa: E731
    res = {"freeze_commit": fz["git_commit"], "gates": g, "summary": {c: strip(sums[c]) for c in CONDITIONS},
           "messages_per_day": {c: statistics.mean(evs[c]["n_msgs"]) for c in CONDITIONS},
           "perspective": {"share_dv_set_differs": persp["share_dv_set_differs"], "agg": persp["agg"],
                           "examples": persp["rows"][:20]},
           "cpu_s": round(time.process_time() - t0, 1), "wall_s": round(time.monotonic() - w0, 1)}
    (OUT / "g1-results.json").write_bytes(json.dumps(res, indent=1, default=str).encode("utf-8"))
    print(json.dumps({"gates": {k: (v if k == "overall" else v["verdict"]) for k, v in g.items()},
                      "cpu_s": res["cpu_s"]}, indent=1))


if __name__ == "__main__":
    {"freeze": stage_freeze, "run": stage_run}[sys.argv[1]]()
