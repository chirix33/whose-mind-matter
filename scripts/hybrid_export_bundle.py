"""D-020 evidence export from EXISTING hybrid-block artifacts (no model calls, no new runs).

    python3 scripts/hybrid_export_bundle.py RUN_DIR     # writes reports/hybrid-block/audit/{episodes.csv, interventions.csv,
                                                         #   traces/*.json, episodes-agent.jsonl.gz, episodes-privileged.jsonl}

Column convention: fields prefixed `eval_` are EVALUATOR-ONLY (computed by replaying the hidden draw or by the exact
reference); they were never inputs to any deployed condition. All other fields are what the deployed condition saw or did.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from officeminds.world import Action  # noqa: E402
import run_hybrid_fallback as RF  # noqa: E402

OUT = ROOT / "reports" / "hybrid-block" / "audit"


def parse(s):
    m = re.match(r"(\w+)\((\w*)(?:,(\w+))?\)", s)
    return Action(m[1], m[2] or "", m[3] or "")


def klass(con, a):
    return "social_belief" if a.kind == "give" else ("testimony_reliability" if con in ("4b", "4c") else "physical")


def write_csv(path, rows, cols):
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in cols})
    path.write_bytes(buf.getvalue().encode("utf-8"))


def main():
    run = Path(sys.argv[1])
    eps = [json.loads(l) for l in (run / "episodes.jsonl").read_text().splitlines() if l.strip()]
    states = {s["state_id"]: s for s in RF.states()}
    audit = {r["state_id"]: r for r in json.loads((OUT / "input-audit.json").read_text())["t0"]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "traces").mkdir(exist_ok=True)

    # ---------------------------------------------------------------- per-episode table
    rows = []
    for e in eps:
        u = e["usage"]
        r = {k: e[k] for k in ("state_id", "seed", "base", "construction", "stakes", "condition", "draw", "outcome",
                               "n_steps", "n_checks")}
        r["return"] = e["return_"]
        r["wall_clock_s"] = round(e["wall_clock_s"], 4)
        r["checker_cpu_ms"] = round(e["checker_cpu_s"] * 1000, 4)
        for kind in ("decision", "redecision", "check"):
            g = u.get(kind, {})
            for f in ("calls", "attempts", "attempts_failed", "fallbacks", "prompt_tokens", "completion_tokens",
                      "reasoning_tokens"):
                r[f"{kind}_{f}"] = g.get(f, 0)
            r[f"{kind}_reasoning_known"] = g.get("reasoning_known", True)
            r[f"{kind}_latency_s"] = round(g.get("latency_s", 0.0), 4)
        r["processed_tokens"] = sum(g["prompt_tokens"] + g["completion_tokens"] for g in u.values())
        r["vetoes"] = sum(bool(s.get("veto")) for s in e["steps"])
        r["substituted_asks"] = sum("substituted_ask" in s for s in e["steps"])
        r["actions"] = " ".join(e["actions"])
        r["eval_bayes_v_t0"] = audit[e["state_id"]]["v_card_compiled"]
        r["eval_bayes_first_action"] = audit[e["state_id"]]["best_card_compiled"]
        rows.append(r)
    cols = list(rows[0])
    write_csv(OUT / "episodes.csv", rows, cols)

    # ---------------------------------------------------------------- interventions (deployed vs eval_ fields)
    inter = []
    for e in eps:
        if e["condition"] == "direct":
            continue
        inst = states[e["state_id"]]["inst"]
        w = inst.scenario.build(inst.hidden)  # privileged replay: eval_ fields only
        w.reset()
        for log in e["steps"]:
            prop = parse(log["proposal"])
            if log.get("check") or log.get("substituted_ask"):
                c = w.clone()
                o = c.step(prop)
                chk = log.get("check") or {}
                inter.append({"state_id": e["state_id"], "base": e["base"], "construction": e["construction"],
                              "stakes": e["stakes"], "condition": e["condition"], "draw": e["draw"], "t": log["t"],
                              "proposal": log["proposal"], "class": klass(e["construction"], prop),
                              "p": chk.get("p", ""), "J": chk.get("J", ""), "V_alt": chk.get("V_alt", ""),
                              "allow": chk.get("allow", ""), "cache_hit": chk.get("cache_hit", ""),
                              "cap_reached": chk.get("cap_reached", ""), "check_failed": chk.get("failed", ""),
                              "veto": bool(log.get("veto")), "redecision": log.get("redecision") or "",
                              "second_check_allow": (log.get("second_check") or {}).get("allow", ""),
                              "scripted_fallback": log.get("scripted_fallback", ""),
                              "substituted_ask": log.get("substituted_ask", ""), "executed": log["executed"],
                              "episode_outcome": e["outcome"], "episode_return": e["return_"],
                              "eval_proposal_would_have": o.outcome})
            w.step(parse(log["executed"]))
    write_csv(OUT / "interventions.csv", inter, list(inter[0]))

    # ---------------------------------------------------------------- representative traces
    by = {(e["state_id"], e["condition"], e["draw"]): e for e in eps}

    def trace(e, why):
        return {"why_selected": why, "state_id": e["state_id"], "condition": e["condition"], "draw": e["draw"],
                "deployed": {"agent_view": e["agent_view"], "steps": e["steps"], "actions": e["actions"],
                             "outcome": e["outcome"], "return": e["return_"], "usage": e["usage"],
                             "calls": [{"kind": c["kind"], "step": c["step"], "target": c["target"], "ok": c["ok"],
                                        "parsed": c["parsed"],
                                        "final_text": c["attempts"][-1]["text"] if c["attempts"] else None,
                                        "final_reasoning": c["attempts"][-1].get("reasoning") if c["attempts"] else None}
                                       for c in e["calls"]]},
                "evaluator_only": {"hidden": e["privileged"]["hidden"],
                                   "bayes_v_t0": audit[e["state_id"]]["v_card_compiled"],
                                   "bayes_first_action": audit[e["state_id"]]["best_card_compiled"],
                                   "interventions_would_have": [i["eval_proposal_would_have"] for i in inter
                                                                if i["state_id"] == e["state_id"]
                                                                and i["condition"] == e["condition"]
                                                                and i["draw"] == e["draw"]]}}

    picks = {}
    # (1) social discrimination: a base where checker vetoes a would-fail give and succeeds; direct gives wrongly;
    #     generic vetoes a would-succeed give somewhere
    soc = [i for i in inter if i["condition"] == "checker_gate" and i["class"] == "social_belief" and i["veto"]
           and i["eval_proposal_would_have"] == "error" and i["episode_outcome"] == "success"]
    i = sorted(soc, key=lambda x: (x["construction"] != "3b", x["state_id"], x["draw"]))[0]
    picks["1_social_discrimination_checker"] = trace(by[(i["state_id"], "checker_gate", i["draw"])],
                                                     "checker vetoes a handoff that would have failed; episode succeeds")
    d = [e for e in eps if e["state_id"] == i["state_id"] and e["condition"] == "direct" and e["outcome"] == "error"]
    if d:
        picks["1_social_discrimination_direct_same_state"] = trace(d[0], "direct policy on the same state: wrong handoff")
    g = sorted([x for x in inter if x["condition"] == "generic_gate" and x["class"] == "social_belief" and x["veto"]
                and x["eval_proposal_would_have"] == "success"], key=lambda x: (x["state_id"], x["draw"]))
    if g:
        picks["1_social_generic_vetoes_correct_handoff"] = trace(by[(g[0]["state_id"], "generic_gate", g[0]["draw"])],
                                                                 "generic LLM check vetoes a handoff that would have succeeded")
    # (2) correct ex-ante rejection of a lucky action
    lucky = sorted([x for x in inter if x["condition"] == "checker_gate" and x["veto"] and x["class"] == "physical"
                    and x["eval_proposal_would_have"] == "success"], key=lambda x: (x["state_id"], x["draw"]))[0]
    picks["2_ex_ante_rejection_of_lucky_drop"] = trace(by[(lucky["state_id"], "checker_gate", lucky["draw"])],
                                                       f"checker vetoes {lucky['proposal']} (p={lucky['p']}, "
                                                       f"J={lucky['J']} < V_alt={lucky['V_alt']}); the drop would have "
                                                       f"succeeded in this hidden draw")
    # (3) gate-induced timeout
    to = sorted([e for e in eps if e["condition"] == "checker_gate" and e["outcome"] == "timeout"
                 and any(s.get("veto") for s in e["steps"])], key=lambda e: (e["state_id"], e["draw"]))[0]
    picks["3_gate_induced_timeout"] = trace(to, "checker vetoed a commitment; the episode then timed out")
    # (4) missed opportunity: Bayes commits at t0, the policy never proposes a commitment, episode does not succeed early
    mo = sorted([e for e in eps if e["condition"] == "checker_gate"
                 and re.match(r"(give|drop)\(", audit[e["state_id"]]["best_card_compiled"])
                 and not any(re.match(r"(give|drop)\(", s["proposal"]) for s in e["steps"])
                 and e["outcome"] == "timeout"], key=lambda e: (e["state_id"], e["draw"]))
    if mo:
        picks["4_missed_opportunity"] = trace(mo[0], "Bayes first action commits; the policy never proposes a "
                                                     "commitment and times out (a veto gate cannot help)")
    for k, v in picks.items():
        (OUT / "traces" / f"{k}.json").write_bytes(json.dumps(v, indent=1).encode("utf-8"))

    # ---------------------------------------------------------------- raw episodes, split by information class
    agent = [{k: v for k, v in e.items() if k != "privileged"} for e in eps]
    raw = "".join(json.dumps(a, sort_keys=True) + "\n" for a in agent).encode("utf-8")
    (OUT / "episodes-agent.jsonl.gz").write_bytes(gzip.compress(raw, mtime=0))
    (OUT / "episodes-privileged.jsonl").write_bytes("".join(
        json.dumps({"state_id": e["state_id"], "condition": e["condition"], "draw": e["draw"],
                    "hidden": e["privileged"]["hidden"]}) + "\n" for e in eps).encode("utf-8"))
    print(json.dumps({"episodes": len(rows), "interventions": len(inter), "traces": sorted(picks)}, indent=1))


if __name__ == "__main__":
    main()
