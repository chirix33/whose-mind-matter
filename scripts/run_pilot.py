"""Run the Stage 2 local LLM pilot on a FROZEN dev set.

    python3 scripts/run_pilot.py --mode integration      # one episode per arm
    python3 scripts/run_pilot.py --mode full             # every instance x every arm + paired interventions

Requires the local server (scripts/serve_local_model.sh). The frozen set is verified against its
committed manifest before any call. Every call is fresh (no response cache). Outputs go to
$OFFICEMINDS_RUNS/pilot/<run_id>/ and an aggregated table to reports/pilot/pilot-<mode>-<run_id>.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds.devgen import generate  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from vomi import runlog  # noqa: E402
from vomi.clients import make_client  # noqa: E402
from vomi.pilot import ARMS, BUDGET, MAX_ATTEMPTS, PROMPT_VERSION, prompt_hashes, run_episode_arm  # noqa: E402
from vomi.units import Unit  # noqa: E402

INTEGRATION_INSTANCE = "false_belief-g0-stakes1-evidence1"  # declared before any LLM output


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def verify_frozen(version: str, instances) -> dict:
    man = json.loads((ROOT / "reports" / "pilot" / f"{version}-manifest.json").read_text())
    want = {i["instance_id"]: i["agent_view_sha256"] for i in man["instances"]}
    for inst in instances:
        w = inst.scenario.build(inst.hidden)
        got = sha(VisibleHistory(inst.scenario.brief, [(None, w.reset())]).to_agent_dict())
        if want.get(inst.instance_id) != got:
            raise SystemExit(f"frozen set mismatch for {inst.instance_id}; refusing to run")
    return man


def parse_unit(s: str) -> Unit:
    var = "knowledge" if s.startswith("K(") else "reliability"
    return Unit(tuple(s[2:-1].split("->")), var)


def gpu() -> list:
    return runlog.gpu_snapshot()


def summarize(results: list[dict]) -> dict:
    by_arm = defaultdict(list)
    for r in results:
        by_arm[r["arm"]].append(r)
    out = {}
    for arm, rs in by_arm.items():
        kinds = sorted({k for r in rs for k in r["usage"]})
        fid = [f for r in rs for f in r["privileged"]["unit_fidelity"]]
        tok = lambda k, f: sum(r["usage"].get(k, {}).get(f, 0) for r in rs) / len(rs)
        out[arm] = {
            "episodes": len(rs),
            "success_rate": sum(r["outcome"] == "success" for r in rs) / len(rs),
            "error_rate": sum(r["outcome"] == "error" for r in rs) / len(rs),
            "timeout_rate": sum(r["outcome"] == "timeout" for r in rs) / len(rs),
            "mean_return": statistics.mean(r["return_"] for r in rs),
            "mean_steps": statistics.mean(r["steps"] for r in rs),
            "mean_wall_clock_s": statistics.mean(r["wall_clock_s"] for r in rs),
            "median_wall_clock_s": statistics.median(r["wall_clock_s"] for r in rs),
            "mean_units_instantiated": statistics.mean(r["privileged"]["units_instantiated"] for r in rs),
            "router_stops": sum(r["privileged"]["router_stops"] for r in rs),
            "unit_calls_ok": sum(f["ok"] for f in fid), "unit_calls": len(fid),
            "unit_top_matches_truth": (sum(f["top_matches_truth"] for f in fid) / len(fid)) if fid else None,
            "per_episode": {k: {"calls": tok(k, "calls"), "prompt_tokens": tok(k, "prompt_tokens"),
                                "completion_tokens": tok(k, "completion_tokens"),
                                "reasoning_tokens": tok(k, "reasoning_tokens"),
                                "reasoning_tokens_known": all(r["usage"].get(k, {}).get("reasoning_tokens_known", True) for r in rs),
                                "latency_s": tok(k, "latency_s")} for k in kinds},
            "failed_attempts": sum(v["attempts_failed"] for r in rs for v in r["usage"].values()),
            "fallbacks": sum(v["fallbacks"] for r in rs for v in r["usage"].values()),
        }
    return out


def by_family(results: list[dict]) -> dict:
    t = defaultdict(lambda: defaultdict(list))
    for r in results:
        t[r["instance_id"].split("-")[2]][r["arm"]].append(r["return_"])
    return {f: {a: statistics.mean(v) for a, v in arms.items()} for f, arms in sorted(t.items())}


def render(mode, run_id, meta, summ, fam, interventions) -> str:
    arms = [a for a in ARMS if a in summ]
    L = [f"# Pilot {mode} results: run `{run_id}`", "",
         f"Frozen set `{meta['version']}` (set hash `{meta['set_sha256'][:16]}…`), commit `{(meta['git_commit'] or '')[:7]}`, "
         f"model `{meta['model']}`, prompts `{PROMPT_VERSION}`, decoding {meta['decoding']}, concurrency {meta['concurrency']}. "
         "Development data: exploratory pilot, not a confirmatory result. Temperature 0 does not guarantee "
         "reproducibility under vLLM batching; serving settings are recorded in the manifest.", "",
         "## Outcomes by arm", "",
         "| arm | episodes | success | error | timeout | mean return | mean steps | units/episode | unit calls ok | unit top = truth | router STOPs | failed attempts | fallbacks |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in arms:
        s = summ[a]
        utt = f"{s['unit_top_matches_truth']:.2f}" if s["unit_top_matches_truth"] is not None else "—"
        L.append(f"| {a} | {s['episodes']} | {s['success_rate']:.2f} | {s['error_rate']:.2f} | {s['timeout_rate']:.2f} | "
                 f"{s['mean_return']:+.3f} | {s['mean_steps']:.2f} | {s['mean_units_instantiated']:.2f} | "
                 f"{s['unit_calls_ok']}/{s['unit_calls']} | {utt} | {s['router_stops']} | {s['failed_attempts']} | {s['fallbacks']} |")
    L += ["", "## Compute per episode (means; API calls include retries)", "",
          "| arm | call kind | calls | prompt tok | completion tok | reasoning tok | summed call latency (s) |", "|---|---|---|---|---|---|---|"]
    for a in arms:
        for k, v in summ[a]["per_episode"].items():
            rt = f"{v['reasoning_tokens']:.0f}" if v["reasoning_tokens_known"] else "not reported"
            L.append(f"| {a} | {k} | {v['calls']:.2f} | {v['prompt_tokens']:.0f} | {v['completion_tokens']:.0f} | {rt} | {v['latency_s']:.2f} |")
    L += ["", "| arm | mean episode wall clock (s, monotonic) | median |", "|---|---|---|"]
    L += [f"| {a} | {summ[a]['mean_wall_clock_s']:.2f} | {summ[a]['median_wall_clock_s']:.2f} |" for a in arms]
    L += ["", "Episode wall clock is measured per episode while other episodes ran concurrently (contention included); "
          "summed call latency is NOT elapsed time.", "", "## Mean return by family and arm", "",
          "| family | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for f, v in fam.items():
        L.append(f"| {f} | " + " | ".join(f"{v[a]:+.3f}" if a in v else "—" for a in arms) + " |")
    if interventions:
        L += ["", "## Paired unit interventions (controlled rollouts; one realized world each, so differences are samples)", "",
              "| instance | unit | symbolic category (record) | symbolic delta_J | t0 action without → with | return without | return with | difference | LLM unit top / truth |",
              "|---|---|---|---|---|---|---|---|---|"]
        for iv in interventions:
            L.append(f"| {iv['instance_id']} | {iv['unit']} | {iv['symbolic_category']} ({iv['category_record']}) | "
                     f"{iv['symbolic_delta_j']:+.4f} | {iv['a0_without']} → {iv['a0_with']} | {iv['return_without']:+.2f} | "
                     f"{iv['return_with']:+.2f} | {iv['return_with'] - iv['return_without']:+.2f} | {iv['unit_top']} / {iv['unit_truth']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("integration", "full"), required=True)
    ap.add_argument("--version", default="dev-v2")
    ap.add_argument("--config", default=str(ROOT / "configs" / "models" / "local_gpt_oss_20b.json"))
    ap.add_argument("--concurrency", type=int, default=8)
    args = ap.parse_args()

    instances = generate(version=args.version)
    man = verify_frozen(args.version, instances)
    data = ROOT / "data" / "pilot" / args.version
    priv = {json.loads(l)["instance_id"]: json.loads(l) for l in (data / "privileged.jsonl").open()}
    interventions_spec = json.loads((data / "interventions.json").read_text())
    cfg = json.loads(Path(args.config).read_text())
    client = make_client(cfg)
    decoding = cfg["decoding"]
    meta = {"version": args.version, "set_sha256": man["set_sha256"], "model": cfg["model"], "decoding": decoding,
            "concurrency": args.concurrency if args.mode == "full" else 1, "budget": BUDGET, "max_attempts": MAX_ATTEMPTS,
            "prompt_version": PROMPT_VERSION, "prompt_sha256": prompt_hashes(), "served_models": client.list_models(),
            "serve": cfg.get("serve"), "response_cache": "none (every call fresh)"}
    manifest = runlog.new_manifest(f"pilot-{args.mode}", meta)
    meta["git_commit"] = manifest["git_commit"]
    out = Path(os.environ.get("OFFICEMINDS_RUNS", Path.home() / "officeminds-runs")) / "pilot" / manifest["run_id"]
    out.mkdir(parents=True, exist_ok=True)

    def ref_set(iid):
        sets = priv[iid]["symbolic"]["grounded_typed/face_value"]["best_minimal_sets"]
        return sets[0] if sets else []

    if args.mode == "integration":
        target = next(i for i in instances if i.instance_id.endswith(INTEGRATION_INSTANCE))
        jobs = [(target, arm) for arm in ARMS]
    else:
        jobs = [(inst, arm) for inst in instances for arm in ARMS]

    gpu_before = gpu()
    t0 = time.monotonic()
    results = []
    with (out / "episodes.jsonl").open("w") as f, ThreadPoolExecutor(meta["concurrency"]) as pool:
        futs = [pool.submit(run_episode_arm, client, inst, arm, decoding, ref_set(inst.instance_id)) for inst, arm in jobs]
        for fut in futs:
            r = asdict(fut.result())
            results.append(r)
            f.write(json.dumps(r, default=str) + "\n")
            f.flush()
    episodes_wall = time.monotonic() - t0

    ivs = []
    if args.mode == "full":
        by_id = {i.instance_id: i for i in instances}
        with (out / "interventions.jsonl").open("w") as f:
            for spec in interventions_spec:
                inst, u = by_id[spec["instance_id"]], parse_unit(spec["unit"])
                without = asdict(run_episode_arm(client, inst, "fixed", decoding, initial_units=[], allocate=False))
                with_ = asdict(run_episode_arm(client, inst, "fixed", decoding, initial_units=[u], allocate=False))
                sym = next(x for x in priv[inst.instance_id]["symbolic"][spec["category_record"]]["units"] if x["unit"] == spec["unit"])
                fid = with_["privileged"]["unit_fidelity"][0] if with_["privileged"]["unit_fidelity"] else {}
                iv = {**spec, "symbolic_delta_j": sym["delta_j"], "a0_without": without["actions"][0], "a0_with": with_["actions"][0],
                      "return_without": without["return_"], "return_with": with_["return_"],
                      "unit_top": fid.get("top"), "unit_truth": (fid.get("truth") or [None])[0],
                      "without": without, "with": with_}
                ivs.append(iv)
                f.write(json.dumps(iv, default=str) + "\n")
    total_wall = time.monotonic() - t0
    gpu_after = gpu()

    summ, fam = summarize(results), by_family(results)
    (out / "summary.json").write_text(json.dumps({"by_arm": summ, "by_family": fam}, indent=1))
    runlog.finish(manifest, out, episodes=len(results), interventions=len(ivs), episodes_wall_clock_s=episodes_wall,
                  total_wall_clock_s=total_wall, gpu_before=gpu_before, gpu_after=gpu_after,
                  note_gpu="nvidia-smi memory.used is the vLLM reservation (gpu-memory-utilization), not an activation peak")
    report = ROOT / "reports" / "pilot" / f"pilot-{args.mode}-{manifest['run_id']}.md"
    report.write_text(render(args.mode, manifest["run_id"], meta, summ, fam,
                             [{k: v for k, v in iv.items() if k not in ("without", "with")} for iv in ivs]), encoding="utf-8")
    print(json.dumps({a: {k: summ[a][k] for k in ("episodes", "success_rate", "mean_return", "mean_units_instantiated",
                                                   "unit_top_matches_truth", "fallbacks")} for a in summ}, indent=1))
    print(f"episodes wall {episodes_wall:.1f}s, total {total_wall:.1f}s; out: {out}; report: {report}")


if __name__ == "__main__":
    main()
