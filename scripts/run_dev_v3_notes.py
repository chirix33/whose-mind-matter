"""dev-v3 Round B: fresh-context value-of-notes sanity check (experiment-plan.md Entry 2 + Entry 1a R8-R12).

    python3 scripts/run_dev_v3_notes.py verify                  # frozen dev-v3 hashes == current code (no calls)
    python3 scripts/run_dev_v3_notes.py notes                   # freeze note payloads (local model, temperature 0)
    python3 scripts/run_dev_v3_notes.py render                  # rendered MIND NOTES per state/condition (no calls)
    python3 scripts/run_dev_v3_notes.py policy --replicates 3   # local policy, temperature 1.0, unseeded
    (--config configs/models/api_gpt_6_1_sol.json --tag api for the optional B2 batch, after its own notes stage)

States: the 4 variants of each hash-selected group (dev-v3-freeze.json round_b_selection): 16 t0 states.
Conditions (fixed allocation = the construction's focal units at t0; no further allocation; no refresh; notes retained
and shown at every step with their t0 timestamp):
  none        no explicit notes (direct rendering)
  inferred    pilot-v2.1 note from the same backbone, r6 rules + public model, legal visible history only
  reference   exact public-model posterior of the unit's content given the t0 history (plain posterior b_h), plus
              one `unresolved` line giving P(the belief / view is correct now) for K units (R8)
  privileged  the true content (p = 1) and its true correctness, same format. PRIVILEGED diagnostic only.
Payloads are frozen (sha256) before any policy outcome. Every attempt is logged; truncated outputs count as failed
attempts; after 3 failed attempts the policy falls back to wait() (flagged) and a note is null (no note shown).
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

from officeminds import devgen3 as G  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from vomi import runlog  # noqa: E402
from vomi.clients import BudgetExceeded, make_client  # noqa: E402
from vomi.graph import PerspectiveGraph  # noqa: E402
from vomi.oracle import ExactOracle  # noqa: E402
from vomi.pilot import (PACKAGES, call_with_protocol, describe_unit, load_prompts, policy_messages,  # noqa: E402
                        prompt_hashes, run_episode_arm, task_card, unit_messages)
from vomi.units import KNOWLEDGE, Unit, content, default_holds  # noqa: E402

PACKAGE, REV = "pilot-v2.1", 6
MARKERS = ("Watching a quiet conversation tells a bystander nothing", "PUBLIC MODEL OF THIS TASK")
CONDITIONS = ("none", "inferred", "reference", "privileged")
FREEZE = ROOT / "reports" / "dev-v3-block" / "dev-v3-freeze.json"
DATA = ROOT / "data" / "dev-v3-block"  # PRIVILEGED payloads (gitignored)
RUNS = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "dev-v3-notes"


def sha(obj) -> str:
    return hashlib.sha256((obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True)).encode()).hexdigest()


class LengthGuard:
    """R11: an output cut off at max_tokens is a failed attempt even if its prefix happens to parse."""

    def __init__(self, inner):
        self.inner, self.model = inner, getattr(inner, "model", "?")
        self.ledger = getattr(inner, "ledger", None)

    def chat(self, messages, **params):
        r = self.inner.chat(messages, **params)
        if (r.finish_reason == "length" or str(r.finish_reason or "").startswith("incomplete")) and not r.error:
            r.error = "truncated: finish_reason=length"
        return r


def states():
    fz = json.loads(FREEZE.read_text())
    sel = set(fz["round_b_selection"].values())
    out = []
    for inst in G.generate():
        if inst.construction in sel:
            out.append({"state_id": inst.instance_id, "inst": inst, "units": G.focal_units(inst)})
    assert len(out) == 16, len(out)
    return out


def t0(inst):
    w = inst.scenario.build(inst.hidden)
    return w, VisibleHistory(inst.scenario.brief, [(None, w.reset())])


def verify(_args=None):
    """The frozen manifest must match what the current code renders (refuse to run otherwise)."""
    fz = json.loads(FREEZE.read_text())
    bad = [f for f, h in fz["source_sha256"].items() if hashlib.sha256((ROOT / f).read_bytes()).hexdigest() != h]
    prompts = load_prompts(PACKAGE)
    for inst in G.generate():
        row = fz["instances"][inst.instance_id]
        w, h = t0(inst)
        cfg = inst.scenario.config
        if sha(json.dumps(h.to_agent_dict(), sort_keys=True)) != row["agent_view_t0_sha256"]:
            bad.append(inst.instance_id + ":agent_view")
        if sha(task_card(cfg, inst.scenario.brief, rev=6)) != row["card_sha256"]:
            bad.append(inst.instance_id + ":card")
        pol = policy_messages(prompts, cfg, inst.scenario.brief, h, None, REV)[0][1]["content"]
        if sha(pol) != row["policy_prompt_t0_direct_sha256"]:
            bad.append(inst.instance_id + ":policy_prompt")
        if [str(u) for u in G.focal_units(inst)] != row["focal_units"]:
            bad.append(inst.instance_id + ":focal")
    if prompt_hashes(PACKAGE) != fz["prompt_sha256"]:
        bad.append("prompts")
    if bad:
        raise SystemExit(f"FREEZE MISMATCH: {bad}")
    print("freeze verified:", FREEZE.name, "instances", len(fz["instances"]))
    return fz


def computed_note(u: Unit, cfg, dist: dict[str, float], p_correct: float | None, kind: str) -> dict:
    hyps = [{"value": v, "p": round(p, 4)} for v, p in sorted(dist.items()) if p > 0]
    big = max(hyps, key=lambda h: h["p"])
    big["p"] = round(big["p"] + 1.0 - sum(h["p"] for h in hyps), 4)
    unresolved = []
    if u.variable == KNOWLEDGE and p_correct is not None:
        what = "this belief" if u.depth == 1 else f"this view of {u.path[1]}'s belief"
        unresolved = [f"Under the public model, the probability that {what} is correct now is {p_correct:.2f}"]
    return {"path": list(u.path), "variable": u.variable, "about": describe_unit(u, cfg)[1], "as_of_step": 0,
            "status": "grounded" if max(dist.values()) >= 0.8 else "uncertain", "hypotheses": hyps,
            "unresolved": unresolved, "evidence_ids": [], "rule_ids": [], "source": kind}


def reference_and_privileged(inst, u):
    w, h = t0(inst)
    o = ExactOracle(inst.scenario, h)  # plain posterior b_h under the declared public model (R7)
    dist, corr = {}, 0.0
    for p, x in o.belief:
        v = content(x, u)[0]
        dist[v] = dist.get(v, 0.0) + p
        corr += p * default_holds(x, u)
    cfg = inst.scenario.config
    ref = computed_note(u, cfg, dist, corr, "reference")
    priv = computed_note(u, cfg, {content(w, u)[0]: 1.0}, 1.0 if default_holds(w, u) else 0.0, "privileged")
    return ref, priv, dist


def notes_path(tag):
    return DATA / f"roundB-notes-{tag}.json"


def stage_notes(args):
    verify()
    path = notes_path(args.tag)
    if path.exists():
        raise SystemExit(f"{path} exists: payloads are frozen; refusing to regenerate")
    cfg_m = json.loads(Path(args.config).read_text())
    decoding = dict(cfg_m["decoding"])
    if args.tag == "api":
        decoding = {**decoding, "reasoning_effort": "low", "max_tokens": 6000}
    client = LengthGuard(make_client(cfg_m))
    pkg, prompts = PACKAGES[PACKAGE], load_prompts(PACKAGE)
    out = {"package": PACKAGE, "render_revision": REV, "model": cfg_m["model"], "decoding": decoding, "tag": args.tag,
           "prompt_sha256": prompt_hashes(PACKAGE)["unit_system"], "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "freeze_sha256": hashlib.sha256(FREEZE.read_bytes()).hexdigest(), "states": {}}
    for st in states():
        inst = st["inst"]
        cfg = inst.scenario.config
        w, h = t0(inst)
        row = {"notes": {c: {} for c in CONDITIONS[1:]}, "calls": {}}
        for u in st["units"]:
            msgs, domain, ids = unit_messages(prompts, cfg, inst.scenario.brief, h, u, PACKAGE, REV)
            assert all(m in msgs[1]["content"] for m in MARKERS)
            rec = call_with_protocol(client, "unit", 0, str(u), msgs, pkg.schema(domain, u.variable),
                                     lambda t, u=u, domain=domain, ids=ids: pkg.validate(t, u.path, u.variable, domain, ids),
                                     decoding)
            ref, priv, _ = reference_and_privileged(inst, u)
            row["notes"]["inferred"][str(u)] = dict(rec.parsed, source="inferred") if rec.ok else None
            row["notes"]["reference"][str(u)] = ref
            row["notes"]["privileged"][str(u)] = priv
            row["calls"][str(u)] = asdict(rec)
            print(st["state_id"], u, "inferred ok" if rec.ok else "inferred FAILED", flush=True)
        row["note_sha256"] = {c: sha(v) for c, v in row["notes"].items()}
        out["states"][st["state_id"]] = row
    out["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    sts = {st["state_id"]: st for st in states()}
    for sid, v in out["states"].items():
        v["rendered_notes_sha256"] = {c: sha(rendered(sts[sid], c, out)[1]) for c in CONDITIONS}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1, sort_keys=True))
    proof = {k: out[k] for k in ("package", "render_revision", "model", "decoding", "tag", "prompt_sha256", "started_at",
                                 "ended_at", "freeze_sha256")}
    proof["notes_file_sha256"] = sha(out["states"])
    proof["states"] = {s: {"note_sha256": v["note_sha256"], "rendered_notes_sha256": v["rendered_notes_sha256"],
                           "inferred_ok": {u: n is not None for u, n in v["notes"]["inferred"].items()}}
                       for s, v in out["states"].items()}
    pp = ROOT / "reports" / "dev-v3-block" / f"roundB-notes-freeze-{args.tag}.json"
    pp.write_text(json.dumps(proof, indent=1, sort_keys=True) + "\n")
    print(path, proof["notes_file_sha256"], pp)


def condition_kwargs(st, cond, frozen):
    if cond == "none":
        return {"arm": "direct"}
    notes = frozen["states"][st["state_id"]]["notes"][cond]
    units = [u for u in st["units"] if notes.get(str(u)) is not None]  # a failed inferred note is not shown (R11)
    return {"arm": "fixed", "initial_units": units, "allocate": False,
            "frozen_notes": {str(u): notes[str(u)] for u in units}}


def rendered(st, cond, frozen) -> tuple[str, str]:
    inst = st["inst"]
    kw = condition_kwargs(st, cond, frozen)
    _, h = t0(inst)
    g = None
    if kw["arm"] != "direct":
        g = PerspectiveGraph(recipient=inst.scenario.config.recipient, refutation_mode="fact_only")
        for u in kw["initial_units"]:
            note = kw["frozen_notes"][str(u)]
            g.instantiate(u, note, note.get("evidence_ids", []), t=0, cost=0.0)
    user = policy_messages(load_prompts(PACKAGE), inst.scenario.config, inst.scenario.brief, h, g, REV)[0][1]["content"]
    return user, "MIND NOTES" + user.split("MIND NOTES", 1)[1].split("LEGAL ACTIONS NOW", 1)[0].rstrip()


def stage_render(args):
    frozen = json.loads(notes_path(args.tag).read_text())
    out = DATA / f"roundB-policy-prompts-{args.tag}.md"  # PRIVILEGED note content: kept out of reports/
    L = [f"# Round B ({args.tag}): t0 MIND NOTES per state and condition (rendered locally, no model calls)", ""]
    for st in states():
        sec = {}
        for cond in CONDITIONS:
            user, notes_part = rendered(st, cond, frozen)
            assert all(m in user for m in MARKERS)
            sec[cond] = notes_part
            L += [f"## {st['state_id']} — {cond}", "", "```", notes_part, "```", ""]
        same = [(a, b) for i, a in enumerate(CONDITIONS) for b in CONDITIONS[i + 1:] if sec[a] == sec[b]]
        L += [f"identical conditions: {same or 'none'}", ""]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(out)


def stage_policy(args):
    fz = verify()
    frozen = json.loads(notes_path(args.tag).read_text())
    cfg_m = json.loads(Path(args.config).read_text())
    decoding = {**cfg_m["decoding"], "temperature": 1.0} if args.tag == "local" else {
        **cfg_m["decoding"], "reasoning_effort": "low", "max_tokens": 2000}
    sts = states()
    for st in sts:
        for c in CONDITIONS:
            user, part = rendered(st, c, frozen)
            assert all(m in user for m in MARKERS)
            if c != "none":
                assert sha(part) == frozen["states"][st["state_id"]]["rendered_notes_sha256"][c]
    jobs = []  # counterbalanced: conditions rotated by (state index + replicate); full passes in order (resource rule)
    for r in range(args.replicates):
        for i, st in enumerate(sts):
            for j in range(len(CONDITIONS)):
                jobs.append((st, CONDITIONS[(i + r + j) % len(CONDITIONS)], r))
    meta = {"stage": "policy", "tag": args.tag, "model": cfg_m["model"], "decoding": decoding, "package": PACKAGE,
            "render_revision": REV, "replicates": args.replicates, "concurrency": args.concurrency,
            "freeze_sha256": hashlib.sha256(FREEZE.read_bytes()).hexdigest(), "round_b_selection": fz["round_b_selection"],
            "notes_file_sha256": sha(frozen["states"]), "prompt_sha256": prompt_hashes(PACKAGE),
            "stage_cap_usd_env": os.environ.get("OFFICEMINDS_API_CAP_USD"),
            "dispatch_order": [(s["state_id"], c, r) for s, c, r in jobs]}
    manifest = runlog.new_manifest("dev-v3-notes", meta)
    out = RUNS / manifest["run_id"]
    out.mkdir(parents=True, exist_ok=True)
    client = LengthGuard(make_client(cfg_m))

    def job(item):
        n, (st, cond, r) = item
        base = {"state_id": st["state_id"], "condition": cond, "replicate": r, "dispatch_index": n}
        try:
            res = run_episode_arm(client, st["inst"], decoding=decoding, package=PACKAGE, rev=REV,
                                  **condition_kwargs(st, cond, frozen))
        except BudgetExceeded as e:
            return {**base, "blocked": str(e)}
        except Exception as e:  # recorded, never silently retried
            return {**base, "blocked": f"error: {type(e).__name__}: {e}"}
        return {**base, "units": [str(u) for u in st["units"]],
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
    ap.add_argument("stage", choices=("verify", "notes", "render", "policy"))
    ap.add_argument("--config", default=str(ROOT / "configs" / "models" / "local_gpt_oss_20b.json"))
    ap.add_argument("--tag", default="local", choices=("local", "api"))
    ap.add_argument("--replicates", type=int, default=3)
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()
    {"verify": verify, "notes": stage_notes, "render": stage_render, "policy": stage_policy}[args.stage](args)


if __name__ == "__main__":
    main()
