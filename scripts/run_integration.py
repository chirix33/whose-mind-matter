"""Integration diagnostic (D-016): single-decision probe + small API policy check. experiment-plan.md Entries 1, 1a.

    python3 scripts/run_integration.py qualify   # contexts, ask list, statuses, implication table, Bayes sets (no calls)
    python3 scripts/run_integration.py freeze    # integration-freeze.json (clean tree)
    python3 scripts/run_integration.py local     # 1,536 local decisions (resumable)
    python3 scripts/run_integration.py api       # 16 API decisions (one attempt each; capped)
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
sys.path.insert(0, str(ROOT / "scripts"))

from officeminds import devgen3 as G  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from officeminds.world import Action, legal_actions  # noqa: E402
from run_repair import LengthGuard, reference_note, sha  # noqa: E402
from vomi.clients import make_client  # noqa: E402
from vomi.graph import PerspectiveGraph, visible_evidence  # noqa: E402
from vomi.oracle import ExactOracle  # noqa: E402
from vomi.pilot import (call_with_protocol, implication_line, load_prompts, policy_messages, policy_schema,  # noqa: E402
                        _json_validate)
from vomi.units import content  # noqa: E402

PACKAGE, REV = "pilot-v2.2", 7
BLOCK = ROOT / "reports" / "integration-block"
DATA = ROOT / "data" / "integration-block"
FREEZE = BLOCK / "integration-freeze.json"
SEEDS = tuple(20261200 + k for k in range(8))
CONS = ("2a", "2b", "3a", "3b")
DRAWS = 3
T0_CONDS = ("none", "content", "impl")
POST_CONDS = ("none", "content|shown", "content|omitted", "impl|shown", "impl|omitted")
LOCAL_CFG = ROOT / "configs" / "models" / "local_gpt_oss_20b.json"
API_CFG = ROOT / "configs" / "models" / "api_gpt_6_1_sol.json"
CONCURRENCY = 8


def states():
    out = []
    for seed in SEEDS:
        for inst in G.generate(seed):
            if inst.construction in CONS and not inst.variant.permuted:
                out.append({"state_id": f"s{seed}-{inst.instance_id}", "seed": seed, "inst": inst,
                            "units": sorted(G.focal_units(inst), key=str)})
    assert len(out) == 64
    return out


def ask_of(st):
    """RC1: subject = path[0] of the first focal unit in canonical (alphabetical) order; the task's query fact."""
    u = st["units"][0]
    subj = u.path[0]
    role = next(r for r, n in st["inst"].role.items() if n == subj)
    return Action("ask", subj, st["inst"].scenario.config.query_facts[0]), role


def contexts(st):
    """(t0 world, t0 history, post-ask world, post-ask history)."""
    inst = st["inst"]
    w0 = inst.scenario.build(inst.hidden)
    h0 = VisibleHistory(inst.scenario.brief, [(None, w0.reset())])
    w1 = w0.clone()
    a, _ = ask_of(st)
    assert a in legal_actions(w0.config, h0.last), (st["state_id"], a)
    h1 = VisibleHistory(inst.scenario.brief, list(h0.steps) + [(a, w1.step(a))])
    return w0, h0, w1, h1


def frozen_notes(st):
    return {str(u): reference_note(st["inst"], u)[0] for u in st["units"]}


def graph_for(st, hist, notes):
    g = PerspectiveGraph(recipient=st["inst"].scenario.config.recipient, refutation_mode="fact_only")
    for u in st["units"]:
        g.instantiate(u, notes[str(u)], [], t=0, cost=0.0)
    if hist.last.t > 0:
        g.advance(hist)  # unchanged graph semantics (RC2): statuses computed, never set by hand
    return g


def render_opts(cond):
    if cond == "none":
        return None
    kind, _, stale = cond.partition("|")
    return {"implication": kind == "impl", "show_stale": stale != "omitted"}


def prompt(st, ctx, cond, notes, hist=None):
    inst = st["inst"]
    if hist is None:
        _, h0, _, h1 = contexts(st)
        hist = h0 if ctx == "t0" else h1
    g = None if cond == "none" else graph_for(st, hist, notes)
    msgs, acts = policy_messages(load_prompts(PACKAGE), inst.scenario.config, inst.scenario.brief, hist, g, REV,
                                 render_opts(cond) if cond != "none" else None)
    return msgs, acts


def bayes(scenario, hist):
    o = ExactOracle(scenario, hist)
    qs = {str(a): q for a, q in o.ranked_actions(o.belief, o.obs)}
    best = max(qs.values())
    return qs, sorted(a for a, q in qs.items() if q >= best - 1e-9), o


# ----------------------------------------------------------------------------- qualification (no calls)
def stage_qualify(args):
    rows, imp_rows = [], []
    for st in states():
        inst = st["inst"]
        cfg = inst.scenario.config
        w0, h0, w1, h1 = contexts(st)
        notes = frozen_notes(st)
        a, role = ask_of(st)
        g1 = graph_for(st, h1, notes)
        statuses = {r["unit"]: r["status"] for r in g1.policy_view()}
        assert set(statuses.values()) <= {"stale", "retained", "fresh"}, statuses  # RC2: only stale may appear
        triggers = {str(u): [e for e in visible_evidence(h1, u.path) if int(e.split(":")[0][1:]) > 0] for u in st["units"]}
        q0, opt0, o0 = bayes(inst.scenario, h0)
        q1, opt1, o1 = bayes(inst.scenario, h1)
        sym = {}
        for u in st["units"]:
            post0 = {}
            for p, x in o0.belief:
                post0[content(x, u)[0]] = post0.get(content(x, u)[0], 0) + p
            post1 = {}
            for p, x in o1.belief:
                post1[content(x, u)[0]] = post1.get(content(x, u)[0], 0) + p
            sym[str(u)] = {"true_content_unchanged": content(w0, u) == content(w1, u),
                           "posterior_unchanged": all(abs(post0.get(k, 0) - post1.get(k, 0)) < 1e-9 for k in set(post0) | set(post1)),
                           "posterior_t0": post0, "posterior_post_ask": post1}
            mass = {h["value"]: h["p"] for h in notes[str(u)]["hypotheses"]}
            line = implication_line(u, mass, cfg)
            if line:
                give = Action("give", u.path[0])
                ps = pw = 0.0
                for p, x in o0.belief:
                    y = x.clone()
                    out = y.step(give).outcome
                    ps += p * (out == "success")
                    pw += p * (out == "error")
                imp_rows.append({"state_id": st["state_id"], "unit": str(u), "note_distribution": mass, "line": line,
                                 "destination_distribution": mass, "p_success_given_give": round(ps, 6),
                                 "p_wrong_given_give": round(pw, 6), "unknown_mass": mass.get("unknown", 0.0)})
        p_t0 = {c: sha(prompt(st, "t0", c, notes, h0)[0][1]["content"]) for c in ("none", "content|shown", "content|omitted",
                                                                               "impl|shown", "impl|omitted")}
        assert p_t0["content|shown"] == p_t0["content|omitted"] and p_t0["impl|shown"] == p_t0["impl|omitted"]
        p_post = {c: sha(prompt(st, "post", c, notes, h1)[0][1]["content"]) for c in POST_CONDS}
        assert len(set(p_post.values())) == 5, (st["state_id"], "post-ask prompts must all differ")
        rows.append({"state_id": st["state_id"], "seed": st["seed"], "construction": inst.construction,
                     "stakes": inst.variant.stakes, "ask": str(a), "ask_subject_role": role,
                     "post_ask_statuses": statuses, "stale_triggers": triggers, "symbolic": sym,
                     "bayes_opt_t0": opt0, "bayes_v_t0": max(q0.values()), "bayes_opt_post": opt1,
                     "bayes_v_post": max(q1.values()), "note_sha256": {k: sha(v) for k, v in notes.items()},
                     "prompt_sha256_t0": {"none": p_t0["none"], "content": p_t0["content|shown"], "impl": p_t0["impl|shown"]},
                     "prompt_sha256_post": p_post})
    assert all(r["unknown_mass"] < 0.005 for r in imp_rows)
    out = {"states": rows, "implication_table": imp_rows,
           "implication_template": "Given this estimate and the stated forwarding rule, give(<X>) sends the package to "
                                   "<office> with probability <p>[, to <office> with probability <p> ...].",
           "checks": {"states": len(rows), "implication_lines": len(imp_rows),
                      "any_unknown_mass": any(r["unknown_mass"] >= 0.005 for r in imp_rows),
                      "only_stale_status_post_ask": all(set(r["post_ask_statuses"].values()) <= {"stale"} for r in rows),
                      "t0_duplicate_prompts_identical": True}}
    out["implication_table_sha256"] = sha(imp_rows)
    BLOCK.mkdir(parents=True, exist_ok=True)
    (BLOCK / "qualification.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out["checks"]))
    for r in imp_rows[:8]:
        print(r["state_id"], r["unit"], r["line"], "P(success|give)", r["p_success_given_give"])


# ----------------------------------------------------------------------------- freeze
SRC = ["src/vomi/pilot.py", "src/vomi/graph.py", "src/vomi/oracle.py", "src/vomi/units.py", "src/vomi/clients.py",
       "src/officeminds/devgen3.py", "src/officeminds/world.py", "scripts/run_integration.py",
       "scripts/report_integration.py", "scripts/run_repair.py", "prompts/pilot-v1/policy_system.txt",
       "configs/models/local_gpt_oss_20b.json", "configs/models/api_gpt_6_1_sol.json"]


def jobs():
    out = []
    sts = states()
    for d in range(DRAWS):
        for i, st in enumerate(sts):
            for ctx, conds in (("t0", T0_CONDS), ("post", POST_CONDS)):
                for j in range(len(conds)):
                    out.append((st["state_id"], ctx, conds[(i + d + j) % len(conds)], d))
    assert len(out) == 1536
    return out


def api_selection():
    sel = []
    sts = {st["state_id"]: st for st in states()}
    for c in CONS:
        k = int(hashlib.sha256(f"integration:api:{c}".encode()).hexdigest(), 16) % 8
        stakes = 4 if int(hashlib.sha256(f"integration:api:stakes:{c}".encode()).hexdigest(), 16) % 2 else 1
        sid = f"s{SEEDS[k]}-{G.DEV_VERSION}-{c}-stakes{stakes}-perm0"
        assert sid in sts
        sel += [(sid, "t0"), (sid, "post")]
    return sel


def stage_freeze(args):
    dirty = [x for x in os.popen(f'git -C "{ROOT}" status --porcelain').read().split("\n") if x.strip()]
    if dirty:
        raise SystemExit(f"freeze needs a clean tree: {dirty}")
    q = json.loads((BLOCK / "qualification.json").read_text())
    fz = {"created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
          "git_commit": os.popen(f'git -C "{ROOT}" rev-parse HEAD').read().strip(),
          "seeds": SEEDS, "constructions": CONS, "draws": DRAWS, "t0_conditions": T0_CONDS, "post_conditions": POST_CONDS,
          "asks": {r["state_id"]: [r["ask"], r["ask_subject_role"]] for r in q["states"]},
          "note_sha256": {r["state_id"]: r["note_sha256"] for r in q["states"]},
          "prompt_sha256": {r["state_id"]: {"t0": r["prompt_sha256_t0"], "post": r["prompt_sha256_post"]} for r in q["states"]},
          "bayes_optimal": {r["state_id"]: {"t0": r["bayes_opt_t0"], "post": r["bayes_opt_post"]} for r in q["states"]},
          "implication_table_sha256": q["implication_table_sha256"],
          "qualification_sha256": hashlib.sha256((BLOCK / "qualification.json").read_bytes()).hexdigest(),
          "source_sha256": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in SRC},
          "local_decoding": {**json.loads(LOCAL_CFG.read_text())["decoding"], "temperature": 1.0, "max_tokens": 1024},
          "api": {"model": json.loads(API_CFG.read_text())["model"], "reasoning_effort": "low", "max_output_tokens": 2000,
                  "attempts": 1, "selection": api_selection()},
          "dispatch_order": jobs(), "concurrency": CONCURRENCY,
          "cache_policy": "no cache: every (state, context, condition, draw) is a fresh call; the draw index is part of the "
                          "record key; nothing is replayed"}
    FREEZE.write_text(json.dumps(fz, indent=1, sort_keys=True) + "\n")
    print("freeze written;", len(fz["dispatch_order"]), "local decisions;", len(fz["api"]["selection"]), "API contexts")


def verify():
    fz = json.loads(FREEZE.read_text())
    bad = [f for f, h in fz["source_sha256"].items() if hashlib.sha256((ROOT / f).read_bytes()).hexdigest() != h]
    if hashlib.sha256((BLOCK / "qualification.json").read_bytes()).hexdigest() != fz["qualification_sha256"]:
        bad.append("qualification")
    if bad:
        raise SystemExit(f"FREEZE MISMATCH: {bad}")
    return fz


# ----------------------------------------------------------------------------- decisions
def decide(client, st, ctx, cond, decoding, attempts=3):
    notes = frozen_notes(st)
    w0, h0, w1, h1 = contexts(st)
    hist, world = (h0, w0) if ctx == "t0" else (h1, w1)
    msgs, acts = prompt(st, ctx, cond, notes, hist)
    validate = (lambda txt, acts=acts: (lambda o, e: (o, e) if o is None or o["action"] in acts else (None, ["illegal_action"]))(
        *_json_validate(("action",))(txt)))
    if attempts == 1:
        params = dict(decoding)
        params["response_format"] = {"type": "json_schema", "json_schema": {"name": "decision", "schema": policy_schema(acts)}}
        r = client.chat(msgs, **params)
        parsed, errors = (None, ["request_error"]) if r.error else validate(r.text)
        rec = {"attempts": [{"text": r.text, "reasoning": r.reasoning, "finish_reason": r.finish_reason,
                             "prompt_tokens": r.prompt_tokens, "completion_tokens": r.completion_tokens,
                             "reasoning_tokens": r.reasoning_tokens, "latency_s": r.latency_s, "error": r.error,
                             "validation_errors": errors}], "ok": parsed is not None, "parsed": parsed}
    else:
        rec = asdict(call_with_protocol(client, "decision", hist.last.t, "policy", msgs, policy_schema(acts), validate, decoding))
    action = rec["parsed"]["action"] if rec["ok"] else "wait()"
    a = next(x for x in legal_actions(st["inst"].scenario.config, hist.last) if str(x) == action)
    y = world.clone()
    out = y.step(a).outcome
    qs, opt, _ = bayes(st["inst"].scenario, hist)
    return {"action": action, "fallback": not rec["ok"], "outcome_if_taken": out, "wrong": out == "error",
            "correct_handoff": a.kind in ("give", "drop") and out == "success", "handoff": a.kind in ("give", "drop"),
            "gap": max(qs.values()) - qs[action], "bayes_optimal": opt, "prompt_sha256": sha(msgs[1]["content"]),
            "call": rec}


def stage_local(args):
    fz = verify()
    sts = {st["state_id"]: st for st in states()}
    client = LengthGuard(make_client(json.loads(LOCAL_CFG.read_text())))
    decoding = fz["local_decoding"]
    DATA.mkdir(parents=True, exist_ok=True)
    part = DATA / "local-decisions.jsonl"  # resumable: finished decisions are kept and skipped on rerun
    done = set()
    if part.exists():
        for l in part.read_text().splitlines():
            if l.strip():
                r = json.loads(l)
                done.add((r["state_id"], r["context"], r["condition"], r["draw"]))
    todo = [tuple(j) for j in fz["dispatch_order"] if tuple(j) not in done]
    t_start = time.monotonic()

    def job(j):
        sid, ctx, cond, d = j
        r = decide(client, sts[sid], ctx, cond, decoding)
        assert r["prompt_sha256"] == fz["prompt_sha256"][sid][ctx][cond if ctx == "post" else cond.split("|")[0]]
        return {"state_id": sid, "context": ctx, "condition": cond, "draw": d, **r}

    with ThreadPoolExecutor(CONCURRENCY) as pool, part.open("a") as f:
        for r in pool.map(job, todo):
            f.write(json.dumps(r, default=str) + "\n")
            f.flush()
    seg = {"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "decisions": len(todo), "wall_s": round(time.monotonic() - t_start, 1)}
    log = DATA / "local-segments.json"
    segs = json.loads(log.read_text()) if log.exists() else []
    log.write_text(json.dumps(segs + [seg], indent=1))
    print("local decisions done:", len(done) + len(todo), seg)


def stage_api(args):
    fz = verify()
    cfg = json.loads(API_CFG.read_text())
    sts = {st["state_id"]: st for st in states()}
    sel = [tuple(x) for x in fz["api"]["selection"]]
    price_in, price_out = cfg["price_per_mtok"]["input"] / 1e6, cfg["price_per_mtok"]["output"] / 1e6
    prompts_ = []
    for sid, ctx in sel:
        for cond in ("none", "content|shown"):
            msgs, _ = prompt(sts[sid], ctx, cond if ctx == "post" else cond.split("|")[0], frozen_notes(sts[sid]))
            prompts_.append((sid, ctx, cond, msgs))
    # conservative ceiling: 1 token per 2 characters of the full request (system + user)
    worst = sum((len(m[0]["content"]) + len(m[1]["content"])) / 2 * price_in for *_, m in prompts_) \
        + len(prompts_) * fz["api"]["max_output_tokens"] * price_out
    led = json.load(open(os.path.expanduser(cfg["budget"]["ledger_path"])))
    spent = led["spent_usd"] + led.get("unresolved_usd", 0) + sum(led.get("reserved", {}).values())
    plan = {"calls": len(prompts_), "worst_case_usd": round(worst, 4), "reconciled_committed_usd": round(spent, 5),
            "stage_cap_usd": round(spent + 0.50, 5)}
    print(json.dumps(plan))
    if worst > 0.50 or spent + worst >= 5.0:
        (BLOCK / "api-check-skipped.json").write_text(json.dumps({**plan, "skipped": "worst case does not fit"}, indent=1))
        raise SystemExit("API check skipped: worst case does not fit the caps")
    os.environ["OFFICEMINDS_API_CAP_USD"] = str(spent + 0.50)
    client = make_client(cfg)
    decoding = {"reasoning_effort": "low", "max_tokens": fz["api"]["max_output_tokens"]}
    out = []
    for sid, ctx, cond, _ in prompts_:  # one attempt each, no retries
        r = decide(client, sts[sid], ctx, cond if ctx == "post" else cond.split("|")[0], decoding, attempts=1)
        out.append({"state_id": sid, "context": ctx, "condition": cond, **r})
    led2 = json.load(open(os.path.expanduser(cfg["budget"]["ledger_path"])))
    res = {**plan, "ledger_after_usd": led2["spent_usd"], "incremental_usd": round(led2["spent_usd"] - led["spent_usd"], 5),
           "decisions": out}
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "api-decisions.json").write_text(json.dumps(res, indent=1, default=str))
    pub = {k: v for k, v in res.items() if k != "decisions"}
    pub["decisions"] = [{k: v for k, v in d.items() if k != "call"} | {"finish_reason": d["call"]["attempts"][0]["finish_reason"],
                                                                      "tokens": [d["call"]["attempts"][0]["prompt_tokens"],
                                                                                 d["call"]["attempts"][0]["completion_tokens"]]}
                        for d in out]
    (BLOCK / "api-check.json").write_text(json.dumps(pub, indent=1, default=str) + "\n")
    print("API check done; incremental USD", res["incremental_usd"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("qualify", "freeze", "local", "api"))
    args = ap.parse_args()
    {"qualify": stage_qualify, "freeze": stage_freeze, "local": stage_local, "api": stage_api}[args.stage](args)


if __name__ == "__main__":
    main()
