"""Hybrid block (D-019) Concept 2 fallback pilot: reports/hybrid-block/fallback-protocol.md (frozen before outcomes).

    python3 scripts/run_hybrid_fallback.py render        # CPU: rendered prompts for the tokenizer forecast (no calls)
    python3 scripts/run_hybrid_fallback.py smoke         # <= 48 single-decision probes (check + re-decision), seed 20261499
    python3 scripts/run_hybrid_fallback.py freeze        # fallback-freeze.json (clean tree)
    python3 scripts/run_hybrid_fallback.py verify        # current code/prompts == freeze
    python3 scripts/run_hybrid_fallback.py pilot [--resume DIR]

Conditions (one frozen configuration; the gate is identical for checker_gate and generic_gate):
  direct         existing full-history policy (pilot-v1 policy prompt, render r7, no notes)
  checker_gate   direct + action gate; checker = public-model posterior tracker (CPU, robot-visible history only)
  generic_gate   direct + the same gate; checker = one generic LLM verification call (full history)
  ask_first      direct + the first irreversible commitment of the episode is replaced by one ask() of a present person
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds import devgen3 as G  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.world import Action, legal_actions  # noqa: E402
from vomi import runlog  # noqa: E402
from vomi.clients import make_client  # noqa: E402
from vomi.oracle import ExactOracle  # noqa: E402
from vomi.pilot import (call_with_protocol, ledger, load_prompts, physical_summary, policy_messages,  # noqa: E402
                        policy_schema, task_card, _json_validate)
from vomi.relational import GateVerdict, gate, j_commit  # noqa: E402

BLOCK = ROOT / "reports" / "hybrid-block"
FREEZE = BLOCK / "fallback-freeze.json"
PROTOCOL = BLOCK / "fallback-protocol.md"
RUNS = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "hybrid"
MODEL_CFG = ROOT / "configs" / "models" / "local_gpt_oss_20b.json"
CHECK_PROMPT = ROOT / "prompts" / "hybrid-v1" / "check_system.txt"
PACKAGE, REV = "pilot-v1", 7  # policy prompt package (policy_system is shared by all packages) and render revision
SEEDS = tuple(range(20261400, 20261408))  # fresh, preselected; never used before this block
SMOKE_SEED = 20261499
CONDS = ("direct", "checker_gate", "generic_gate", "ask_first")
DRAWS = 2
CONCURRENCY = 8
MAX_CHECKS_PER_EPISODE = 4  # counted checks (cache hits are free and not counted)
FALLBACK_ACTION = "wait()"
CODE_FILES = ("scripts/run_hybrid_fallback.py", "src/vomi/relational.py", "src/vomi/pilot.py", "src/vomi/clients.py",
              "src/officeminds/devgen3.py", "src/officeminds/world.py", "src/vomi/oracle.py",
              "prompts/pilot-v1/policy_system.txt", "prompts/hybrid-v1/check_system.txt",
              "reports/hybrid-block/fallback-protocol.md")


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def decoding() -> dict:
    d = dict(json.loads(MODEL_CFG.read_text())["decoding"])
    return {**d, "temperature": 1.0, "max_tokens": 1024}


class LengthGuard:
    def __init__(self, inner):
        self.inner, self.model = inner, getattr(inner, "model", "?")

    def chat(self, messages, **params):
        r = self.inner.chat(messages, **params)
        if (r.finish_reason == "length" or str(r.finish_reason or "").startswith("incomplete")) and not r.error:
            r.error = "truncated: finish_reason=length"
        return r


def parse(s: str) -> Action:
    m = re.match(r"(\w+)\((\w*)(?:,(\w+))?\)", s)
    return Action(m[1], m[2] or "", m[3] or "")


def is_commit(a: Action) -> bool:
    return a.kind in ("give", "drop")


def states(seeds=SEEDS):
    out = []
    for seed in seeds:
        for inst in G.generate(seed):
            if inst.variant.permuted:
                continue
            out.append({"state_id": f"s{seed}-{inst.instance_id}", "seed": seed, "inst": inst,
                        "base": f"s{seed}-{inst.construction}"})
    return out


# ----------------------------------------------------------------------------- robot-visible helpers
def excluded_offices(hist: VisibleHistory, cfg) -> tuple:
    """Offices the robot entered after the prologue without seeing the recipient (the public model: nobody moves)."""
    return tuple(sorted({o.room for _, o in hist.steps[1:] if o.room in cfg.offices
                         and cfg.recipient not in o.people_present}))


def evidence_signature(hist: VisibleHistory, cfg) -> str:
    """Cache key for a check's ESTIMATES (p, location): everything heard or seen that can change them. The gate itself
    is recomputed at every use from the current room and remaining steps."""
    heard = [(list(o.utterances), [n[2] for n in o.notices]) for _, o in hist.steps]
    return sha_bytes(json.dumps([heard, excluded_offices(hist, cfg),
                                 cfg.recipient in hist.last.people_present]).encode())


def tracker_check(public_scenario, hist: VisibleHistory, a: Action) -> tuple[float, dict]:
    """Deployed targeted checker: the public-model posterior given the robot-visible history ONLY (the disclosed finite
    hidden-variable model, enumerated). Inputs: the public scenario (prior + public generative rules) and `hist`."""
    cfg = public_scenario.config
    o = ExactOracle(public_scenario, hist)
    loc, p = {}, 0.0
    for w, x in o.belief:
        r = x.people_rooms[cfg.recipient]
        loc[r] = loc.get(r, 0.0) + w
        if a.kind == "give":
            other, fact = cfg.handoff_routes[a.target]
            m = x.minds[a.target]
            dest = m.beliefs.get(fact, "unknown") if not other else m.nested.get((other, fact), "unknown")
            p += w * (dest == r)
        else:
            p += w * (a.target == r)
    return p, loc


def check_messages(prompts, cfg, brief, hist, a: Action):
    led, _ = ledger(hist)
    offices = list(cfg.offices)
    user = "\n\n".join([task_card(cfg, brief, REV), led, physical_summary(hist), f"PROPOSED ACTION: {a}",
                        'Respond as JSON: {"p_success": <probability 0-1>, "recipient_location": {'
                        + ", ".join(f'"{o}": <probability>' for o in offices) + "}}"])
    schema = {"type": "object", "properties": {
        "p_success": {"type": "number", "minimum": 0, "maximum": 1},
        "recipient_location": {"type": "object", "properties": {o: {"type": "number", "minimum": 0, "maximum": 1}
                                                                for o in offices},
                               "required": offices, "additionalProperties": False}},
        "required": ["p_success", "recipient_location"], "additionalProperties": False}
    return [{"role": "system", "content": prompts["check_system"]}, {"role": "user", "content": user}], schema


def validate_check(offices):
    def v(text):
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            return None, ["not_json"]
        try:
            p = float(obj["p_success"])
            loc = {o: float(obj["recipient_location"][o]) for o in offices}
        except (KeyError, TypeError, ValueError):
            return None, ["schema_violation"]
        if not 0 <= p <= 1 or any(not 0 <= x <= 1 for x in loc.values()):
            return None, ["out_of_range"]
        return {"p_success": p, "recipient_location": loc}, []
    return v


def veto_line(v) -> str:
    return (f"ACTION CHECK: {v.action} was blocked by the robot's action check (estimated success probability {v.p:.2f}; "
            f"its expected value {v.j_commit:.2f} is below {v.v_alt:.2f}, the estimated value of searching for the "
            f"recipient in person). Choose a different action.")


def decision_messages(prompts, cfg, brief, hist, acts: list[str], veto=None):
    msgs, _ = policy_messages(prompts, cfg, brief, hist, None, REV)
    user = msgs[1]["content"]
    head, _legal = user.rsplit("\n\nLEGAL ACTIONS NOW: ", 1)
    extra = (veto_line(veto) + "\n\n") if veto is not None else ""
    user = head + "\n\n" + extra + "LEGAL ACTIONS NOW: " + ", ".join(acts) + '\n\nRespond as JSON: {"action": "<one legal action>"}'
    return [msgs[0], {"role": "user", "content": user}]


def search_step(hist, cfg, loc: dict, excluded) -> Action:
    """Declared scripted fallback: next step of the in-person search (deliver on sight; most probable office first)."""
    o = hist.last
    if cfg.recipient in o.people_present:
        return Action("deliver")
    cand = [x for x in cfg.offices if x not in excluded and x != o.room] or [x for x in cfg.offices if x != o.room]
    target = sorted(cand, key=lambda x: (-loc.get(x, 0.0), cfg.offices.index(x)))[0]
    if o.room == "hall":
        return Action("move", target)
    return Action("move", "hall")


def normalized_loc(loc: dict, cfg, excluded) -> dict:
    keep = {o: max(0.0, float(loc.get(o, 0.0))) for o in cfg.offices if o not in excluded}
    tot = sum(keep.values())
    return {o: v / tot for o, v in keep.items()} if tot > 0 else {o: 1 / len(keep) for o in keep} if keep else {}


# ----------------------------------------------------------------------------- episode
def run_episode(client, st: dict, cond: str, draw: int) -> dict:
    inst = st["inst"]
    sc, cfg = inst.scenario, inst.scenario.config  # sc = PUBLIC model (prior + rules); inst.hidden is never read below
    world = sc.build(inst.hidden)  # the environment (privileged; only world.step observations reach the agent)
    hist = VisibleHistory(sc.brief, [(None, world.reset())])
    prompts = {**load_prompts(PACKAGE), "check_system": CHECK_PROMPT.read_text(encoding="utf-8")}
    dec = decoding()
    calls, steps = [], []
    cache: dict = {}
    n_checks, ask_used, cpu_s = 0, False, 0.0
    start = time.monotonic()

    def decide(acts, veto=None, kind="decision"):
        msgs = decision_messages(prompts, cfg, sc.brief, hist, acts, veto)
        rec = call_with_protocol(client, kind, hist.last.t, "policy", msgs, policy_schema(acts),
                                 lambda txt, acts=acts: (lambda o, e: (o, e) if o is None or o["action"] in acts
                                                         else (None, ["illegal_action"]))(*_json_validate(("action",))(txt)),
                                 dec)
        calls.append(rec)
        return rec

    def check(a: Action, log: dict):
        """Returns (GateVerdict, normalized location) or None (unchecked: cap reached or check failed)."""
        nonlocal n_checks, cpu_s
        excl = excluded_offices(hist, cfg)
        key = (str(a), evidence_signature(hist, cfg))
        info = {}
        if key in cache:
            est = cache[key]
            info["cache_hit"] = True
        elif n_checks >= MAX_CHECKS_PER_EPISODE:
            log["check"] = {"cap_reached": True}
            return None
        else:
            n_checks += 1
            if cond == "checker_gate":
                t = time.perf_counter()
                est = tracker_check(sc, hist, a)
                cpu_s += time.perf_counter() - t
            else:
                msgs, schema = check_messages(prompts, cfg, sc.brief, hist, a)
                rec = call_with_protocol(client, "check", hist.last.t, str(a), msgs, schema,
                                         validate_check(list(cfg.offices)), dec)
                calls.append(rec)
                est = (rec.parsed["p_success"], rec.parsed["recipient_location"]) if rec.ok else None
            cache[key] = est
        if est is None:
            log["check"] = {**info, "failed": True}
            return None
        p, loc = est
        loc_n = normalized_loc(loc, cfg, excl)
        if cfg.recipient in hist.last.people_present:  # deliver() is available now: the alternative is certain
            j = j_commit(p, cfg.stakes)
            v = GateVerdict(str(a), p, j, 0.95, j >= 0.95, cond)
        else:
            v = gate(str(a), p, loc_n, hist.last.room, cfg.horizon - hist.last.t, cfg, excl, cond)
        log["check"] = {**info, "p": round(p, 4), "J": round(v.j_commit, 4), "V_alt": round(v.v_alt, 4), "allow": v.allow}
        return v, loc_n

    while not hist.last.done:
        acts = [str(a) for a in legal_actions(cfg, hist.last)]
        rec = decide(acts)
        proposal = rec.parsed["action"] if rec.ok else FALLBACK_ACTION
        log = {"t": hist.last.t, "proposal": proposal, "policy_ok": rec.ok}
        a = parse(proposal)
        if cond == "ask_first" and is_commit(a) and not ask_used:
            asked = {x.target for x in hist.actions if x.kind == "ask"}
            present = list(hist.last.people_present)
            pref = [a.target] if a.kind == "give" and a.target in present else []
            cands = [p for p in pref + sorted(present) if p not in asked]
            if cands:
                a = Action("ask", cands[0], cfg.query_facts[0])
                ask_used = True
                log["substituted_ask"] = str(a)
        elif cond in ("checker_gate", "generic_gate") and is_commit(a):
            res = check(a, log)
            if res is not None and not res[0].allow:
                v, loc_n = res
                log["veto"] = True
                acts2 = [x for x in acts if x != str(a)]
                rec2 = decide(acts2, veto=v, kind="redecision")
                log["redecision"] = rec2.parsed["action"] if rec2.ok else None
                if not rec2.ok:
                    a = search_step(hist, cfg, loc_n, excluded_offices(hist, cfg))
                    log["scripted_fallback"] = str(a)
                else:
                    a2 = parse(rec2.parsed["action"])
                    if is_commit(a2):
                        log2 = {}
                        res2 = check(a2, log2)
                        log["second_check"] = log2.get("check")
                        if res2 is not None and not res2[0].allow:
                            a2 = search_step(hist, cfg, res2[1], excluded_offices(hist, cfg))
                            log["scripted_fallback"] = str(a2)
                    a = a2
        assert a in legal_actions(cfg, hist.last), (st["state_id"], cond, str(a))
        obs = world.step(a)
        hist.steps.append((a, obs))
        log["executed"] = str(a)
        steps.append(log)
    wall = time.monotonic() - start
    usage = {}
    for r in calls:
        u = r.usage()
        g = usage.setdefault(r.kind, {"calls": 0, "attempts": 0, "attempts_failed": 0, "fallbacks": 0, "prompt_tokens": 0,
                                      "completion_tokens": 0, "reasoning_tokens": 0, "reasoning_known": True,
                                      "latency_s": 0.0})
        g["calls"] += 1
        g["attempts"] += u["calls"]
        g["attempts_failed"] += sum(bool(x["validation_errors"]) for x in r.attempts)
        g["fallbacks"] += int(not r.ok)
        g["prompt_tokens"] += u["prompt_tokens"]
        g["completion_tokens"] += u["completion_tokens"]
        if u["reasoning_tokens"] is None:
            g["reasoning_known"] = False
        else:
            g["reasoning_tokens"] += u["reasoning_tokens"]
        g["latency_s"] += u["latency_s"]
    return {"state_id": st["state_id"], "seed": st["seed"], "base": st["base"], "construction": inst.construction,
            "stakes": inst.variant.stakes, "condition": cond, "draw": draw,
            "actions": [str(a) for a in hist.actions], "steps": steps, "return_": round(sum(o.reward for _, o in hist.steps), 10),
            "outcome": hist.last.outcome, "n_steps": len(hist.actions), "n_checks": n_checks, "checker_cpu_s": cpu_s,
            "wall_clock_s": wall, "usage": usage, "agent_view": hist.to_agent_dict(),
            "calls": [{"kind": r.kind, "step": r.step, "target": r.target, "ok": r.ok, "parsed": r.parsed,
                       "attempts": r.attempts} for r in calls],
            "privileged": {"hidden": [list(x) for x in inst.hidden]}}


# ----------------------------------------------------------------------------- stages
def stage_render(args):
    """Rendered prompts at t0 for the tokenizer forecast (no model calls)."""
    prompts = {**load_prompts(PACKAGE), "check_system": CHECK_PROMPT.read_text(encoding="utf-8")}
    out = []
    for st in states((SMOKE_SEED,)):
        inst = st["inst"]
        if inst.variant.stakes != 1.0:
            continue
        sc, cfg = inst.scenario, inst.scenario.config
        h = VisibleHistory(sc.brief, [(None, sc.build(inst.hidden).reset())])
        acts = [str(a) for a in legal_actions(cfg, h.last)]
        commit = next((parse(x) for x in acts if parse(x).kind in ("give", "drop")), None)
        rec = {"construction": inst.construction, "decision": decision_messages(prompts, cfg, sc.brief, h, acts)}
        if commit is not None:
            v = GateVerdict(str(commit), 0.5, 0.2, 0.8, False, "render")
            rec["redecision"] = decision_messages(prompts, cfg, sc.brief, h, [x for x in acts if x != str(commit)], v)
            rec["check"] = check_messages(prompts, cfg, sc.brief, h, commit)[0]
        out.append(rec)
    BLOCK.mkdir(parents=True, exist_ok=True)
    (BLOCK / "rendered-t0.json").write_bytes(json.dumps(out, indent=1).encode("utf-8"))
    print("rendered", len(out))


def stage_smoke(args):
    """Interface smoke probes (<= 48 of the 96 allowed): one generic check and one re-decision per t0 state of the smoke
    seed, both stakes. Every output is kept; nothing is tuned on them."""
    client = LengthGuard(make_client(json.loads(MODEL_CFG.read_text())))
    prompts = {**load_prompts(PACKAGE), "check_system": CHECK_PROMPT.read_text(encoding="utf-8")}
    jobs = []
    for st in states((SMOKE_SEED,)):
        inst = st["inst"]
        sc, cfg = inst.scenario, inst.scenario.config
        h = VisibleHistory(sc.brief, [(None, sc.build(inst.hidden).reset())])
        acts = [str(a) for a in legal_actions(cfg, h.last)]
        commit = next((parse(x) for x in acts if parse(x).kind in ("give", "drop")), None)
        if commit is None:
            continue
        p, loc = tracker_check(sc, h, commit)
        v = gate(str(commit), p, loc, h.last.room, cfg.horizon, cfg, (), "checker_gate")
        jobs.append(("check", st, h, commit, None))
        jobs.append(("redecision", st, h, commit, v))
    jobs = jobs[:48]

    def run(job):
        kind, st, h, commit, v = job
        cfg, sc = st["inst"].scenario.config, st["inst"].scenario
        if kind == "check":
            msgs, schema = check_messages(prompts, cfg, sc.brief, h, commit)
            rec = call_with_protocol(client, "check", 0, str(commit), msgs, schema, validate_check(list(cfg.offices)),
                                     decoding())
        else:
            acts = [str(a) for a in legal_actions(cfg, h.last) if str(a) != str(commit)]
            msgs = decision_messages(prompts, cfg, sc.brief, h, acts, v)
            rec = call_with_protocol(client, "redecision", 0, "policy", msgs, policy_schema(acts),
                                     _json_validate(("action",)), decoding())
        return {"kind": kind, "state_id": st["state_id"], "commit": str(commit), "ok": rec.ok, "parsed": rec.parsed,
                "attempts": rec.attempts}

    t0 = time.monotonic()
    with ThreadPoolExecutor(CONCURRENCY) as pool:
        res = list(pool.map(run, jobs))
    wall = time.monotonic() - t0
    summ = {"probes": len(res), "ok": sum(r["ok"] for r in res),
            "attempts": sum(len(r["attempts"]) for r in res), "wall_s": round(wall, 1),
            "by_kind": {k: {"n": sum(r["kind"] == k for r in res), "ok": sum(r["ok"] and r["kind"] == k for r in res)}
                        for k in ("check", "redecision")}}
    (BLOCK / "smoke.jsonl").write_bytes("".join(json.dumps(r) + "\n" for r in res).encode("utf-8"))
    (BLOCK / "smoke-summary.json").write_bytes(json.dumps(summ, indent=1).encode("utf-8"))
    print(json.dumps(summ, indent=1))


def code_hashes() -> dict:
    return {f: sha_bytes((ROOT / f).read_bytes()) for f in CODE_FILES}


def stage_freeze(args):
    dirty = [x for x in os.popen(f'git -C "{ROOT}" status --porcelain').read().split("\n") if x.strip()]
    if dirty:
        raise SystemExit(f"freeze needs a clean tree: {dirty}")
    fz = {"block": "D-019 fallback", "git_commit": os.popen(f'git -C "{ROOT}" rev-parse HEAD').read().strip(),
          "code_sha256": code_hashes(), "seeds": list(SEEDS), "conditions": list(CONDS), "draws": DRAWS,
          "decoding": decoding(), "package": PACKAGE, "render_revision": REV, "concurrency": CONCURRENCY,
          "max_checks_per_episode": MAX_CHECKS_PER_EPISODE, "fallback_action": FALLBACK_ACTION,
          "model": json.loads(MODEL_CFG.read_text())["hf_snapshot"],
          "episodes_planned": len(states()) * len(CONDS) * DRAWS,
          "state_ids_sha256": sha_bytes(json.dumps([s["state_id"] for s in states()]).encode())}
    FREEZE.write_bytes(json.dumps(fz, indent=1).encode("utf-8"))
    print(json.dumps(fz, indent=1))


def verify(_args=None) -> dict:
    fz = json.loads(FREEZE.read_text())
    now = code_hashes()
    bad = {f: (fz["code_sha256"].get(f), h) for f, h in now.items() if fz["code_sha256"].get(f) != h}
    if bad:
        raise SystemExit(f"code differs from freeze: {bad}")
    assert fz["state_ids_sha256"] == sha_bytes(json.dumps([s["state_id"] for s in states()]).encode())
    print("verify ok", fz["git_commit"])
    return fz


def stage_pilot(args):
    fz = verify()
    dirty = [x for x in os.popen(f'git -C "{ROOT}" status --porcelain --untracked-files=no').read().split("\n") if x.strip()]
    tracked = os.popen(f'git -C "{ROOT}" ls-files reports/hybrid-block/fallback-freeze.json').read().strip()
    if dirty or not tracked:
        raise SystemExit(f"pilot needs a clean tree with the freeze committed: dirty={dirty} tracked={tracked!r}")
    sts = states()
    per_block = len([s for s in sts if s["seed"] == SEEDS[0]]) * len(CONDS) * DRAWS
    meta = {"stage": "pilot", "freeze_sha256": sha_bytes(FREEZE.read_bytes()), "decoding": decoding(), "draws": DRAWS,
            "concurrency": CONCURRENCY, "limit_s": 7200, "seeds": list(SEEDS)}
    kept, prior_wall, done = [], 0.0, []
    if args.resume:
        out = Path(args.resume)
        manifest = json.loads((out / "manifest-start.json").read_text())
        prev = [json.loads(l) for l in (out / "episodes.jsonl").read_text().splitlines() if l.strip()]
        aborted = []
        for seed in sorted({e["seed"] for e in prev}):
            es = [e for e in prev if e["seed"] == seed]
            (kept if len(es) == per_block else aborted).extend(es)
            if len(es) == per_block:
                done.append(seed)
        with (out / "aborted-episodes.jsonl").open("a") as af:
            af.write("".join(json.dumps(e) + "\n" for e in aborted))
        prior_wall = float(json.loads((out / "progress.json").read_text())["wall_s"]) if (out / "progress.json").exists() else 0.0
        manifest.setdefault("resumes", []).append({"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "kept_blocks": done,
                                                   "aborted_episodes": len(aborted)})
        (out / "episodes.jsonl").write_text("".join(json.dumps(e) + "\n" for e in kept))
    else:
        manifest = runlog.new_manifest("hybrid-fallback", meta)
        out = RUNS / manifest["run_id"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "manifest-start.json").write_text(json.dumps(manifest, indent=1, default=str))
    print("run dir", out, flush=True)
    client = LengthGuard(make_client(json.loads(MODEL_CFG.read_text())))
    t_start = time.monotonic() - prior_wall

    def job(item):
        n, (st, cond, r) = item
        try:
            res = run_episode(client, st, cond, r)
        except Exception as e:  # recorded, never silently retried
            return {"state_id": st["state_id"], "seed": st["seed"], "condition": cond, "draw": r, "dispatch_index": n,
                    "blocked": f"error: {type(e).__name__}: {e}"}
        return {**res, "dispatch_index": n}

    with (out / "episodes.jsonl").open("a") as f, ThreadPoolExecutor(CONCURRENCY) as pool:
        for seed in SEEDS:
            if seed in done:
                continue
            if time.monotonic() - t_start + 15 * 60 > 7200:
                print("serving-time limit: not starting seed block", seed, flush=True)
                break
            block = [s for s in sts if s["seed"] == seed]
            jobs = []
            for r in range(DRAWS):
                for i, st in enumerate(block):
                    for j in range(len(CONDS)):
                        jobs.append((st, CONDS[(i + r + j) % len(CONDS)], r))
            for res in pool.map(job, [(len(done) * 10000 + n, x) for n, x in enumerate(jobs)]):
                f.write(json.dumps(res, default=str) + "\n")
                f.flush()
            done.append(seed)
            (out / "progress.json").write_text(json.dumps({"completed_seed_blocks": done,
                                                           "wall_s": round(time.monotonic() - t_start, 1)}))
            print("seed block done", seed, round(time.monotonic() - t_start), "s", flush=True)
    runlog.finish(manifest, out, wall_clock_s=time.monotonic() - t_start, completed_seed_blocks=done)
    print("out", out, "blocks", len(done))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("render", "smoke", "freeze", "verify", "pilot"))
    ap.add_argument("--resume")
    args = ap.parse_args()
    {"render": stage_render, "smoke": stage_smoke, "freeze": stage_freeze, "verify": verify,
     "pilot": stage_pilot}[args.stage](args)


if __name__ == "__main__":
    main()
