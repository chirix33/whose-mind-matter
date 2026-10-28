"""Freeze the Stage 2 pilot development groups (dev-v1) BEFORE any LLM output is inspected.

Run (CPU only, WSL):
    python scripts/freeze_dev_groups.py

Declared exclusion rules (applied identically to every instance, never by method outcome):
  E1  generator error while building or replaying the instance;
  E2  posterior support at t=0 larger than MAX_SUPPORT worlds (exact symbolic labels too costly);
  E3  the initial observation is already terminal;
  E4  agent view identical to an earlier group's instance in the same family (duplicate).
An excluded instance removes its whole group, so that paired variants stay together.

Outputs:
  data/pilot/dev-v1/public.jsonl        robot-visible material + public metadata (agent view, brief, config)
  data/pilot/dev-v1/privileged.jsonl    hidden params, symbolic reference annotations, generator audit
  data/pilot/dev-v1/interventions.json  prespecified paired-intervention states (by symbolic category)
  reports/pilot/dev-v1-manifest.json    committed manifest: ids, groups, factors, hashes, counts, exclusions
  reports/pilot/dev-v1-freeze.md        human-readable freeze record (rendered from the manifest)
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from officeminds.devgen import BASE_SEED, DEV_VERSION, FACTORS, FAMILIES, KNOBS, generate  # noqa: E402
from officeminds.episode import VisibleHistory  # noqa: E402
from vomi import runlog  # noqa: E402
from vomi.allocation import minimal_sufficient, reference_value  # noqa: E402
from vomi.oracle import GROUNDED_SCALAR, GROUNDED_TYPED, ExactOracle  # noqa: E402
from vomi.theory import generator_audit  # noqa: E402
from vomi.units import generate_candidates  # noqa: E402

MAX_SUPPORT = 64
SETTINGS = ((GROUNDED_TYPED, "face_value"), (GROUNDED_SCALAR, "face_value"), (GROUNDED_SCALAR, "hedged"))
CATEGORY_RECORD = "grounded_typed/face_value"  # symbolic categories for intervention selection
PER_CATEGORY, MAX_INTERVENTIONS = 3, 12
OUT_DATA = ROOT / "data" / "pilot" / DEV_VERSION
OUT_REPORT = ROOT / "reports" / "pilot"


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def annotate(sc, hist, units) -> dict:
    out = {}
    for record, testimony in SETTINGS:
        o = ExactOracle(sc, hist, testimony=testimony)
        values = o.subset_values(units, record=record)
        decs = [o.decompose(u, record=record) for u in units]
        out[f"{record}/{testimony}"] = {
            "j_empty": values[frozenset()],
            "reference_best": reference_value(values),
            "best_minimal_sets": [sorted(map(str, s)) for s in minimal_sufficient(values)],
            "required_depth": o.effective_depth(units, record=record),
            "units": [{k: v for k, v in asdict(d).items() if k not in ("record",)} for d in decs],
        }
    return out


SELECT_ORDER = ("useful_current_action", "zero_value_stop", "negative", "carryover")
# Declared fallback, for the negative category ONLY: the typed record rarely yields negatives, so
# the scalar diagnostic records are searched next, in this fixed order (recorded per state).
NEGATIVE_FALLBACK = ("grounded_typed/face_value", "grounded_scalar/face_value", "grounded_scalar/hedged")


def categories(ann: dict, record: str = CATEGORY_RECORD) -> dict[str, str]:
    """category -> defining unit, under `record`. An instance may fall in several categories.
    mixed = positive delta_J with a current-action flip AND nonzero carryover (not selected)."""
    units = ann[record]["units"]
    out = {}
    carry = [u for u in units if u["carryover"]]
    neg = sorted((u for u in units if u["delta_j"] < -0.01), key=lambda u: u["delta_j"])
    useful = sorted((u for u in units if u["delta_j"] > 0.01 and abs(u["d_memory"]) < 1e-12), key=lambda u: -u["delta_j"])
    mixed = [u for u in units if u["delta_j"] > 0.01 and abs(u["d_memory"]) > 1e-12 and u["p_flip"] > 0]
    if carry:
        out["carryover"] = carry[0]["unit"]
    if neg:
        out["negative"] = neg[0]["unit"]
    if useful:
        out["useful_current_action"] = useful[0]["unit"]
    if mixed:
        out["mixed_flip_and_carryover"] = mixed[0]["unit"]
    if units and all(abs(u["delta_j"]) < 1e-12 for u in units):
        out["zero_value_stop"] = sorted(u["unit"] for u in units)[0]
    return out


def main() -> None:
    cfg = {"version": DEV_VERSION, "seed": BASE_SEED, "families": FAMILIES, "knobs": KNOBS, "max_support": MAX_SUPPORT,
           "settings": [list(s) for s in SETTINGS], "category_record": CATEGORY_RECORD,
           "select_order": SELECT_ORDER, "negative_fallback": NEGATIVE_FALLBACK,
           "per_category": PER_CATEGORY, "max_interventions": MAX_INTERVENTIONS}
    manifest = runlog.new_manifest("pilot-freeze", cfg)
    instances = generate()
    public, privileged, exclusions = [], [], []
    seen_views: dict[str, dict[str, str]] = {f: {} for f in FAMILIES}
    bad_groups = set()
    rows = []
    for inst in instances:
        try:
            w = inst.scenario.build(inst.hidden)
            obs = w.reset()
            hist = VisibleHistory(inst.scenario.brief, [(None, obs)])
            o = ExactOracle(inst.scenario, hist)
            support = len(o.worlds)
        except Exception as e:  # E1
            exclusions.append({"instance": inst.instance_id, "group": inst.group_id, "rule": "E1", "detail": repr(e)})
            bad_groups.add(inst.group_id)
            continue
        view = hist.to_agent_dict()
        vh = sha(view)
        reason = None
        if support > MAX_SUPPORT:
            reason = ("E2", f"posterior support {support} > {MAX_SUPPORT}")
        elif obs.done:
            reason = ("E3", "initial observation terminal")
        else:
            dup = seen_views[inst.family].get(vh)
            if dup and dup != inst.group_id:
                reason = ("E4", f"agent view duplicates group {dup}")
        if reason:
            exclusions.append({"instance": inst.instance_id, "group": inst.group_id, "rule": reason[0], "detail": reason[1]})
            bad_groups.add(inst.group_id)
            continue
        seen_views[inst.family].setdefault(vh, inst.group_id)
        rows.append((inst, w, hist, o, view, vh))

    for inst, w, hist, o, view, vh in rows:
        if inst.group_id in bad_groups:
            continue
        cfgp = inst.scenario.config
        units = generate_candidates(cfgp, hist)
        pub = {"instance_id": inst.instance_id, "group_id": inst.group_id, "family": inst.family,
               "factor": FACTORS[inst.family], "variant": asdict(inst.variant), "brief": inst.scenario.brief,
               "roster": list(cfgp.roster), "offices": list(cfgp.offices), "recipient": cfgp.recipient,
               "query_facts": list(cfgp.query_facts), "handoff": sorted(cfgp.handoff_routes),
               "chute": cfgp.chute_room, "stakes": cfgp.stakes, "horizon": cfgp.horizon,
               "candidates": [str(u) for u in units], "agent_view": view, "agent_view_sha256": vh,
               "public_prior_sha256": sha([list(map(list, p)) + [wt] for p, wt in inst.scenario.prior])}
        priv = {"instance_id": inst.instance_id, "hidden": [list(x) for x in inst.hidden],
                "posterior_support": len(o.worlds), "generator_audit": generator_audit(inst.scenario, o),
                "symbolic": annotate(inst.scenario, hist, units)}
        public.append(pub)
        privileged.append(priv)

    # Prespecified intervention states: deterministic outcome-independent order, symbolic categories.
    order = sorted(privileged, key=lambda p: hashlib.sha256(p["instance_id"].encode()).hexdigest())
    fam = {p["instance_id"]: p["instance_id"].split("-")[2] for p in privileged}
    chosen, taken = [], set()
    for c in SELECT_ORDER:
        records = NEGATIVE_FALLBACK if c == "negative" else (CATEGORY_RECORD,)
        families_used: set[str] = set()
        for record in records:
            for p in order:
                n_c = sum(x["symbolic_category"] == c for x in chosen)
                if n_c >= PER_CATEGORY or len(chosen) >= MAX_INTERVENTIONS:
                    break
                iid = p["instance_id"]
                cats = categories(p["symbolic"], record)
                if c not in cats or iid in taken or fam[iid] in families_used:
                    continue
                taken.add(iid)
                families_used.add(fam[iid])
                chosen.append({"instance_id": iid, "decision_state": "t0", "unit": cats[c], "symbolic_category": c,
                               "category_record": record})

    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, rows_ in (("public.jsonl", public), ("privileged.jsonl", privileged)):
        text = "".join(json.dumps(r, sort_keys=True, default=str) + "\n" for r in rows_)
        (OUT_DATA / name).write_text(text)
        files[name] = hashlib.sha256(text.encode()).hexdigest()
    inter_text = json.dumps(chosen, indent=1, sort_keys=True)
    (OUT_DATA / "interventions.json").write_text(inter_text)
    files["interventions.json"] = hashlib.sha256(inter_text.encode()).hexdigest()

    groups = sorted({p["group_id"] for p in public})
    cats = Counter(c for p in privileged for c in (categories(p["symbolic"]) or {"none": ""}))
    depth = Counter((p["instance_id"].split("-")[2], p["symbolic"][CATEGORY_RECORD]["required_depth"]) for p in privileged)
    summary = {
        "version": DEV_VERSION, "seed": BASE_SEED, "dev_only": True,
        "n_groups": len(groups), "n_instances": len(public),
        "groups_by_family": dict(Counter(g.split("-")[2] for g in groups)),
        "instances_by_family": dict(Counter(p["family"] for p in public)),
        "stakes_instances": dict(Counter(str(p["stakes"]) for p in public)),
        "symbolic_categories": dict(cats),
        "required_depth_by_family": {f"{f}:{d}": n for (f, d), n in sorted(depth.items())},
        "jointly_unsatisfiable_defaults": sum(not p["generator_audit"]["all_defaults_jointly_satisfiable"] for p in privileged),
        "exclusions": exclusions, "excluded_groups": sorted(bad_groups),
        "file_sha256": files, "set_sha256": sha(files),
        "instances": [{k: p[k] for k in ("instance_id", "group_id", "family", "variant", "agent_view_sha256",
                                          "public_prior_sha256", "candidates")} for p in public],
        "interventions": chosen,
        "data_dir": str(OUT_DATA.relative_to(ROOT)),
    }
    (OUT_REPORT / "dev-v1-manifest.json").write_text(json.dumps(summary, indent=1, sort_keys=True))
    path = runlog.finish(manifest, OUT_DATA, summary={k: v for k, v in summary.items() if k not in ("instances",)})
    (OUT_REPORT / "dev-v1-freeze.md").write_text(render(summary, manifest["run_id"], manifest.get("git_commit")), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("n_groups", "n_instances", "groups_by_family", "symbolic_categories",
                                              "excluded_groups", "set_sha256")}, indent=1))
    print(f"manifest: {path}")


def render(s: dict, run_id: str, commit: str | None) -> str:
    L = [f"# Frozen development set `{s['version']}` (Stage 2 pilot)", "",
         f"Frozen by `scripts/freeze_dev_groups.py`, run `{run_id}`, commit `{(commit or 'none')[:7]}`, seed {s['seed']}, "
         "**before any LLM output was produced or inspected.**",
         "**Development data only: never to be used as confirmatory test data.** Set hash (over file hashes): "
         f"`{s['set_sha256']}`.", "",
         f"- Groups: **{s['n_groups']}**; instances: **{s['n_instances']}**; variants stay inside their group and share one hidden world.",
         f"- Groups per family: {s['groups_by_family']}",
         f"- Instances per family: {s['instances_by_family']}",
         f"- Instances by stakes: {s['stakes_instances']}",
         f"- Exclusions (rules E1–E4, see script): {len(s['exclusions'])} instances; excluded groups: {s['excluded_groups'] or 'none'}",
         f"- Instances whose face-value defaults are jointly unsatisfiable at h (D-008 audit; logged, not filtered): {s['jointly_unsatisfiable_defaults']}",
         "", "## Symbolic categories (grounded_typed, face value; privileged evaluator annotations)", "",
         "These categories may not transfer to the LLM; the pilot checks whether they do.", "",
         "| category | instances |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in sorted(s["symbolic_categories"].items())]
    L += ["", "Required depth by family (family:depth → instances):", "", "| family:depth | instances |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in s["required_depth_by_family"].items()]
    L += ["", f"## Prespecified paired-intervention states ({len(s['interventions'])})", "",
          "Selected per category in the order useful, zero/STOP, negative, carryover, walking a fixed sha256 order of instance ids (independent of any LLM outcome); at most "
          "3 per category, one family per category, no instance twice. Negatives fall back to the scalar records in a declared order (column `record`). Counts above are multi-label.", "",
          "| instance | decision state | unit | symbolic category | record |", "|---|---|---|---|---|"]
    L += [f"| {c['instance_id']} | {c['decision_state']} | {c['unit']} | {c['symbolic_category']} | {c['category_record']} |" for c in s["interventions"]]
    L += ["", "## Files", "", f"Data (gitignored, regenerable from code + seed): `{s['data_dir']}/`", "",
          "| file | sha256 |", "|---|---|"]
    L += [f"| {k} | `{v}` |" for k, v in sorted(s["file_sha256"].items())]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
