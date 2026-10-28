"""Pilot input check (requested in the dev-v1 review): compare FULLY RENDERED requests across paired
variants, including configuration supplied outside the history (rewards, stakes, layout, actions).

For every group and every pair of its variants, render the t=0 policy request (direct arm, the one
every arm shares) and the t=0 unit request for each candidate. Classify each pair:
  stakes pair      MUST differ (the reward line carries the stakes-scaled penalty)
  evidence pair    MUST differ (evidence variant adds robot-visible evidence)
  bystander pair   MUST differ
  permuted pair    MAY be identical (names swapped with nothing visible to distinguish them);
                   reported, by design a hidden-role permutation
No LLM is called. There is no response cache in the pilot runner (every call is fresh), so cache
keys cannot drop stakes; if a cache is added later its key must hash the full rendered request.

Run:  python scripts/check_pilot_inputs.py [--version dev-v2]
Writes reports/pilot/input-check-<version>.md and exits non-zero on any MUST violation.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds.devgen import KNOBS, generate  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from vomi.pilot import load_prompts, policy_messages, unit_messages  # noqa: E402
from vomi.units import generate_candidates  # noqa: E402


def h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="dev-v2")
    args = ap.parse_args()
    prompts = load_prompts()
    rendered = {}
    groups = defaultdict(list)
    for inst in generate(version=args.version):
        sc = inst.scenario
        w = sc.build(inst.hidden)
        hist = VisibleHistory(sc.brief, [(None, w.reset())])
        pol, _ = policy_messages(prompts, sc.config, sc.brief, hist, None)
        units = {str(u): h(unit_messages(prompts, sc.config, sc.brief, hist, u)[0])
                 for u in generate_candidates(sc.config, hist)}
        rendered[inst.instance_id] = {"policy": h(pol), "units": units, "view": h(hist.to_agent_dict()), "variant": inst.variant}
        groups[inst.group_id].append(inst)
    rows, violations = [], 0
    for gid, members in sorted(groups.items()):
        fam = members[0].family
        for a, b in itertools.combinations(members, 2):
            diff = [k for k in KNOBS[fam] if getattr(a.variant, k) != getattr(b.variant, k)]
            if len(diff) != 1:
                continue
            knob = diff[0]
            ra, rb = rendered[a.instance_id], rendered[b.instance_id]
            same_view, same_policy = ra["view"] == rb["view"], ra["policy"] == rb["policy"]
            must_differ = knob in ("stakes", "evidence", "bystander")
            bad = must_differ and same_policy
            violations += bad
            rows.append((gid, knob, a.instance_id.split(gid + "-")[1], b.instance_id.split(gid + "-")[1],
                         same_view, same_policy, "VIOLATION" if bad else ("ok" if must_differ else "by design")))
    out = ROOT / "reports" / "pilot" / f"input-check-{args.version}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    L = [f"# Pilot input check: `{args.version}`", "",
         "Fully rendered t=0 policy requests (task card with rewards and stakes, layout, history ledger, physical summary, "
         "legal actions) compared across single-knob variant pairs. No LLM call is made. No response cache is used.", "",
         f"MUST-differ violations: **{violations}**.", "",
         "| group | knob | variant a | variant b | identical history view | identical rendered policy request | verdict |",
         "|---|---|---|---|---|---|---|"]
    L += [f"| {g} | {k} | {a} | {b} | {sv} | {sp} | {v} |" for g, k, a, b, sv, sp, v in rows]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"pairs checked: {len(rows)}; violations: {violations}; identical views: {sum(r[4] for r in rows)}; "
          f"identical rendered requests: {sum(r[5] for r in rows)}; report: {out}")
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
