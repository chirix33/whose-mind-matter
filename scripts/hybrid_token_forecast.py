"""Hybrid block (D-019): actual-tokenizer forecast for the fallback prompts (CPU; run with the vLLM venv, offline).

    HF_HUB_OFFLINE=1 ~/venvs/vllm/bin/python scripts/hybrid_token_forecast.py

Tokenizes the rendered t0 prompts (reports/hybrid-block/rendered-t0.json) with the served model's own tokenizer and chat
template, and combines them with MEASURED per-decision usage of the direct policy from the repair-block traces.
"""

import json
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPAIR = Path.home() / "officeminds-runs" / "repair" / "repair-stage2-20261029-132459-743ace" / "episodes.jsonl"


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("openai/gpt-oss-20b")
    rendered = json.loads((ROOT / "reports" / "hybrid-block" / "rendered-t0.json").read_text())
    n = lambda msgs: len(tok(tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False),  # noqa: E731
                             add_special_tokens=False)["input_ids"])
    per = []
    for r in rendered:
        row = {"construction": r["construction"], "decision": n(r["decision"])}
        if "check" in r:
            row["check"] = n(r["check"])
            row["redecision"] = n(r["redecision"])
        per.append(row)
    measured = {"decision_prompt": [], "decision_completion": [], "decisions_per_episode": []}
    for line in REPAIR.read_text().splitlines():
        e = json.loads(line)
        if e.get("condition") != "none":
            continue
        ds = [c for c in e["calls"] if c["kind"] == "decision"]
        measured["decisions_per_episode"].append(len(ds))
        for c in ds:
            for a in c["attempts"]:
                measured["decision_prompt"].append(a["prompt_tokens"])
                measured["decision_completion"].append(a["completion_tokens"])
    m = {k: round(statistics.mean(v), 1) for k, v in measured.items()}
    out = {"tokenizer": "openai/gpt-oss-20b (HF snapshot, chat template)", "t0_rendered": per,
           "measured_direct_none_repair_stage2": m,
           "t0_template_vs_server_note": "server prompt_tokens for the same t0 prompt can differ slightly from the local "
                                         "chat-template count (server-side system/developer header)."}
    (ROOT / "reports" / "hybrid-block" / "token-forecast.json").write_bytes(json.dumps(out, indent=1).encode())
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    main()
