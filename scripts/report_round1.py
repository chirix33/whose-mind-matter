"""Autonomous block Round 1: rescore fixed-context runs with scoring v3 and the pre-registered ambiguity policy.

    python3 scripts/report_round1.py <run_dir> [<run_dir> ...]

Every run is labelled with its render revision (from its manifest; runs without one are r3) and its output cap.
Categories partition n per cell. Primary block = contexts flagged consistent in reports/autonomous-block/reference-audit.json;
ambiguous contexts are reported apart. Writes reports/autonomous-block/round1-results.md and a per-output JSONL
(data/autonomous-block/round1-scored.jsonl; privileged: contains truths).
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vomi.fidelity import CATS_V3, score_output_v3  # noqa: E402

AUDIT = json.loads((ROOT / "reports/autonomous-block/reference-audit.json").read_text())["contexts"]
AMBIG = {c for c, v in AUDIT.items() if v["flag"] == "ambiguous"}
HALLU = ("unsupported_committed", "leakage")


def load(run_dir: Path):
    man = json.loads((run_dir / "manifest.json").read_text())
    cfg = man["config"]
    rev = cfg.get("render_revision") or 3
    cap = cfg["decoding"].get("max_tokens")
    for l in (run_dir / "records.jsonl").open():
        r = json.loads(l)
        r["rev"], r["cap"], r["run_id"] = rev, cap, man["run_id"]
        yield r


def mean(xs):
    xs = list(xs)
    return statistics.mean(xs) if xs else float("nan")


def main():
    ctxs = {json.loads(l)["context_id"]: json.loads(l) for l in (ROOT / "reports/autonomous-block/unit-contexts-v1-r4.jsonl").open()}
    priv = {json.loads(l)["context_id"]: json.loads(l) for l in (ROOT / "data/pilot/unit-contexts-v1-privileged.jsonl").open()}
    rows, runs = [], []
    for d in sys.argv[1:]:
        runs.append(Path(d).name)
        for r in load(Path(d)):
            p, c = priv[r["context_id"]], ctxs[r["context_id"]]
            vals = c["requests"]["pilot-v1"]["schema"]["properties"]["hypotheses"]["items"]["properties"]["value"]["enum"]
            s = score_output_v3(r["call"]["parsed"], p["truth"], p["posterior"], set(p["robot_known"]), vals,
                                r["context_id"] in AMBIG)
            rows.append({"context_id": r["context_id"], "cell": (r["model"], r["effort"], f"r{r['rev']}", r["package"]),
                         "cap": r["cap"], "run_id": r["run_id"], "score": s, "usage": r["usage"],
                         "incomplete": r["incomplete_attempts"], "attempts": len(r["call"]["attempts"])})
    cells = defaultdict(list)
    for r in rows:
        cells[r["cell"]].append(r)
    keys = sorted(cells)
    name = lambda k: "/".join(k)
    L = ["# Round 1 results: fixed contexts under scoring v3", "",
         f"Runs: {', '.join(f'`{x}`' for x in runs)}. Contexts: the 24 of `unit-contexts-v1` "
         "(r4 rows use `reports/autonomous-block/unit-contexts-v1-r4.jsonl`). Development data; exploratory.",
         f"Ambiguity policy: `reports/autonomous-block/reference-audit.json` (written before outputs). Primary block = "
         f"{24 - len(AMBIG)} consistent contexts; ambiguous = {', '.join(sorted(AMBIG))}.",
         "Hallucination-type = unsupported_committed + leakage. r3 rows are earlier runs rescored with v3 (contract r3, "
         "not re-run).", ""]
    for block, members in (("Primary (consistent contexts)", lambda c: c not in AMBIG), ("Ambiguous contexts", lambda c: c in AMBIG)):
        L += [f"## {block}: category counts (each row sums to n)", "",
              "| cell (model/effort/rules/package) | cap | n | " + " | ".join(CATS_V3) + " | hallucination-type |",
              "|---|---|---|" + "---|" * len(CATS_V3) + "---|"]
        for k in keys:
            rs = [r for r in cells[k] if members(r["context_id"])]
            cnt = Counter(r["score"]["category"] for r in rs)
            assert sum(cnt.values()) == len(rs)
            L.append(f"| {name(k)} | {rs[0]['cap'] if rs else ''} | {len(rs)} | " + " | ".join(str(cnt[c]) for c in CATS_V3)
                     + f" | {sum(cnt[c] for c in HALLU)} |")
        L.append("")
    CONTENT = [c for c in CATS_V3 if c not in ("abstained", "invalid")]
    L += ["## Primary contexts: status-agnostic content categories (Opus gate item 3)", "",
          "Every valid output is categorized by its content, whatever its status, so a package cannot hide content "
          "inside abstentions (pilot-v2's insufficient_evidence covers what pilot-v2.1 calls uncertain). Coverage by status "
          "is its own column. Unsupported mass = mean probability on values the reference gives < 0.2 (item 4). "
          "**Limitation:** the committed/hedged line (top p >= 0.5) is crude; unsupported mass complements it.", "",
          "| cell | n | " + " | ".join(CONTENT) + " | invalid | hallucination-type (content) | mean unsupported mass | status-abstained |",
          "|---|---|" + "---|" * len(CONTENT) + "---|---|---|---|"]
    for k in keys:
        rs = [r for r in cells[k] if r["context_id"] not in AMBIG]
        v = [r["score"] for r in rs if r["score"]["valid"]]
        cnt = Counter(x["content_category"] for x in v)
        L.append(f"| {name(k)} | {len(rs)} | " + " | ".join(str(cnt[c]) for c in CONTENT) + f" | {len(rs) - len(v)} | "
                 f"{sum(cnt[c] for c in HALLU)} | {mean(x['unsupported_mass'] for x in v):.2f} | {sum(x['abstained'] for x in v)} |")
    L.append("")
    L += ["## Proper scores and coverage (all 24 contexts)", "",
          "Over all valid outputs (abstentions included through their distributions) and over attributed outputs only. "
          "Log score vs truth (higher better, 1e-3 floor); Brier, CE vs reference posterior and TV vs posterior: lower better.", "",
          "| cell | coverage (attributed/24) | invalid | log score | Brier | CE vs post. | TV vs post. | log score (attributed) | "
          "mean tokens in/out/reasoning | incomplete attempts |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k in keys:
        rs = cells[k]
        v = [r["score"] for r in rs if r["score"]["valid"]]
        att = [s for s in v if not s["abstained"]]
        u = [r["usage"] for r in rs]
        rt = "n/a" if any(x["reasoning_tokens"] is None for x in u) else f"{mean(x['reasoning_tokens'] for x in u):.0f}"
        L.append(f"| {name(k)} | {len(att)}/{len(rs)} | {len(rs) - len(v)} | {mean(s['log_score_truth'] for s in v):.2f} | "
                 f"{mean(s['brier_truth'] for s in v):.2f} | {mean(s['cross_entropy_posterior'] for s in v):.2f} | "
                 f"{mean(s.get('tv_posterior', math.nan) for s in v):.2f} | {mean(s['log_score_truth'] for s in att):.2f} | "
                 f"{mean(x['prompt_tokens'] for x in u):.0f}/{mean(x['completion_tokens'] for x in u):.0f}/{rt} | "
                 f"{sum(r['incomplete'] for r in rs)} |")
    L += ["", "## Proper scores on the 19 consistent contexts only (Opus gate item 5)", "",
          "In the flagged contexts CE/TV mostly measure undisclosed generator base rates, so the primary comparison uses "
          "these rows. Note: uc03, uc20, uc21, uc22 have posterior 1.0 only because people without an incentive never lie "
          "in the generator; CE/TV there penalize hedges that rule 6 invites.", "",
          "| cell | n | log score | Brier | CE vs post. | TV vs post. | mean unsupported mass |", "|---|---|---|---|---|---|---|"]
    for k in keys:
        v = [r["score"] for r in cells[k] if r["context_id"] not in AMBIG and r["score"]["valid"]]
        L.append(f"| {name(k)} | {len(v)} | {mean(s['log_score_truth'] for s in v):.2f} | {mean(s['brier_truth'] for s in v):.2f} | "
                 f"{mean(s['cross_entropy_posterior'] for s in v):.2f} | {mean(s['tv_posterior'] for s in v):.2f} | "
                 f"{mean(s['unsupported_mass'] for s in v):.2f} |")
    by = {k: {r["context_id"]: r["score"] for r in cells[k]} for k in keys}

    def paired(a, b, label):
        common = [c for c in sorted(set(by[a]) & set(by[b])) if by[a][c]["valid"] and by[b][c]["valid"]]
        prim = [c for c in common if c not in AMBIG]
        if not prim:
            return
        dl = mean(by[b][c]["log_score_truth"] - by[a][c]["log_score_truth"] for c in prim)
        dce = mean(by[a][c]["cross_entropy_posterior"] - by[b][c]["cross_entropy_posterior"] for c in prim)
        dtv = mean(by[a][c]["tv_posterior"] - by[b][c]["tv_posterior"] for c in prim)
        dh = sum(by[b][c]["content_category"] in HALLU for c in prim) - sum(by[a][c]["content_category"] in HALLU for c in prim)
        dum = mean(by[b][c]["unsupported_mass"] - by[a][c]["unsupported_mass"] for c in prim)
        dab = sum(by[b][c]["abstained"] for c in common) - sum(by[a][c]["abstained"] for c in common)
        L.append(f"| {label} | {name(b)} vs {name(a)} | {len(prim)} | {dl:+.2f} | {dce:+.2f} | {dtv:+.2f} | {dh:+d} | {dum:+.2f} | {dab:+d} |")

    L += ["", "## Paired comparisons on the same 19 consistent contexts (B vs A)", "",
          "Positive Δ log / Δ CE / Δ TV = B better. Hallucination-type and unsupported mass use the status-agnostic content "
          "category. Δ abstentions counts all 24 contexts.", "",
          "| effect | B vs A | contexts | Δ log score | Δ CE (negated) | Δ TV (negated) | Δ hallucination-type | Δ unsupported mass | Δ abstentions |",
          "|---|---|---|---|---|---|---|---|---|"]
    for a in keys:
        for b in keys:
            if a == b:
                continue
            if a[:3] == b[:3] and a[3] < b[3]:  # same model/effort/rules, different package
                paired(a, b, "package (same rules)")
            if a[0:2] == b[0:2] and a[3] == b[3] and a[2] < b[2]:
                caps = {r["cap"] for r in cells[a]} | {r["cap"] for r in cells[b]}
                label = (f"rules {a[2]} -> {b[2]} + output cap {sorted(caps)} + fresh sampled draw (descriptive only)"
                         if len(caps) > 1 or a[0].startswith("gpt-6") else f"rules {a[2]} -> {b[2]} (same package; combined rules effect)")
                paired(a, b, label)
            if a[1:] == b[1:] and a[0] != b[0] and a[0] < b[0]:
                paired(a, b, "model (same effort/rules/package)")
    L += ["", "## Per-context top value / category", "",
          "| ctx | ref | unit | truth | posterior top (p) | " + " | ".join(name(k) for k in keys) + " |",
          "|---|---|---|---|---|" + "---|" * len(keys)]
    for cid in sorted(ctxs):
        p = priv[cid]
        pt = max(p["posterior"], key=p["posterior"].get)
        cellsx = []
        for k in keys:
            s = by[k].get(cid)
            cellsx.append("—" if s is None else ("INVALID" if not s["valid"] else
                          f"{s['top']} {s['top_p']:.2f} / {s['category']}" + (f" [{s['status']}]" if s.get("status") else "")))
        L.append(f"| {cid} | {'AMB' if cid in AMBIG else 'ok'} | {ctxs[cid]['unit']} | {p['truth']} | {pt} ({p['posterior'][pt]:.2f}) | "
                 + " | ".join(cellsx) + " |")
    out = ROOT / "reports/autonomous-block/round1-results.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    priv_out = ROOT / "data/autonomous-block/round1-scored.jsonl"
    priv_out.parent.mkdir(parents=True, exist_ok=True)
    priv_out.write_text("".join(json.dumps({**r, "cell": list(r["cell"])}, default=str) + "\n" for r in rows))
    print(out)


if __name__ == "__main__":
    main()
