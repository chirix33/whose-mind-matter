"""Repair block (D-015) runner: reports/repair-block/experiment-plan.md Entries 1, 1a, 2.

    python3 scripts/run_repair.py qualify            # RC12: symbolic checks on every Stage 2 fresh-seed instance
    python3 scripts/run_repair.py regress            # Stage 1 regression check on inspected Round B states (local)
    python3 scripts/run_repair.py freeze             # stage1-freeze.json (clean tree)
    python3 scripts/run_repair.py verify             # current code == freeze
    python3 scripts/run_repair.py notes              # Stage 2 frozen note payloads (all seeds)
    python3 scripts/run_repair.py policy             # Stage 2 policy, complete seed blocks

Package pilot-v2.2, render r7 (citable PM IDs, matched notes), local gpt-oss-20b. Notes: temperature 1.0, max_tokens
2048; policy: temperature 1.0, max_tokens 1024; reasoning low; up to 3 attempts; truncation = failed attempt.
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
from vomi import runlog  # noqa: E402
from vomi.clients import make_client  # noqa: E402
from vomi.graph import PerspectiveGraph  # noqa: E402
from vomi.oracle import ExactOracle  # noqa: E402
from vomi.pilot import (PACKAGES, call_with_protocol, describe_unit, load_prompts, policy_messages,  # noqa: E402
                        prompt_hashes, run_episode_arm, unit_messages)
from vomi.units import K, content  # noqa: E402

PACKAGE, REV = "pilot-v2.2", 7
BLOCK = ROOT / "reports" / "repair-block"
DATA = ROOT / "data" / "repair-block"  # PRIVILEGED payloads (gitignored)
FREEZE = BLOCK / "stage1-freeze.json"
RUNS = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "repair"
SEED0 = 20261100
CONCURRENCY = 8
MODEL_CFG = ROOT / "configs" / "models" / "local_gpt_oss_20b.json"
CONDS = ("none", "inferred", "reference")
DEPTH_CONDS = ("inferred_KR", "reference_KR")
MARKERS = ("[PM1]", "Watching a quiet conversation tells a bystander nothing")


def sha(obj) -> str:
    return hashlib.sha256((obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True)).encode()).hexdigest()


class LengthGuard:
    def __init__(self, inner):
        self.inner, self.model = inner, getattr(inner, "model", "?")

    def chat(self, messages, **params):
        r = self.inner.chat(messages, **params)
        if (r.finish_reason == "length" or str(r.finish_reason or "").startswith("incomplete")) and not r.error:
            r.error = "truncated: finish_reason=length"
        return r


def decoding(kind):
    d = dict(json.loads(MODEL_CFG.read_text())["decoding"])
    return {**d, "temperature": 1.0, "max_tokens": 2048 if kind == "notes" else 1024}


def chosen_k() -> int:
    return json.loads((BLOCK / "power.json").read_text())["chosen_K"]


def stage2_states(k_max: int | None = None):
    """Seed-qualified t0 states: every construction's unpermuted x1 and x4 variants, seeds SEED0 + k."""
    out = []
    for k in range(k_max if k_max is not None else chosen_k()):
        seed = SEED0 + k
        for inst in G.generate(seed):
            if inst.variant.permuted:
                continue
            units = G.focal_units(inst)
            conds = {c: units for c in CONDS}
            if inst.stratum == 3:
                kr = [K(inst.role["R"])]
                conds.update({"inferred_KR": kr, "reference_KR": kr})
            out.append({"state_id": f"s{seed}-{inst.instance_id}", "seed": seed, "k": k, "inst": inst, "conds": conds})
    return out


def t0(inst):
    w = inst.scenario.build(inst.hidden)
    return w, VisibleHistory(inst.scenario.brief, [(None, w.reset())])


def reference_note(inst, u) -> tuple[dict, dict]:
    w, h = t0(inst)
    o = ExactOracle(inst.scenario, h)  # plain posterior b_h under the declared public model
    dist = {}
    for p, x in o.belief:
        v = content(x, u)[0]
        dist[v] = dist.get(v, 0.0) + p
    hyps = [{"value": v, "p": round(p, 6)} for v, p in sorted(dist.items()) if p > 0]
    note = {"path": list(u.path), "variable": u.variable, "about": describe_unit(u, inst.scenario.config)[1],
            "as_of_step": 0, "status": "grounded" if max(dist.values()) >= 0.8 else "uncertain", "hypotheses": hyps,
            "unresolved": [], "evidence_ids": [], "rule_ids": [], "source": "reference"}
    return note, dist


def infer_note(client, inst, u):
    cfg = inst.scenario.config
    _, h = t0(inst)
    pkg = PACKAGES[PACKAGE]
    msgs, domain, ids = unit_messages(load_prompts(PACKAGE), cfg, inst.scenario.brief, h, u, PACKAGE, REV)
    assert all(m in msgs[1]["content"] for m in MARKERS)
    return call_with_protocol(client, "unit", 0, str(u), msgs, pkg.schema(domain, u.variable),
                              lambda t: pkg.validate(t, u.path, u.variable, domain, ids), decoding("notes"))


# ----------------------------------------------------------------------------- RC12 symbolic qualification
def stage_qualify(args):
    import qualify_dev_v3 as Q
    sys.path.insert(0, str(ROOT / "tests"))
    import test_dev_v3 as T
    sts = stage2_states()
    insts = [s["inst"] for s in sts]
    T.INSTS, T.BY_ID = insts, {i.instance_id: i for i in insts}
    rule_tests = ["test_rule1_and_rule5_quiet_conversations", "test_rule2_recipient_knows_own_office",
                  "test_rule2_lobby_sightings_change_no_beliefs", "test_rule3_statements_are_not_adopted_and_give_speaker_nothing",
                  "test_rule4_remarks_change_nothing", "test_rule5_nested_beliefs_only_from_statements_and_announcements",
                  "test_rule6_only_declared_people_may_mislead", "test_designed_contents", "test_evidence_resolved_access_status",
                  "test_card_has_r6_and_public_model_and_no_hidden_values", "test_reference_inputs_are_the_disclosed_spec",
                  "test_agent_visible_text_has_no_design_labels"]
    results = {}
    for name in rule_tests:
        try:
            getattr(T, name)()
            results[name] = "pass"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
    recs, t_start = [], time.monotonic()
    for st in sts:
        r = Q.instance_record(st["inst"])
        recs.append({"state_id": st["state_id"], "seed": st["seed"], "construction": r["construction"],
                     "stakes": r["stakes"], "rates": {k: float(v) for k, v in st["inst"].spec.rates},
                     "optimal": r["optimal_first_actions"], "bayes_value_t0": r["bayes_value_t0"],
                     "focal": r["focal"], "focal_in_candidates": r["focal_in_candidates"],
                     "superset_ok": (r["superset"]["max_abs_q_diff"] < 1e-9 and r["superset"]["focal_posterior_equal"])
                     if "superset" in r else None, "oracle_seconds": r["oracle_seconds"]})
    by = {}
    for r in recs:
        by.setdefault((r["seed"], r["construction"]), {})[r["stakes"]] = r
    flips = {f"{s}|{c}": v[1.0]["optimal"] != v[4.0]["optimal"] for (s, c), v in by.items() if c.startswith("4")}
    checks = {"states": len(recs), "seeds": len({r["seed"] for r in recs}), "rule_and_text_tests": results,
              "access_status_unique_strata_1_3": all(len(f["access_status_set"]) == 1 for r in recs
                                                    if r["construction"][0] in "123" for f in r["focal"]),
              "focal_in_candidates_all": all(r["focal_in_candidates"] for r in recs),
              "superset_ok_all": all(r["superset_ok"] for r in recs if r["superset_ok"] is not None),
              "stratum4_flip": {"all": all(flips.values()), "failing": sorted(k for k, v in flips.items() if not v)},
              "max_oracle_seconds": max(r["oracle_seconds"] for r in recs),
              "wall_s": round(time.monotonic() - t_start, 1)}
    (BLOCK / "stage2-qualification.json").write_text(json.dumps({"checks": checks, "states": recs}, indent=1,
                                                                sort_keys=True) + "\n")
    print(json.dumps(checks, indent=1))


# ----------------------------------------------------------------------------- Stage 1 regression (inspected material)
def stage_regress(args):
    sel = {"1c", "2a", "3c", "4b"}
    insts = [i for i in G.generate() if i.construction in sel]
    jobs = [(i, u) for i in insts for u in G.focal_units(i)] + [(i, K(i.role["R"])) for i in insts if i.stratum == 3]
    client = LengthGuard(make_client(json.loads(MODEL_CFG.read_text())))
    tag = time.strftime("%Y%m%d-%H%M%S")

    def job(item):
        inst, u = item
        rec = infer_note(client, inst, u)
        _, dist = reference_note(inst, u)
        return inst, u, rec, dist

    rows = []
    with ThreadPoolExecutor(CONCURRENCY) as pool:
        for inst, u, rec, dist in pool.map(job, jobs):
            rows.append(score_row(inst, u, rec.parsed if rec.ok else None, dist, rec))
    out = {"label": "Stage 1 regression check on INSPECTED dev-v3 Round B states (development/debugging only; "
                    "temperature-1.0 single draws; no content pass/fail threshold)", "run": tag,
           "prompt_sha256": prompt_hashes(PACKAGE)["unit_system"], "decoding": decoding("notes"), "rows": rows,
           "summary": summarize(rows)}
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / f"regress-{tag}.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str))
    pub = {k: v for k, v in out.items() if k != "rows"}
    pub["rows"] = [{k: v for k, v in r.items() if k not in ("call",)} for r in rows]
    (BLOCK / f"stage1-regress-{tag}.json").write_text(json.dumps(pub, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps(out["summary"], indent=1))


def score_row(inst, u, parsed, dist, rec=None):
    from vomi.fidelity import robot_known_values, score_output_v3
    w, h = t0(inst)
    cfg = inst.scenario.config
    domain = list(cfg.fact_domains[cfg.query_facts[0]])
    vals = PACKAGES[PACKAGE].schema(domain, u.variable)["properties"]["hypotheses"]["items"]["properties"]["value"]["enum"]
    s = score_output_v3(parsed, content(w, u)[0], dist, robot_known_values(h, cfg.recipient), vals, False)
    prior_copy = prior_copy_discriminating = prior = None
    if u.variable == "reliability" and parsed:
        r = dict(inst.spec.rates)
        key = {"X": "r_X", "Y": "r_Y"}.get(next(k for k, v in inst.role.items() if v == u.path[0]), "r_incentive")
        prior = float(r.get(key, r.get("r_incentive", 0)))
        pm = {h_["value"]: h_["p"] for h_ in parsed["hypotheses"]}
        prior_copy = abs(pm.get("obstructive", 0) - prior) <= 0.02 and abs(pm.get("cooperative", 0) - (1 - prior)) <= 0.02
        # R1 (Stage 1 results gate; defined AFTER the Stage 1 output): a copy is only diagnosable where the posterior
        # is far from the prior. The raw flag is kept.
        prior_copy_discriminating = prior_copy and abs(dist.get("obstructive", 0.0) - prior) > 0.04
    errs = [a["validation_errors"] for a in (rec.attempts if rec else [])]
    return {"state": inst.instance_id, "unit": str(u), "ok": parsed is not None, "category": s.get("category"),
            "tv_posterior": s.get("tv_posterior"), "unsupported_mass": s.get("unsupported_mass"),
            "top": s.get("top"), "posterior": dist, "status": (parsed or {}).get("status"),
            "distribution": {h_["value"]: h_["p"] for h_ in (parsed or {}).get("hypotheses", [])},
            "prior_copy": prior_copy, "prior_copy_discriminating": prior_copy_discriminating,
            "prior": prior if u.variable == "reliability" and parsed else None, "attempt_errors": errs,
            "public_model_ids": (parsed or {}).get("public_model_ids"), "call": asdict(rec) if rec else None}


def summarize(rows):
    ok = [r for r in rows if r["ok"]]
    rel = [r for r in ok if r["unit"].startswith("R(")]
    return {"notes": len(rows), "valid": len(ok), "coverage": round(len(ok) / len(rows), 3),
            "mean_tv": round(sum(r["tv_posterior"] for r in ok) / len(ok), 4) if ok else None,
            "mean_unsupported_mass": round(sum(r["unsupported_mass"] for r in ok) / len(ok), 4) if ok else None,
            "categories": {c: sum(r["category"] == c for r in rows) for c in sorted({str(r["category"]) for r in rows})},
            "reliability_prior_copies": f"{sum(bool(r['prior_copy']) for r in rel)}/{len(rel)}",
            "reliability_prior_copies_discriminating": (
                f"{sum(bool(r.get('prior_copy_discriminating')) for r in rel)}/"
                f"{sum(r.get('prior') is not None and abs(r['posterior'].get('obstructive', 0.0) - r['prior']) > 0.04 for r in rel)}"),
            "notes_citing_pm": sum(bool(r["public_model_ids"]) for r in ok)}


# ----------------------------------------------------------------------------- freeze / verify
FROZEN_SOURCES = ["src/officeminds/devgen3.py", "src/officeminds/world.py", "src/officeminds/scenarios.py",
                  "src/officeminds/episode.py", "src/vomi/oracle.py", "src/vomi/units.py", "src/vomi/pilot.py",
                  "src/vomi/fidelity.py", "src/vomi/unit_schema.py", "src/vomi/graph.py", "src/vomi/clients.py",
                  "scripts/run_repair.py", "scripts/report_repair_stage2.py", "scripts/power_repair_stage2.py",
                  "scripts/qualify_dev_v3.py", "prompts/pilot-v1/policy_system.txt", "prompts/pilot-v2.2/unit_system.txt"]


def stage_freeze(args):
    dirty = [x for x in os.popen(f'git -C "{ROOT}" status --porcelain').read().split("\n") if x.strip()]
    if dirty:
        raise SystemExit(f"freeze needs a clean tree: {dirty}")
    sts = stage2_states()
    prompts = load_prompts(PACKAGE)
    rows = {}
    for st in sts:
        inst = st["inst"]
        _, h = t0(inst)
        cfg = inst.scenario.config
        rows[st["state_id"]] = {"agent_view_t0_sha256": sha(json.dumps(h.to_agent_dict(), sort_keys=True)),
                                "policy_prompt_t0_direct_sha256": sha(policy_messages(prompts, cfg, inst.scenario.brief, h, None, REV)[0][1]["content"]),
                                "conditions": {c: [str(u) for u in us] for c, us in st["conds"].items()}}
    fz = {"created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
          "git_commit": os.popen(f'git -C "{ROOT}" rev-parse HEAD').read().strip(), "package": PACKAGE,
          "render_revision": REV, "prompt_sha256": prompt_hashes(PACKAGE),
          "source_sha256": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in FROZEN_SOURCES},
          "power_sha256": hashlib.sha256((BLOCK / "power.json").read_bytes()).hexdigest(), "K": chosen_k(),
          "model_config_sha256": hashlib.sha256(MODEL_CFG.read_bytes()).hexdigest(),
          "seeds": [SEED0 + k for k in range(chosen_k())], "notes_decoding": decoding("notes"),
          "policy_decoding": decoding("policy"), "concurrency": CONCURRENCY, "draws": 2,
          "model": json.loads(MODEL_CFG.read_text())["hf_snapshot"],
          "qualification_sha256": hashlib.sha256((BLOCK / "stage2-qualification.json").read_bytes()).hexdigest(),
          "states": rows}
    FREEZE.write_text(json.dumps(fz, indent=1, sort_keys=True) + "\n")
    print("freeze", len(rows), "states, K =", fz["K"])


def verify(_args=None):
    fz = json.loads(FREEZE.read_text())
    bad = [f for f, hsh in fz["source_sha256"].items() if hashlib.sha256((ROOT / f).read_bytes()).hexdigest() != hsh]
    if prompt_hashes(PACKAGE) != fz["prompt_sha256"]:
        bad.append("prompts")
    for key, path in (("power_sha256", BLOCK / "power.json"), ("qualification_sha256", BLOCK / "stage2-qualification.json"),
                      ("model_config_sha256", MODEL_CFG)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != fz[key]:
            bad.append(key)
    if decoding("notes") != fz["notes_decoding"] or decoding("policy") != fz["policy_decoding"]:
        bad.append("decoding")
    prompts = load_prompts(PACKAGE)
    for st in stage2_states(fz["K"]):
        row = fz["states"][st["state_id"]]
        inst = st["inst"]
        _, h = t0(inst)
        if sha(json.dumps(h.to_agent_dict(), sort_keys=True)) != row["agent_view_t0_sha256"]:
            bad.append(st["state_id"])
    if bad:
        raise SystemExit(f"FREEZE MISMATCH: {bad[:10]}")
    print("freeze verified", len(fz["states"]), "states")
    return fz


# ----------------------------------------------------------------------------- Stage 2 notes and policy
NOTES = DATA / "stage2-notes.json"


def stage_notes(args):
    fz = verify()
    if NOTES.exists():
        raise SystemExit("notes frozen; refusing to regenerate")
    sts = stage2_states(fz["K"])
    client = LengthGuard(make_client(json.loads(MODEL_CFG.read_text())))
    jobs = sorted({(st["state_id"], str(u)) for st in sts for c, us in st["conds"].items() if c.startswith("inferred")
                   for u in us})
    by = {st["state_id"]: st for st in sts}

    def job(item):
        sid, us = item
        st = by[sid]
        u = next(u for c, uu in st["conds"].items() for u in uu if str(u) == us)
        return sid, us, infer_note(client, st["inst"], u)

    out = {"started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "freeze_sha256": hashlib.sha256(FREEZE.read_bytes()).hexdigest(),
           "states": {}}
    t_start = time.monotonic()
    partial = DATA / "stage2-notes-partial.jsonl"  # resumable after a machine restart: finished calls are kept
    DATA.mkdir(parents=True, exist_ok=True)
    done = {}
    if partial.exists():
        for line in partial.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done[(r["sid"], r["unit"])] = r
    out["resumed_calls"] = len(done)
    seg = time.strftime("%Y%m%d-%H%M%S")
    segs = {}
    for r in done.values():  # earlier segments: each one's elapsed time is its largest recorded elapsed
        segs[r.get("segment", "?")] = max(segs.get(r.get("segment", "?"), 0.0), r.get("segment_wall_s", 0.0))
    out["prior_wall_s"] = round(sum(segs.values()), 1)
    out["segments"] = sorted(segs) + [seg]
    todo = [j for j in jobs if j not in done]
    with ThreadPoolExecutor(CONCURRENCY) as pool, partial.open("a") as pf:
        for sid, us, rec in pool.map(job, todo):
            r = {"sid": sid, "unit": us, "ok": rec.ok, "parsed": rec.parsed, "call": asdict(rec),
                 "segment": seg, "segment_wall_s": round(time.monotonic() - t_start, 1)}
            pf.write(json.dumps(r, default=str) + "\n")
            pf.flush()
            done[(sid, us)] = r
    for (sid, us), r in sorted(done.items()):
        row = out["states"].setdefault(sid, {"inferred": {}, "calls": {}})
        row["inferred"][us] = dict(r["parsed"], source="inferred") if r["ok"] else None
        row["calls"][us] = r["call"]
    t_ref = time.process_time()
    for st in sts:
        row = out["states"].setdefault(st["state_id"], {"inferred": {}, "calls": {}})
        row["reference"] = {}
        for us in {str(u) for c, uu in st["conds"].items() for u in uu}:
            u = next(u for c, uu in st["conds"].items() for u in uu if str(u) == us)
            row["reference"][us] = reference_note(st["inst"], u)[0]
        row["rendered_sha256"] = {c: sha(rendered(st, c, out)[1]) for c in st["conds"]}
    out["reference_oracle_s"] = round(time.process_time() - t_ref, 2)  # includes rendering; non-deployable oracle CPU
    out["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    out["wall_s"] = round(time.monotonic() - t_start + out["prior_wall_s"], 1)  # summed over segments (restarts)
    DATA.mkdir(parents=True, exist_ok=True)
    NOTES.write_text(json.dumps(out, indent=1, sort_keys=True, default=str))
    proof = {"notes_file_sha256": sha(out["states"]), "freeze_sha256": out["freeze_sha256"], "wall_s": out["wall_s"],
             "coverage": f"{sum(v is not None for r in out['states'].values() for v in r['inferred'].values())}/"
                         f"{sum(len(r['inferred']) for r in out['states'].values())}",
             "states": {s: {"rendered_sha256": r["rendered_sha256"],
                            "inferred_ok": {u: v is not None for u, v in r["inferred"].items()}}
                        for s, r in out["states"].items()}}
    (BLOCK / "stage2-notes-freeze.json").write_text(json.dumps(proof, indent=1, sort_keys=True) + "\n")
    print("notes frozen; coverage", proof["coverage"], "wall_s", out["wall_s"])


def frozen_for(st, cond, notes):
    units = st["conds"][cond]
    src = "inferred" if cond.startswith("inferred") else "reference"
    pay = notes["states"][st["state_id"]][src]
    keep = [u for u in units if pay.get(str(u)) is not None]
    return keep, {str(u): pay[str(u)] for u in keep}


def condition_kwargs(st, cond, notes):
    if cond == "none":
        return {"arm": "direct"}
    keep, frozen = frozen_for(st, cond, notes)
    return {"arm": "fixed", "initial_units": keep, "allocate": False, "frozen_notes": frozen}


def rendered(st, cond, notes):
    inst = st["inst"]
    _, h = t0(inst)
    g = None
    if cond != "none":
        keep, frozen = frozen_for(st, cond, notes)
        g = PerspectiveGraph(recipient=inst.scenario.config.recipient, refutation_mode="fact_only")
        for u in keep:
            g.instantiate(u, frozen[str(u)], frozen[str(u)].get("evidence_ids", []), t=0, cost=0.0)
    user = policy_messages(load_prompts(PACKAGE), inst.scenario.config, inst.scenario.brief, h, g, REV)[0][1]["content"]
    return user, "MIND NOTES" + user.split("MIND NOTES", 1)[1].split("LEGAL ACTIONS NOW", 1)[0].rstrip()


def stage_policy(args):
    fz = verify()
    dirty = [x for x in os.popen(f'git -C "{ROOT}" status --porcelain').read().split("\n") if x.strip()]
    tracked = os.popen(f'git -C "{ROOT}" ls-files reports/repair-block/stage2-notes-freeze.json').read().strip()
    if dirty or not tracked:
        raise SystemExit(f"policy needs a clean tree with the notes-freeze proof committed: dirty={dirty} tracked={tracked!r}")
    notes = json.loads(NOTES.read_text())
    proof = json.loads((BLOCK / "stage2-notes-freeze.json").read_text())
    assert proof["notes_file_sha256"] == sha(notes["states"])
    sts = stage2_states(fz["K"])
    for st in sts:
        for c in st["conds"]:
            user, part = rendered(st, c, notes)
            assert all(m in user for m in MARKERS) and sha(part) == proof["states"][st["state_id"]]["rendered_sha256"][c]
    meta = {"stage": "policy", "freeze_sha256": hashlib.sha256(FREEZE.read_bytes()).hexdigest(),
            "notes_file_sha256": proof["notes_file_sha256"], "decoding": decoding("policy"), "draws": 2,
            "concurrency": CONCURRENCY, "limit_s": 4 * 3600, "package": PACKAGE, "render_revision": REV}
    resume = getattr(args, "resume", None)
    prior_blocks, prior_wall, kept = [], 0.0, []
    if resume:
        out = Path(resume)
        manifest = json.loads((out / "manifest.json").read_text()) if (out / "manifest.json").exists() else \
            json.loads((out / "manifest-start.json").read_text())
        prev = [json.loads(l) for l in (out / "episodes.jsonl").read_text().splitlines() if l.strip()]
        per_block = 2 * sum(len(st["conds"]) for st in sts if st["k"] == 0)
        aborted = []
        for seed in sorted({e["seed"] for e in prev}):
            es = [e for e in prev if e["seed"] == seed]
            if len(es) == per_block:
                prior_blocks.append(seed)
                kept.extend(es)
            else:  # a block cut off by a restart is logged and re-run in full; it never enters the analysis
                aborted.extend(es)
        with (out / "aborted-episodes.jsonl").open("a") as af:
            af.write("".join(json.dumps(e, default=str) + "\n" for e in aborted))
        prior_wall = float(json.loads((out / "progress.json").read_text())["wall_s"]) if (out / "progress.json").exists() else 0.0
        manifest.setdefault("resumes", []).append({"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "kept_blocks": prior_blocks,
                                                   "aborted_episodes": len(prev) - len(kept), "prior_wall_s": prior_wall})
        (out / "episodes.jsonl").write_text("".join(json.dumps(e, default=str) + "\n" for e in kept))
    else:
        manifest = runlog.new_manifest("repair-stage2", meta)
        out = RUNS / manifest["run_id"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "manifest-start.json").write_text(json.dumps(manifest, indent=1, default=str))
    print("run dir", out, flush=True)
    client = LengthGuard(make_client(json.loads(MODEL_CFG.read_text())))
    t_start = time.monotonic() - prior_wall
    budget = 4 * 3600 - float(notes.get("wall_s", 0))
    completed = list(prior_blocks)

    def job(item):
        n, (st, cond, r) = item
        base = {"state_id": st["state_id"], "seed": st["seed"], "condition": cond, "replicate": r, "dispatch_index": n}
        try:
            res = run_episode_arm(client, st["inst"], decoding=decoding("policy"), package=PACKAGE, rev=REV,
                                  **condition_kwargs(st, cond, notes))
        except Exception as e:  # recorded, never silently retried
            return {**base, "blocked": f"error: {type(e).__name__}: {e}"}
        return {**base, "units": [str(u) for u in st["conds"][cond]], **asdict(res)}

    with (out / "episodes.jsonl").open("a") as f, ThreadPoolExecutor(CONCURRENCY) as pool:
        for k in range(fz["K"]):
            if SEED0 + k in completed:
                continue
            if time.monotonic() - t_start + 8 * 60 > budget:
                break  # overrun rule: start a seed block only if a full block (~8 min) still fits in the 4 h limit
            block = [st for st in sts if st["k"] == k]
            jobs = []
            for r in range(2):
                for i, st in enumerate(block):
                    cs = list(st["conds"])
                    for j in range(len(cs)):
                        jobs.append((st, cs[(i + r + j) % len(cs)], r))
            for res in pool.map(job, [(len(completed) * 10000 + n, x) for n, x in enumerate(jobs)]):
                f.write(json.dumps(res, default=str) + "\n")
                f.flush()
            completed.append(SEED0 + k)
            (out / "progress.json").write_text(json.dumps({"completed_seed_blocks": completed,
                                                           "wall_s": round(time.monotonic() - t_start, 1)}))
            print("seed block done", SEED0 + k, round(time.monotonic() - t_start), "s", flush=True)
    runlog.finish(manifest, out, wall_clock_s=time.monotonic() - t_start, completed_seed_blocks=completed)
    print("out", out, "blocks", len(completed))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("qualify", "regress", "freeze", "verify", "notes", "policy"))
    ap.add_argument("--resume", help="policy: an interrupted run dir to continue (complete seed blocks are kept)")
    args = ap.parse_args()
    {"qualify": stage_qualify, "regress": stage_regress, "freeze": stage_freeze, "verify": verify,
     "notes": stage_notes, "policy": stage_policy}[args.stage](args)


if __name__ == "__main__":
    main()
