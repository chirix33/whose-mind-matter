"""Merge fixed-context runs into one table: model and package effects reported separately.

    python3 scripts/report_unit_contexts.py <run_dir> [<run_dir> ...]

Adds the ORIGINAL pilot-v1 (renderer r2) outputs stored from the full pilot run as their own row (k=0 contexts only).
Those were not re-generated; a fresh pilot-v1 replay at r3 is the corresponding repaired-interface comparison.
Writes reports/pilot/unit-contexts-results.md.
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vomi.fidelity import score_output  # noqa: E402

CATS = ("correct_supported", "correct_unsupported", "incorrect_supported", "unsupported_incorrect", "leakage", "abstained")


def main():
    pub = {json.loads(l)["context_id"]: json.loads(l) for l in (ROOT / "reports/pilot/unit-contexts-v1.jsonl").open()}
    priv = {json.loads(l)["context_id"]: json.loads(l) for l in (ROOT / "data/pilot/unit-contexts-v1-privileged.jsonl").open()}
    rows = []
    run_ids = []
    for d in sys.argv[1:]:
        run_ids.append(Path(d).name)
        rows += [json.loads(l) for l in (Path(d) / "records.jsonl").open()]
    for cid, p in priv.items():  # original stored outputs
        o = p["original_pilot_v1_r2"]
        if o is None:
            continue
        vals = pub[cid]["requests"]["pilot-v1"]["schema"]["properties"]["hypotheses"]["items"]["properties"]["value"]["enum"]
        rows.append({"context_id": cid, "package": "pilot-v1 (original r2 run)", "model": "gpt-oss-20b", "effort": "low",
                     "score": score_output(o["parsed"] if o["ok"] else None, p["truth"], p["posterior"], set(p["robot_known"]), vals),
                     "usage": None, "incomplete_attempts": 0})
    cells = defaultdict(list)
    for r in rows:
        cells[(r["model"], r["effort"], r["package"])].append(r)

    L = ["# Fixed unit-context diagnostic: model × package", "",
         f"Runs: {', '.join(f'`{x}`' for x in run_ids) or '(none)'}. Contexts: `reports/pilot/unit-contexts-v1.md` (24 frozen contexts; "
         "renderer r3 for fresh runs). Scoring v2 (`src/vomi/fidelity.py`): categories over ATTRIBUTED outputs; proper scores "
         "over all valid outputs. Development data; exploratory.", "",
         "| model | effort | package | n | valid | incomplete attempts | abstained | " + " | ".join(CATS[:-1]) +
         " | top-1 | log score (truth) | Brier | CE vs evidence posterior | mean in/out/reasoning tokens |",
         "|---|---|---|---|---|---|---|" + "---|" * (len(CATS) - 1) + "---|---|---|---|---|"]
    for key in sorted(cells):
        rs = cells[key]
        sc = [r["score"] for r in rs if r["score"].get("valid")]
        att = [s for s in sc if not s["abstained"]]
        cat = Counter(s["category"] for s in att)
        u = [r["usage"] for r in rs if r["usage"]]
        tok = (f"{statistics.mean(x['prompt_tokens'] for x in u):.0f}/{statistics.mean(x['completion_tokens'] for x in u):.0f}/"
               + (f"{statistics.mean(x['reasoning_tokens'] for x in u):.0f}" if u and all(x['reasoning_tokens'] is not None for x in u) else "n/a")) if u else "—"
        L.append(f"| {key[0]} | {key[1]} | {key[2]} | {len(rs)} | {len(sc)} | {sum(r['incomplete_attempts'] for r in rs)} | "
                 f"{sum(s['abstained'] for s in sc)} | " + " | ".join(f"{cat[c]}" for c in CATS[:-1]) +
                 f" | {statistics.mean(s['top1_correct'] for s in sc):.2f} | {statistics.mean(s['log_score_truth'] for s in sc):.2f} | "
                 f"{statistics.mean(s['brier_truth'] for s in sc):.2f} | {statistics.mean(s['cross_entropy_posterior'] for s in sc):.2f} | {tok} |"
                 if sc else f"| {key[0]} | {key[1]} | {key[2]} | {len(rs)} | 0 | — | — |" + " — |" * (len(CATS) + 3))
    L += ["", "Categories count attributed (non-abstained) outputs only; `abstained` = pilot-v2 status insufficient_evidence. "
          "Log score uses a 1e-3 floor; lower Brier/CE is better, higher log score is better.", "",
          "## Paired effects on the same contexts (mean difference; positive = better)", "",
          "| comparison | contexts | Δ log score (truth) | Δ CE vs posterior (negated) | Δ unsupported+leakage rate |", "|---|---|---|---|---|"]
    bykey = {k: {r["context_id"]: r["score"] for r in v if r["score"].get("valid")} for k, v in cells.items()}

    def bad(s):
        return (not s["abstained"]) and s["category"] in ("unsupported_incorrect", "leakage", "correct_unsupported")

    keys = sorted(bykey)
    for a in keys:
        for b in keys:
            same_model = a[0] == b[0] and a[1] == b[1] and a[2] != b[2]
            same_pkg = a[2] == b[2] and (a[0], a[1]) != (b[0], b[1])
            if not (same_model or same_pkg) or a >= b:
                continue
            common = sorted(set(bykey[a]) & set(bykey[b]))
            if not common:
                continue
            d_log = statistics.mean(bykey[b][c]["log_score_truth"] - bykey[a][c]["log_score_truth"] for c in common)
            d_ce = statistics.mean(bykey[a][c]["cross_entropy_posterior"] - bykey[b][c]["cross_entropy_posterior"] for c in common)
            d_bad = statistics.mean(bad(bykey[a][c]) - bad(bykey[b][c]) for c in common)
            kind = "package" if same_model else "model"
            L.append(f"| {kind}: {'/'.join(map(str, b))} vs {'/'.join(map(str, a))} | {len(common)} | {d_log:+.2f} | {d_ce:+.2f} | {d_bad:+.2f} |")

    L += ["", "## Per-context outputs (top value / category; abstention shown as ABST)", "",
          "| ctx | unit | k | truth | evidence-posterior top (p) | " + " | ".join("/".join(map(str, k)) for k in keys) + " |",
          "|---|---|---|---|---|" + "---|" * len(keys)]
    for cid in sorted(pub):
        p, c = priv[cid], pub[cid]
        pt = max(p["posterior"], key=p["posterior"].get)
        cells_txt = []
        for k in keys:
            s = bykey[k].get(cid)
            cells_txt.append("—" if s is None else (f"ABST ({s['top']})" if s["abstained"] else f"{s['top']} / {s['category']}"))
        L.append(f"| {cid} | {c['unit']} | {c['k']} | {p['truth']} | {pt} ({p['posterior'][pt]:.2f}) | " + " | ".join(cells_txt) + " |")
    out = ROOT / "reports" / "pilot" / "unit-contexts-results.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
