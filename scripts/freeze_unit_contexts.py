"""Freeze ~24 fixed unit-inference contexts for the model/package diagnostic (pilot review, 2026-10-28).

Declared selection rule (applied before any new model output):
  Pool: every dev-v2 instance at two history prefixes. k=0 is the initial observation. k=1 adds the
        first action of that instance's pilot-v1 DIRECT-arm episode (a realized legal history from the
        stored run). Units are the visible candidates at that prefix.
  1. The 9 prespecified pilot intervention states (k=0, given unit) are always included.
  2. The pool is walked in sha256 order of "instance|k|unit" in fixed passes. Each pass accepts items
     matching its predicate until its target count is reached, under global constraints:
       - at most one context per group (no near-duplicate variants);
       - at most 4 contexts per family (3 in the first draft left R1 at 1 of 4; changed before any output);
       - 24 contexts in total.
     Passes, in order (targets are minimum counts over the whole set):
       R2 units >= 2; R1 units >= 4; K2 units >= 6; truth "unknown" >= 5;
       default-violating content (false belief / misjudgment / obstruction) >= 4; k=1 >= 8; then any.
  The truth-based passes read PRIVILEGED annotations only to guarantee coverage (as the review asked:
  unknown truths, false beliefs, nested units). No model output influences selection.

Outputs:
  reports/pilot/unit-contexts-v1.jsonl   VISIBLE ONLY: ids, history, rendered requests for both
                                         packages at renderer r3, schemas, visible evidence IDs
  data/pilot/unit-contexts-v1-privileged.jsonl   truth, evidence posterior, robot-known values, default
                                         flags, and the original pilot-v1 (r2) stored output where it exists
  reports/pilot/unit-contexts-v1.md      selection summary + hashes
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds.devgen import generate  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.world import legal_actions  # noqa: E402
from vomi.fidelity import evidence_posterior, robot_known_values  # noqa: E402
from vomi.pilot import PACKAGES, RENDER_REVISION, ledger, load_prompts, unit_messages  # noqa: E402
from vomi.units import Unit, content, default_holds, generate_candidates  # noqa: E402

PILOT_RUN = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "pilot" / "pilot-full-20261028-060517-3237fb"
N_TOTAL, PER_FAMILY = 24, 4  # cap 3 -> 4 before any output: with 3, the R1 and default-violating targets could not be met
PASSES = [("R2", 2), ("R1", 4), ("K2", 6), ("truth_unknown", 5), ("default_violating", 4), ("k1", 8), ("any", N_TOTAL)]


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def utype(u: Unit) -> str:
    return f"{u.variable[0].upper()}{u.depth}"


def parse_unit(s: str) -> Unit:
    return Unit(tuple(s[2:-1].split("->")), "knowledge" if s.startswith("K(") else "reliability")


def main():
    insts = {i.instance_id: i for i in generate(version="dev-v2")}
    eps = [json.loads(l) for l in (PILOT_RUN / "episodes.jsonl").open()]
    first_action = {e["instance_id"]: e["actions"][0] for e in eps if e["arm"] == "direct" and e["actions"]}
    stored = {}  # (instance, unit) -> original pilot-v1 output from the dense arm at step 0
    for e in eps:
        if e["arm"] == "dense":
            for c in e["calls"]:
                if c["kind"] == "unit" and c["step"] == 0:
                    stored[(e["instance_id"], c["target"])] = {"ok": c["ok"], "parsed": c["parsed"],
                                                               "attempts": len(c["attempts"])}
    interventions = json.loads((ROOT / "data" / "pilot" / "dev-v2" / "interventions.json").read_text())

    def build(iid, k):
        inst = insts[iid]
        w = inst.scenario.build(inst.hidden)
        h = VisibleHistory(inst.scenario.brief, [(None, w.reset())])
        if k == 1:
            a = next(x for x in legal_actions(inst.scenario.config, h.last) if str(x) == first_action[iid])
            h.steps.append((a, w.step(a)))
        return inst, w, h

    def item(iid, k, u):
        inst, w, h = build(iid, k)
        truth = content(w, u)[0]
        return {"instance_id": iid, "group_id": iid.rsplit("-", 1)[0] if inst.family == "stop" else inst.group_id,
                "family": inst.family, "k": k, "unit": str(u), "unit_type": utype(u), "truth": truth,
                "default_violating": not default_holds(w, u)}

    chosen = [item(iv["instance_id"], 0, parse_unit(iv["unit"])) for iv in interventions]
    for c in chosen:
        c["source"] = "prespecified_intervention"
    pool = []
    for iid, inst in insts.items():
        for k in (0, 1):
            if k == 1 and (iid not in first_action or build(iid, 0)[2].last.done):
                continue
            _, _, h = build(iid, k)
            if h.last.done:
                continue
            for u in generate_candidates(inst.scenario.config, h):
                pool.append((sha(f"{iid}|{k}|{u}"), iid, k, u))
    pool.sort()
    preds = {"R2": lambda x: x["unit_type"] == "R2", "R1": lambda x: x["unit_type"] == "R1", "K2": lambda x: x["unit_type"] == "K2",
             "truth_unknown": lambda x: x["truth"] == "unknown", "default_violating": lambda x: x["default_violating"],
             "k1": lambda x: x["k"] == 1, "any": lambda x: True}
    for name, target in PASSES:
        for _, iid, k, u in pool:
            if len(chosen) >= N_TOTAL or sum(preds[name](c) for c in chosen) >= target:
                break
            cand = item(iid, k, u)
            if not preds[name](cand) or any(c["group_id"] == cand["group_id"] for c in chosen) \
                    or sum(c["family"] == cand["family"] for c in chosen) >= PER_FAMILY:
                continue
            cand["source"] = f"pass:{name}"
            chosen.append(cand)

    public_rows, priv_rows = [], []
    for n, c in enumerate(chosen, 1):
        inst, w, h = build(c["instance_id"], c["k"])
        u = parse_unit(c["unit"])
        cfg = inst.scenario.config
        cid = f"uc{n:02d}"
        req = {}
        for pkg in PACKAGES:
            msgs, domain, ids = unit_messages(load_prompts(pkg), cfg, inst.scenario.brief, h, u, pkg, RENDER_REVISION)
            req[pkg] = {"messages": msgs, "schema": PACKAGES[pkg].schema(domain, u.variable), "domain": domain}
        public_rows.append({"context_id": cid, "instance_id": c["instance_id"], "family": c["family"], "k": c["k"],
                            "unit": c["unit"], "unit_type": c["unit_type"], "source": c["source"], "render_revision": RENDER_REVISION,
                            "agent_view": h.to_agent_dict(), "visible_ids": sorted(ledger(h)[1]), "requests": req})
        priv_rows.append({"context_id": cid, "truth": c["truth"], "default_violating": c["default_violating"],
                          "posterior": evidence_posterior(inst.scenario, h, u),
                          "robot_known": sorted(robot_known_values(h, cfg.recipient)),
                          "original_pilot_v1_r2": stored.get((c["instance_id"], c["unit"])) if c["k"] == 0 else None})
    pub_path = ROOT / "reports" / "pilot" / "unit-contexts-v1.jsonl"
    priv_path = ROOT / "data" / "pilot" / "unit-contexts-v1-privileged.jsonl"
    pub_text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in public_rows)
    priv_text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in priv_rows)
    pub_path.write_text(pub_text)
    priv_path.write_text(priv_text)
    hashes = {"public": sha(pub_text), "privileged": sha(priv_text)}
    L = ["# Fixed unit-inference contexts `unit-contexts-v1`", "",
         f"Selection rule: `scripts/freeze_unit_contexts.py` docstring. Renderer r{RENDER_REVISION}; packages {list(PACKAGES)}. "
         "Frozen before any pilot-v2 or API output.", "",
         f"- Contexts: {len(chosen)}; by family {dict(Counter(c['family'] for c in chosen))}",
         f"- By unit type {dict(Counter(c['unit_type'] for c in chosen))}; history prefix k: {dict(Counter(c['k'] for c in chosen))}",
         f"- Truth 'unknown': {sum(c['truth'] == 'unknown' for c in chosen)}; default-violating content: {sum(c['default_violating'] for c in chosen)}",
         f"- With a stored original pilot-v1 (r2) output: {sum(r['original_pilot_v1_r2'] is not None for r in priv_rows)}",
         f"- sha256 public `{hashes['public']}`, privileged `{hashes['privileged']}`", "",
         "| id | instance | k | unit | source |", "|---|---|---|---|---|"]
    L += [f"| {p['context_id']} | {p['instance_id']} | {p['k']} | {p['unit']} | {p['source']} |" for p in public_rows]
    (ROOT / "reports" / "pilot" / "unit-contexts-v1.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:8]))


if __name__ == "__main__":
    main()
