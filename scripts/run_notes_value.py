"""Autonomous block Round 2: replicated value-of-notes diagnostic on the nine prespecified intervention states.

    python3 scripts/run_notes_value.py notes  --config configs/models/api_gpt_6_1_sol.json   # freeze note payloads
    python3 scripts/run_notes_value.py render                                               # policy prompts, no calls
    python3 scripts/run_notes_value.py policy --config configs/models/api_gpt_6_1_sol.json --replicates 3
    python3 scripts/run_notes_value.py doubt                                                # Round 3 control payloads
    python3 scripts/run_notes_value.py policy --round 3 --replicates 4

States: data/pilot/dev-v2/interventions.json (instance, t0, unit; original labels kept). Conditions, same API policy,
fixed allocation (the state's one unit at t0, no further allocation, no refresh):
  none        no explicit notes (direct rendering)
  inferred    pilot-v2.1 note from the API model, r5 rules, legal visible history only
  inferred_bare  the SAME frozen inferred payload with support / evidence IDs / rule IDs / unresolved removed, so it
              renders exactly like the computed notes (matched-presentation control; Round 2 Opus gate item 3)
  reference   the exact evidence posterior of the unit's content under the declared public model (the dev-v2
              generator) given the same visible history. No hidden-world identity, correctness flag or action. It uses
              generator base rates/templates the LLM prompt does not state (reports/autonomous-block/reference-audit.json)
  privileged  the unit's actual content in the realized world (p = 1). PRIVILEGED diagnostic; not deployable and
              not a guaranteed upper bound
Payloads are frozen (stage `notes`, sha256 per payload) before any policy outcome and reused for every replicate.
Representation: all notes use the pilot-v2.1 note format and status vocabulary. Inferred notes carry the model's
per-hypothesis support, cited evidence IDs with quoted excerpts, unresolved items and a model-chosen status; computed
notes print "cited evidence: none" and take their status from a 0.8 threshold. inferred vs inferred_bare measures that
presentation difference; inferred_bare / reference / privileged contrast content at matched presentation (status
still differs: model-chosen vs threshold).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds.devgen import generate  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from vomi import runlog  # noqa: E402
from vomi.clients import BudgetExceeded, make_client  # noqa: E402
from vomi.fidelity import evidence_posterior  # noqa: E402
from vomi.graph import PerspectiveGraph  # noqa: E402
from vomi.pilot import (PACKAGES, call_with_protocol, describe_unit, load_prompts, policy_messages,  # noqa: E402
                        prompt_hashes, run_episode_arm, unit_messages)
from vomi.units import Unit, content  # noqa: E402

PACKAGE, REV = "pilot-v2.1", 5
R5_MARKER = "Before the task (none of this appears"  # checked in every rendered request (Round 2 Opus gate item 1)
CONDITIONS = ("none", "inferred", "inferred_bare", "reference", "privileged")
NOTES = ROOT / "data" / "autonomous-block" / "round2-notes.json"  # PRIVILEGED (reference/privileged payloads)
RUNS = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "notes-value"


def parse_unit(s: str) -> Unit:
    return Unit(tuple(s[2:-1].split("->")), "knowledge" if s.startswith("K(") else "reliability")


def states():
    insts = {i.instance_id: i for i in generate(version="dev-v2")}
    ivs = json.loads((ROOT / "data" / "pilot" / "dev-v2" / "interventions.json").read_text())
    out = []
    for n, iv in enumerate(ivs, 1):
        assert iv["decision_state"] == "t0"
        out.append({"state_id": f"s{n}", **iv, "inst": insts[iv["instance_id"]], "u": parse_unit(iv["unit"])})
    return out


def t0(inst):
    w = inst.scenario.build(inst.hidden)
    return w, VisibleHistory(inst.scenario.brief, [(None, w.reset())])


def computed_note(u: Unit, cfg, dist: dict[str, float], kind: str) -> dict:
    hyps = [{"value": v, "p": round(p, 4)} for v, p in sorted(dist.items()) if p > 0]
    s = sum(h["p"] for h in hyps)
    big = max(hyps, key=lambda h: h["p"])
    big["p"] = round(big["p"] + 1.0 - s, 4)  # rounding residue on the largest mass keeps the sum at 1
    assert all(h["p"] >= 0 for h in hyps) and abs(sum(h["p"] for h in hyps) - 1.0) < 1e-6
    return {"path": list(u.path), "variable": u.variable, "about": describe_unit(u, cfg)[1], "as_of_step": 0,
            "status": "grounded" if max(dist.values()) >= 0.8 else "uncertain", "hypotheses": hyps,
            "unresolved": [], "evidence_ids": [], "rule_ids": [], "source": kind}


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def bare(note: dict) -> dict:
    """The same content with the argument fields removed: renders like a computed note."""
    return {**{k: v for k, v in note.items() if k not in ("support", "evidence_ids", "rule_ids", "unresolved")},
            "hypotheses": [{"value": h["value"], "p": h["p"]} for h in note["hypotheses"]],
            "unresolved": [], "evidence_ids": [], "rule_ids": [], "source": "inferred_bare"}


def git_state() -> dict:
    head = os.popen(f'git -C "{ROOT}" rev-parse HEAD').read().strip()
    dirty = [x for x in os.popen(f'git -C "{ROOT}" status --porcelain').read().split("\n") if x.strip()]
    return {"git_commit": head, "dirty_paths": dirty}


def rendered_notes(st, cond, frozen) -> tuple[str, str]:
    """(full t0 policy user message, its MIND NOTES section) for one state/condition, built without any client."""
    inst = st["inst"]
    kw = condition_kwargs(st, cond, frozen)
    _, h = t0(inst)
    g = None
    if kw["arm"] != "direct":
        g = PerspectiveGraph(recipient=inst.scenario.config.recipient, refutation_mode="fact_only")
        for u in kw.get("initial_units", []):
            note = kw["frozen_notes"][str(u)]
            g.instantiate(u, note, note.get("evidence_ids", []), t=0, cost=0.0)
    msgs, _ = policy_messages(load_prompts(PACKAGE), inst.scenario.config, inst.scenario.brief, h, g, REV)
    user = msgs[1]["content"]
    return user, "MIND NOTES" + user.split("MIND NOTES", 1)[1].split("LEGAL ACTIONS NOW", 1)[0].rstrip()


def stage_notes(args):
    if NOTES.exists():
        raise SystemExit(f"{NOTES} exists: payloads are frozen; refusing to regenerate")
    cfg_m = json.loads(Path(args.config).read_text())
    decoding = {**cfg_m["decoding"], "reasoning_effort": "low", "max_tokens": args.max_tokens}
    client = make_client(cfg_m)
    pkg = PACKAGES[PACKAGE]
    spent0 = client.ledger.state["spent_usd"]
    out = {"package": PACKAGE, "render_revision": REV, "model": cfg_m["model"], "decoding": decoding,
           "prompt_sha256": prompt_hashes(PACKAGE)["unit_system"], "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           **git_state(), "states": {}}
    for st in states():
        inst, u = st["inst"], st["u"]
        cfg = inst.scenario.config
        w, h = t0(inst)
        msgs, domain, ids = unit_messages(load_prompts(PACKAGE), cfg, inst.scenario.brief, h, u, PACKAGE, REV)
        assert R5_MARKER in msgs[1]["content"]
        rec = call_with_protocol(client, "unit", 0, str(u), msgs, pkg.schema(domain, u.variable),
                                 lambda t: pkg.validate(t, u.path, u.variable, domain, ids), decoding)
        inferred = dict(rec.parsed, source="inferred") if rec.ok else None
        notes = {"inferred": inferred, "inferred_bare": bare(inferred) if inferred else None,
                 "reference": computed_note(u, cfg, evidence_posterior(inst.scenario, h, u), "reference"),
                 "privileged": computed_note(u, cfg, {content(w, u)[0]: 1.0}, "privileged")}
        out["states"][st["state_id"]] = {
            "instance_id": st["instance_id"], "unit": st["unit"], "symbolic_category": st["symbolic_category"],
            "category_record": st["category_record"], "notes": notes,
            "note_sha256": {k: (sha(v) if v else None) for k, v in notes.items()},
            "inferred_call": asdict(rec), "inferred_usage": rec.usage()}
        print(st["state_id"], st["unit"], "inferred ok" if rec.ok else "inferred FAILED", {k: (v or {}).get("status") for k, v in notes.items()})
    out["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    out["inferred_notes_usd_ledger_delta"] = client.ledger.state["spent_usd"] - spent0
    sts = {st["state_id"]: st for st in states()}
    for sid, v in out["states"].items():  # also hash what the policy will actually see
        v["rendered_notes_sha256"] = {c: hashlib.sha256(rendered_notes(sts[sid], c, out)[1].encode()).hexdigest()
                                      for c in CONDITIONS}
    NOTES.parent.mkdir(parents=True, exist_ok=True)
    NOTES.write_text(json.dumps(out, indent=1, sort_keys=True))
    # tracked, pre-outcome proof of the freeze (the payload file itself is gitignored and privileged)
    keep = ("package", "render_revision", "model", "decoding", "prompt_sha256", "started_at", "ended_at", "git_commit",
            "dirty_paths", "inferred_notes_usd_ledger_delta")
    proof = {k: out[k] for k in keep}
    proof["notes_file_sha256"] = sha(out["states"])
    proof["states"] = {s: {"unit": v["unit"], "note_sha256": v["note_sha256"], "rendered_notes_sha256": v["rendered_notes_sha256"],
                           "inferred_status": (v["notes"]["inferred"] or {}).get("status")} for s, v in out["states"].items()}
    proof_path = ROOT / "reports" / "autonomous-block" / "round2-notes-freeze.json"
    proof_path.write_text(json.dumps(proof, indent=1, sort_keys=True) + "\n")
    print(NOTES, proof["notes_file_sha256"], proof_path)


NOTES3 = ROOT / "data" / "autonomous-block" / "round3-notes.json"  # PRIVILEGED-derived diagnostic payloads
DOUBT = 0.2


def doubt_note(ref: dict) -> dict:
    """Round 3 matched control: the frozen reference distribution scaled by 1 - DOUBT plus DOUBT on "unknown".
    Status is copied from the reference note so that only the distribution changes (no new banner)."""
    hyps = [{"value": h["value"], "p": round(h["p"] * (1 - DOUBT), 4)} for h in ref["hypotheses"] if h["value"] != "unknown"]
    prior_unknown = sum(h["p"] for h in ref["hypotheses"] if h["value"] == "unknown")
    hyps.append({"value": "unknown", "p": round(DOUBT + prior_unknown * (1 - DOUBT), 4)})
    big = max(hyps, key=lambda h: h["p"])
    big["p"] = round(big["p"] + 1.0 - sum(h["p"] for h in hyps), 4)
    assert all(h["p"] >= 0 for h in hyps) and abs(sum(h["p"] for h in hyps) - 1.0) < 1e-6
    return {**ref, "hypotheses": sorted(hyps, key=lambda h: h["value"]), "source": "reference_doubt"}


def merged_frozen() -> dict:
    """Round 2 payloads plus the Round 3 reference_doubt payloads (when frozen)."""
    frozen = json.loads(NOTES.read_text())
    if NOTES3.exists():
        r3 = json.loads(NOTES3.read_text())
        for sid, v in r3["states"].items():
            frozen["states"][sid]["notes"]["reference_doubt"] = v["note"]
            frozen["states"][sid]["note_sha256"]["reference_doubt"] = v["note_sha256"]
    return frozen


def stage_doubt(args):
    if NOTES3.exists():
        raise SystemExit(f"{NOTES3} exists: payloads are frozen; refusing to regenerate")
    frozen = json.loads(NOTES.read_text())
    out = {"derived_from_notes_file_sha256": sha(frozen["states"]), "doubt_mass": DOUBT, "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           **git_state(), "states": {}}
    for sid, v in frozen["states"].items():
        note = doubt_note(v["notes"]["reference"])
        out["states"][sid] = {"unit": v["unit"], "note": note, "note_sha256": sha(note)}
    NOTES3.write_text(json.dumps(out, indent=1, sort_keys=True))
    merged = merged_frozen()
    proof = {k: out[k] for k in ("derived_from_notes_file_sha256", "doubt_mass", "created_at", "git_commit", "dirty_paths")}
    proof["states"] = {}
    for st in states():
        sid = st["state_id"]
        proof["states"][sid] = {"unit": st["unit"], "note_sha256": out["states"][sid]["note_sha256"],
                                "rendered_notes_sha256": hashlib.sha256(rendered_notes(st, "reference_doubt", merged)[1].encode()).hexdigest(),
                                "distribution": {h["value"]: h["p"] for h in out["states"][sid]["note"]["hypotheses"]},
                                "status": out["states"][sid]["note"]["status"]}
    path = ROOT / "reports" / "autonomous-block" / "round3-notes-freeze.json"
    path.write_text(json.dumps(proof, indent=1, sort_keys=True) + "\n")
    print(NOTES3, path)


def condition_kwargs(st, cond, frozen):
    if cond == "none":
        return {"arm": "direct"}
    note = frozen["states"][st["state_id"]]["notes"][cond]
    if note is None:  # inferred note failed after the protocol: the policy sees no note (recorded)
        return {"arm": "fixed", "initial_units": [], "allocate": False}
    return {"arm": "fixed", "initial_units": [st["u"]], "allocate": False, "frozen_notes": {st["unit"]: note}}


def stage_render(args):
    frozen = json.loads(NOTES.read_text())
    out = ROOT / "data" / "autonomous-block" / "round2-policy-prompts.md"  # PRIVILEGED note content: kept out of reports/
    L = ["# Round 2: the t0 policy MIND NOTES per state and condition (rendered locally, no model calls)", ""]
    for st in states():
        for cond in CONDITIONS:
            user, notes_part = rendered_notes(st, cond, frozen)
            assert R5_MARKER in user
            L += [f"## {st['state_id']} {st['instance_id']} {st['unit']} — {cond}", "", "```", notes_part, "```", ""]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(out)


def stage_policy(args):
    frozen = merged_frozen()
    cfg_m = json.loads(Path(args.config).read_text())
    decoding = {**cfg_m["decoding"], "reasoning_effort": "low", "max_tokens": args.max_tokens}
    sts = states()
    conds = CONDITIONS if args.round == 2 else ("none", "reference", "reference_doubt")
    extra = [] if args.round == 2 else [("s9", "inferred_bare")]  # Round 3: replicate the s9 inferred_bare cell only
    for st in sts:  # the policy must render the same rules revision the notes cite
        assert all(R5_MARKER in rendered_notes(st, c, frozen)[0] for c in conds)
    jobs = []  # counterbalanced dispatch order: conditions rotated by (state index + replicate)
    for r in range(args.replicates):
        for i, st in enumerate(sts):
            for j in range(len(conds)):
                jobs.append((st, conds[(i + r + j) % len(conds)], r))
            jobs += [(st, c, r) for sid, c in extra if sid == st["state_id"]]
    meta = {"stage": "policy", "round": args.round, "conditions": list(conds), "extra_cells": extra, "model": cfg_m["model"], "decoding": decoding, "package": PACKAGE, "render_revision": REV,
            "replicates": args.replicates, "concurrency": args.concurrency, "notes_file_sha256": sha(frozen["states"]),
            "stage_cap_usd_env": os.environ.get("OFFICEMINDS_API_CAP_USD"),
            "note_sha256": {s: v["note_sha256"] for s, v in frozen["states"].items()},
            "prompt_sha256": prompt_hashes(PACKAGE), "dispatch_order": [(s["state_id"], c, r) for s, c, r in jobs]}
    manifest = runlog.new_manifest("notes-value", meta)
    manifest["dirty_paths"] = [l for l in os.popen(f'git -C "{ROOT}" status --porcelain').read().split("\n") if l.strip()]
    out = RUNS / manifest["run_id"]
    out.mkdir(parents=True, exist_ok=True)
    client = make_client(cfg_m)

    def job(item):
        n, (st, cond, r) = item
        try:
            res = run_episode_arm(client, st["inst"], decoding=decoding, package=PACKAGE, rev=REV,
                                  **condition_kwargs(st, cond, frozen))
        except BudgetExceeded as e:
            return {"state_id": st["state_id"], "condition": cond, "replicate": r, "dispatch_index": n, "blocked": str(e)}
        except Exception as e:  # one failure must not kill the pool before the manifest is written; the ledger is authoritative
            return {"state_id": st["state_id"], "condition": cond, "replicate": r, "dispatch_index": n,
                    "blocked": f"error: {type(e).__name__}: {e}"}
        return {"state_id": st["state_id"], "condition": cond, "replicate": r, "dispatch_index": n, "unit": st["unit"],
                "note_sha256": frozen["states"][st["state_id"]]["note_sha256"].get(cond), **asdict(res)}

    t_start = time.monotonic()
    results = []
    with (out / "episodes.jsonl").open("w") as f, ThreadPoolExecutor(args.concurrency) as pool:
        for res in pool.map(job, enumerate(jobs)):
            results.append(res)
            f.write(json.dumps(res, default=str) + "\n")
            f.flush()
    runlog.finish(manifest, out, wall_clock_s=time.monotonic() - t_start,
                  episodes=sum("blocked" not in r for r in results), blocked=sum("blocked" in r for r in results))
    print(f"episodes {sum('blocked' not in r for r in results)}; blocked {sum('blocked' in r for r in results)}; out: {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("notes", "render", "policy", "doubt"))
    ap.add_argument("--round", type=int, choices=(2, 3), default=2)
    ap.add_argument("--config", default=str(ROOT / "configs" / "models" / "api_gpt_6_1_sol.json"))
    ap.add_argument("--max-tokens", type=int, default=6000)
    ap.add_argument("--replicates", type=int, default=3)
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()
    {"notes": stage_notes, "render": stage_render, "policy": stage_policy, "doubt": stage_doubt}[args.stage](args)


if __name__ == "__main__":
    main()
