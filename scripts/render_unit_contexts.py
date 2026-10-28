"""Re-render the 24 frozen fixed unit contexts (unit-contexts-v1) under a later renderer revision.

    python3 scripts/render_unit_contexts.py --rev 4

The CONTEXTS do not change: the same instances, history prefixes and units. Each history is rebuilt by replaying
the instance with the recorded robot action(s) and must equal the frozen agent view byte for byte, or the script
stops. Only the rendered requests change (public rules r4; packages pilot-v1, pilot-v2, pilot-v2.1).
Writes reports/autonomous-block/unit-contexts-v1-r<rev>.{jsonl,md}; the .md records the sha256 that
run_unit_contexts.py checks before sending anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds.devgen import generate  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.world import legal_actions  # noqa: E402
from vomi.pilot import PACKAGES, ledger, load_prompts, unit_messages  # noqa: E402
from vomi.units import Unit  # noqa: E402

FROZEN = ROOT / "reports" / "pilot" / "unit-contexts-v1.jsonl"


def parse_unit(s: str) -> Unit:
    return Unit(tuple(s[2:-1].split("->")), "knowledge" if s.startswith("K(") else "reliability")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", type=int, required=True)
    args = ap.parse_args()
    insts = {i.instance_id: i for i in generate(version="dev-v2")}
    frozen_text = FROZEN.read_text()
    rows = []
    for ctx in map(json.loads, frozen_text.splitlines()):
        inst = insts[ctx["instance_id"]]
        w = inst.scenario.build(inst.hidden)
        h = VisibleHistory(inst.scenario.brief, [(None, w.reset())])
        for st in ctx["agent_view"]["steps"][1:]:
            a = next(x for x in legal_actions(inst.scenario.config, h.last) if str(x) == st["action"])
            h.steps.append((a, w.step(a)))
        if json.dumps(h.to_agent_dict(), sort_keys=True) != json.dumps(ctx["agent_view"], sort_keys=True):
            raise SystemExit(f"{ctx['context_id']}: rebuilt history differs from the frozen agent view")
        u = parse_unit(ctx["unit"])
        req = {}
        for pkg, package in PACKAGES.items():
            if args.rev < package.min_render_revision:
                continue
            msgs, domain, ids = unit_messages(load_prompts(pkg), inst.scenario.config, inst.scenario.brief, h, u, pkg, args.rev)
            req[pkg] = {"messages": msgs, "schema": package.schema(domain, u.variable), "domain": domain}
        assert sorted(ledger(h)[1]) == ctx["visible_ids"]
        rows.append({**{k: ctx[k] for k in ("context_id", "instance_id", "family", "k", "unit", "unit_type", "source",
                                            "agent_view", "visible_ids")},
                     "render_revision": args.rev, "requests": req})
    out = ROOT / "reports" / "autonomous-block" / f"unit-contexts-v1-r{args.rev}.jsonl"
    text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    out.write_text(text)
    digest = hashlib.sha256(text.encode()).hexdigest()
    (out.with_suffix(".md")).write_text(
        f"# unit-contexts-v1 re-rendered at r{args.rev}\n\nSame 24 contexts as `reports/pilot/unit-contexts-v1.jsonl` "
        f"(sha256 `{hashlib.sha256(frozen_text.encode()).hexdigest()}`); histories verified identical. "
        f"Packages: {sorted(rows[0]['requests'])}.\n\n- sha256 `{digest}`\n", encoding="utf-8")
    print(out, digest)


if __name__ == "__main__":
    main()
