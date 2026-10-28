"""Stage 2 local LLM pilot: rendering, typed-unit / router / policy calls, five arms, accounting.

Arms (Stage 1 review, pilot item 4). All explicit arms share the unit schema, instantiation
backend, deterministic physical summary, graph protocol and policy prompt; only allocation differs.
  direct     full-history policy, no explicit units (may reason implicitly about minds)
  dense      every eligible candidate unit is instantiated
  random     a fixed per-episode budget of BUDGET units, chosen uniformly (seeded per instance)
  router     one prompted router call per step (select up to the remaining budget, or STOP)
  symbolic   reference allocation at t0 = first best minimal set of the privileged grounded_typed
             annotation; content is still LLM-inferred (never true private content). This is a
             reference-selected allocation, NOT an oracle-optimal LLM allocation.

Declared failure protocol: every call gets up to MAX_ATTEMPTS attempts; each attempt and its errors
are logged. After that: a unit abstains (recorded, not shown as a note), the router STOPs, and the
policy falls back to `wait()` (flagged). Nothing is dropped silently.

Graph protocol: instantiated units are retained; `advance` marks stale/contradicted from visible
evidence; a contradicted unit is refreshed by a counted unit call (kind "refresh").
"""

from __future__ import annotations

import hashlib
import json
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from officeminds.episode import VisibleHistory
from officeminds.world import World, WorldConfig, legal_actions

from .clients import ChatClient, ChatResult
from .graph import PerspectiveGraph
from .unit_schema import unit_output_schema, validate_unit_output
from .units import KNOWLEDGE, Unit, content, generate_candidates

ROOT = Path(__file__).resolve().parents[2]
PROMPT_VERSION = "pilot-v1"
PROMPT_DIR = ROOT / "prompts" / PROMPT_VERSION
ARMS = ("direct", "dense", "random", "router", "symbolic")
BUDGET = 2
MAX_ATTEMPTS = 3
FALLBACK_ACTION = "wait()"


def load_prompts() -> dict[str, str]:
    return {name: (PROMPT_DIR / f"{name}.txt").read_text(encoding="utf-8")
            for name in ("policy_system", "unit_system", "router_system")}


def prompt_hashes() -> dict[str, str]:
    return {k: hashlib.sha256(v.encode()).hexdigest() for k, v in load_prompts().items()}


# ----------------------------------------------------------------------------- rendering (robot-visible only)
def task_card(cfg: WorldConfig, brief: str) -> str:
    err = 0.5 * cfg.stakes
    lines = [
        f"TASK: {brief}",
        f"Recipient: {cfg.recipient}. People the robot knows of: {', '.join(cfg.roster)}.",
        "Layout (room: adjacent rooms): " + "; ".join(f"{r}: {', '.join(n)}" for r, n in cfg.adjacency.items()),
        "The robot only sees who is in a room by being in that room.",
        "Actions: move(room) to an adjacent room; ask(person,fact) a person in the same room; "
        "deliver() hands the package to the recipient if the recipient is in the robot's room"
        + (f"; drop(room) sends the package through the chute in the {cfg.chute_room} to that room" if cfg.chute_room else "")
        + (f"; give(person) hands the package to {', '.join(sorted(cfg.handoff_routes))}, who forwards it to where they think it should go"
           if cfg.handoff_routes else "")
        + "; wait().",
        f"Rewards: +1 for a successful delivery; -0.05 for every step taken; a delivery to the wrong place "
        f"(wrong chute drop or wrongly forwarded package) costs -{err:g} and ends the task. "
        f"The task ends after {cfg.horizon} steps without further penalty.",
        f"Facts that can be asked about: {', '.join(cfg.query_facts)} (possible values: "
        + "; ".join(f"{f}: {', '.join(cfg.fact_domains[f])}" for f in cfg.query_facts) + ").",
    ]
    return "\n".join(lines)


RENDER_REVISION = 2  # r2: utterance IDs t{t}:said{i} (r1 appended ":{speaker}"; the model cited the short
#                      form and valid citations were rejected); action/outcome IDs are citable too.


def ledger(hist: VisibleHistory) -> tuple[str, list[str]]:
    """Visible event ledger; every bracketed ID shown is a citable evidence ID."""
    lines, ids = [], []
    for a, o in hist.steps:
        if a is not None:
            ids.append(f"t{o.t}:action")
            lines.append(f"  [t{o.t}:action] robot did {a}")
        for p in o.people_present:
            eid = f"t{o.t}:seen:{p}"
            ids.append(eid)
            lines.append(f"  [{eid}] {p} is in the {o.room} with the robot")
        for i, (speaker, text) in enumerate(o.utterances):
            eid = f"t{o.t}:said{i}"
            ids.append(eid)
            lines.append(f"  [{eid}] {speaker} says: \"{text}\"")
        if o.outcome:
            ids.append(f"t{o.t}:outcome")
            lines.append(f"  [t{o.t}:outcome] {o.outcome}")
    return "HISTORY (robot's own observations):\n" + "\n".join(lines or ["  (nothing yet)"]), ids


def physical_summary(hist: VisibleHistory, holding: bool = True) -> str:
    """Deterministic depth-0 physical update (no LLM call)."""
    o = hist.last
    seen: dict[str, set] = {}
    for _, ob in hist.steps:
        seen.setdefault(ob.room, set()).update(ob.people_present)
    visited = "; ".join(f"{r}: {', '.join(sorted(p)) or 'nobody'}" for r, p in seen.items())
    return (f"PHYSICAL SUMMARY: step {o.t}; robot is in the {o.room}; present: {', '.join(o.people_present) or 'nobody'}; "
            f"holding the package: {'yes' if holding else 'no'}; rooms visited and who was seen there: {visited}.")


def notes_text(graph: PerspectiveGraph | None) -> str:
    if graph is None:
        return "MIND NOTES: (none; this agent does not use separate mind-inference steps)"
    view = graph.policy_view()
    if not view:
        return "MIND NOTES: (none instantiated)"
    lines = []
    for r in view:
        out = r["output"]
        hyps = ", ".join(f"{h['value']}: {h['p']:.2f}" for h in out.get("hypotheses", [])) if isinstance(out, dict) else ""
        unres = "; ".join(out.get("unresolved", [])) if isinstance(out, dict) else ""
        lines.append(f"  {r['unit']} about {out.get('about', '?')} (as of step {r['as_of']}, status {r['status']}): "
                     f"{hyps}" + (f" | unresolved: {unres}" if unres else ""))
    return "MIND NOTES (from separate inference steps; may be wrong or outdated):\n" + "\n".join(lines)


def describe_unit(u: Unit, cfg: WorldConfig) -> tuple[str, str]:
    fact = cfg.query_facts[0]
    if u.variable == KNOWLEDGE:
        if u.depth == 1:
            return f"knowledge of {u.path[0]}: what {u.path[0]} believes about {fact}", fact
        return f"knowledge path {u.path[0]} -> {u.path[1]}: what {u.path[0]} believes {u.path[1]} believes about {fact}", fact
    if u.depth == 1:
        return f"reliability of {u.path[0]}: is {u.path[0]} cooperative or obstructive", u.path[0]
    return f"reliability path {u.path[0]} -> {u.path[1]}: how {u.path[0]} assesses {u.path[1]}", u.path[1]


def policy_messages(prompts, cfg, brief, hist, graph) -> tuple[list[dict], list[str]]:
    led, _ = ledger(hist)
    acts = [str(a) for a in legal_actions(cfg, hist.last)]
    user = "\n\n".join([task_card(cfg, brief), led, physical_summary(hist), notes_text(graph),
                        "LEGAL ACTIONS NOW: " + ", ".join(acts), 'Respond as JSON: {"action": "<one legal action>"}'])
    return [{"role": "system", "content": prompts["policy_system"]}, {"role": "user", "content": user}], acts


def policy_schema(acts):
    return {"type": "object", "properties": {"action": {"type": "string", "enum": acts}},
            "required": ["action"], "additionalProperties": False}


def unit_messages(prompts, cfg, brief, hist, u) -> tuple[list[dict], list[str], set[str]]:
    led, ids = ledger(hist)
    desc, about = describe_unit(u, cfg)
    domain = list(cfg.fact_domains[cfg.query_facts[0]])
    user = "\n\n".join([task_card(cfg, brief), led, physical_summary(hist),
                        f"ASPECT TO INFER: {desc}.",
                        f'Respond as JSON with fields: path={json.dumps(list(u.path))}, variable="{u.variable}", '
                        f'about="{about}", as_of_step={hist.last.t}, hypotheses=[{{"value","p"}}], evidence_ids=[...], unresolved=[...].'])
    return [{"role": "system", "content": prompts["unit_system"]}, {"role": "user", "content": user}], domain, set(ids)


def router_messages(prompts, cfg, brief, hist, graph, cands, remaining):
    led, _ = ledger(hist)
    lines = [f"  {u}: {describe_unit(u, cfg)[0]}" for u in cands]
    user = "\n\n".join([task_card(cfg, brief), led, physical_summary(hist), notes_text(graph),
                        "CANDIDATE ASPECTS (not yet inferred):\n" + "\n".join(lines),
                        f"REMAINING BUDGET: {remaining} inference call(s).",
                        'Respond as JSON: {"select": [<candidate ids>], "stop": <true if you select none>}'])
    schema = {"type": "object", "properties": {
        "select": {"type": "array", "items": {"type": "string", "enum": [str(u) for u in cands]}, "maxItems": remaining},
        "stop": {"type": "boolean"}}, "required": ["select", "stop"], "additionalProperties": False}
    return [{"role": "system", "content": prompts["router_system"]}, {"role": "user", "content": user}], schema


# ----------------------------------------------------------------------------- calls with the failure protocol
@dataclass
class CallRecord:
    kind: str  # decision | unit | refresh | router
    step: int
    target: str
    attempts: list[dict] = field(default_factory=list)
    ok: bool = False
    fallback: str | None = None
    parsed: dict | None = None

    def usage(self) -> dict:
        tok = lambda k: sum(a[k] for a in self.attempts if a.get(k) is not None)
        known = lambda k: all(a.get(k) is not None for a in self.attempts)
        return {"calls": len(self.attempts), "prompt_tokens": tok("prompt_tokens"),
                "completion_tokens": tok("completion_tokens"),
                "reasoning_tokens": tok("reasoning_tokens") if known("reasoning_tokens") else None,
                "latency_s": sum(a["latency_s"] for a in self.attempts)}


def _attempt_dict(r: ChatResult, errors) -> dict:
    return {"text": r.text, "reasoning": r.reasoning, "finish_reason": r.finish_reason, "prompt_tokens": r.prompt_tokens,
            "completion_tokens": r.completion_tokens, "reasoning_tokens": r.reasoning_tokens, "latency_s": r.latency_s,
            "error": r.error, "validation_errors": errors}


def call_with_protocol(client: ChatClient, kind, step, target, messages, schema, validate, decoding) -> CallRecord:
    rec = CallRecord(kind, step, target)
    params = dict(decoding)
    params["response_format"] = {"type": "json_schema", "json_schema": {"name": kind, "schema": schema}}
    for _ in range(MAX_ATTEMPTS):
        r = client.chat(messages, **params)
        parsed, errors = (None, ["request_error"]) if r.error else validate(r.text)
        rec.attempts.append(_attempt_dict(r, errors))
        if parsed is not None:
            rec.ok, rec.parsed = True, parsed
            break
    return rec


def _json_validate(keys):
    def v(text):
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            return None, ["not_json"]
        if not isinstance(obj, dict) or any(k not in obj for k in keys):
            return None, ["schema_violation"]
        return obj, []
    return v


# ----------------------------------------------------------------------------- episodes
@dataclass
class EpisodeResult:
    instance_id: str
    arm: str
    actions: list[str]
    return_: float
    outcome: str
    steps: int
    wall_clock_s: float
    calls: list[dict]
    graph_final: list[dict]
    agent_view: dict
    privileged: dict  # unit fidelity vs true content, hidden params (evaluation only)
    usage: dict


def run_episode_arm(client, inst, arm: str, decoding: dict, reference_set: list[str] | None = None,
                    initial_units: list[Unit] | None = None, allocate: bool = True, seed: int = 0) -> EpisodeResult:
    """One controlled episode. `initial_units` + allocate=False gives the fixed-graph continuation used by
    paired interventions (instantiate exactly those units at t0, then no further allocation)."""
    prompts = load_prompts()
    sc, cfg = inst.scenario, inst.scenario.config
    world: World = sc.build(inst.hidden)
    hist = VisibleHistory(sc.brief, [(None, world.reset())])
    graph = None if arm == "direct" else PerspectiveGraph(recipient=cfg.recipient)
    rng = random.Random(f"{seed}:{inst.instance_id}:{arm}")
    used, calls, fidelity, actions = 0, [], [], []
    stopped_router = 0
    start = time.monotonic()

    def infer(u: Unit, kind: str):
        msgs, domain, ids = unit_messages(prompts, cfg, sc.brief, hist, u)
        rec = call_with_protocol(client, kind, hist.last.t, str(u), msgs, unit_output_schema(domain, u.variable),
                                 lambda t: validate_unit_output(t, u.path, u.variable, domain, ids), decoding)
        calls.append(rec)
        truth = content(world, u)  # PRIVILEGED: fidelity scoring only, never shown to the agent
        top = max(rec.parsed["hypotheses"], key=lambda h: h["p"])["value"] if rec.ok else None
        fidelity.append({"unit": str(u), "step": hist.last.t, "kind": kind, "ok": rec.ok, "top": top,
                         "truth": list(truth), "top_matches_truth": rec.ok and top == truth[0]})
        return rec

    for u in initial_units or []:
        rec = infer(u, "unit")
        if rec.ok:
            graph.instantiate(u, rec.parsed, rec.parsed.get("evidence_ids", []), t=hist.last.t)
        used += 1

    while not hist.last.done:
        t = hist.last.t
        if graph is not None:
            if t > 0:
                graph.advance(hist)
            for name, r in list(graph.units.items()):
                if r.status == "contradicted":
                    u = Unit(tuple(r.path), r.variable)
                    rec = infer(u, "refresh")
                    if rec.ok:
                        graph.refresh(u, rec.parsed, rec.parsed.get("evidence_ids", []), t=t)
                    else:
                        graph.abstain(u)
        if allocate and graph is not None:
            cands = [u for u in generate_candidates(cfg, hist) if str(u) not in graph.units]
            chosen: list[Unit] = []
            if arm == "dense":
                chosen = cands
            elif arm == "random" and used < BUDGET and cands:
                chosen = rng.sample(cands, min(BUDGET - used, len(cands)))
            elif arm == "router" and used < BUDGET and cands:
                msgs, schema = router_messages(prompts, cfg, sc.brief, hist, graph, cands, BUDGET - used)
                rec = call_with_protocol(client, "router", t, "route", msgs, schema, _json_validate(("select", "stop")), decoding)
                calls.append(rec)
                if rec.ok:
                    names = {str(u): u for u in cands}
                    chosen = [names[s] for s in rec.parsed["select"] if s in names][: BUDGET - used]
                    stopped_router += int(not chosen)
                else:
                    rec.fallback = "stop"
                    stopped_router += 1
            elif arm == "symbolic" and t == 0 and reference_set:
                chosen = [u for u in cands if str(u) in set(reference_set)]
            for u in chosen:
                rec = infer(u, "unit")
                if rec.ok:
                    graph.instantiate(u, rec.parsed, rec.parsed.get("evidence_ids", []), t=t)
                used += 1
        msgs, acts = policy_messages(prompts, cfg, sc.brief, hist, graph)
        rec = call_with_protocol(client, "decision", t, "policy", msgs, policy_schema(acts),
                                 lambda txt, acts=acts: (lambda o, e: (o, e) if o is None or o["action"] in acts
                                                         else (None, ["illegal_action"]))(*_json_validate(("action",))(txt)),
                                 decoding)
        calls.append(rec)
        action_str = rec.parsed["action"] if rec.ok else FALLBACK_ACTION
        if not rec.ok:
            rec.fallback = FALLBACK_ACTION
        action = next(a for a in legal_actions(cfg, hist.last) if str(a) == action_str)
        hist.steps.append((action, world.step(action)))
        actions.append(action_str)

    wall = time.monotonic() - start
    usage = {}
    for rec in calls:
        u = rec.usage()
        agg = usage.setdefault(rec.kind, {"calls": 0, "attempts_failed": 0, "fallbacks": 0, "prompt_tokens": 0,
                                          "completion_tokens": 0, "reasoning_tokens": 0, "reasoning_tokens_known": True,
                                          "latency_s": 0.0})
        agg["calls"] += u["calls"]
        agg["attempts_failed"] += sum(bool(a["validation_errors"]) for a in rec.attempts)
        agg["fallbacks"] += int(not rec.ok)
        agg["prompt_tokens"] += u["prompt_tokens"]
        agg["completion_tokens"] += u["completion_tokens"]
        if u["reasoning_tokens"] is None:
            agg["reasoning_tokens_known"] = False
        else:
            agg["reasoning_tokens"] += u["reasoning_tokens"]
        agg["latency_s"] += u["latency_s"]
    total_return = sum(o.reward for _, o in hist.steps)
    return EpisodeResult(
        inst.instance_id, arm, actions, total_return, hist.last.outcome, len(actions), wall,
        [asdict(c) for c in calls], graph.policy_view() if graph else [], hist.to_agent_dict(),
        {"hidden": [list(x) for x in inst.hidden], "unit_fidelity": fidelity, "router_stops": stopped_router,
         "units_instantiated": used},
        usage)
