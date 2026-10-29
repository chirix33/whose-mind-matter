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
from .unit_schema import (unit_output_schema, unit_output_schema_v2, unit_output_schema_v21, unit_output_schema_v22,
                          validate_unit_output, validate_unit_output_v2, validate_unit_output_v21,
                          validate_unit_output_v22)
from .units import KNOWLEDGE, Unit, content, generate_candidates

ROOT = Path(__file__).resolve().parents[2]
PROMPT_VERSION = "pilot-v1"
PROMPT_DIR = ROOT / "prompts" / PROMPT_VERSION
ARMS = ("direct", "dense", "random", "router", "symbolic")
BUDGET = 2
MAX_ATTEMPTS = 3
FALLBACK_ACTION = "wait()"


@dataclass(frozen=True)
class Package:
    """A versioned unit prompt + schema + validator. Policy/router prompts are shared (pilot-v1)."""
    name: str

    @property
    def unit_prompt_dir(self) -> Path:
        return ROOT / "prompts" / self.name

    def schema(self, domain, variable):
        f = {"pilot-v1": unit_output_schema, "pilot-v2": unit_output_schema_v2, "pilot-v2.1": unit_output_schema_v21,
             "pilot-v2.2": unit_output_schema_v22}[self.name]
        return f(domain, variable)

    def validate(self, text, path, variable, domain, ids):
        f = {"pilot-v1": validate_unit_output, "pilot-v2": validate_unit_output_v2,
             "pilot-v2.1": validate_unit_output_v21, "pilot-v2.2": validate_unit_output_v22}[self.name]
        return f(text, path, variable, domain, ids)

    def fields_hint(self, u, about, step) -> str:
        head = f'Respond as JSON with fields: path={json.dumps(list(u.path))}, variable="{u.variable}", about="{about}", as_of_step={step}, '
        if self.name == "pilot-v1":
            return head + 'hypotheses=[{"value","p"}], evidence_ids=[...], unresolved=[...].'
        status = ('"grounded"|"uncertain"|"abstain"' if self.name in ("pilot-v2.1", "pilot-v2.2")
                  else '"attributed"|"insufficient_evidence"')
        return head + (f'status={status}, hypotheses=[{{"value","p","support":[{{"evidence_id","kind","note"}}]}}], '
                       'unresolved=[...].')

    @property
    def min_render_revision(self) -> int:
        if self.name == "pilot-v2.2":
            return 7  # v2.2 cites the PM<n> public-model IDs rendered from r7
        return 4 if self.name == "pilot-v2.1" else 1  # v2.1 cites the numbered r4 rules


PACKAGES = {"pilot-v1": Package("pilot-v1"), "pilot-v2": Package("pilot-v2"), "pilot-v2.1": Package("pilot-v2.1"),
            "pilot-v2.2": Package("pilot-v2.2")}
ABSTAIN_STATUSES = ("insufficient_evidence", "abstain")  # pilot-v2 / pilot-v2.1 full abstention


def load_prompts(package: str = "pilot-v1") -> dict[str, str]:
    shared = {name: (PROMPT_DIR / f"{name}.txt").read_text(encoding="utf-8") for name in ("policy_system", "router_system")}
    return {**shared, "unit_system": (PACKAGES[package].unit_prompt_dir / "unit_system.txt").read_text(encoding="utf-8")}


def prompt_hashes(package: str = "pilot-v1") -> dict[str, str]:
    return {k: hashlib.sha256(v.encode()).hexdigest() for k, v in load_prompts(package).items()}


# ----------------------------------------------------------------------------- rendering (robot-visible only)
PEOPLE_RULES = (  # r3 shared public domain rules (pilot review item C); describes the scripted contract
    "How people come to believe things (applies to everyone): a person believes what they saw happen or were "
    "sincerely told, and keeps that belief until they see or hear otherwise, so a belief can be outdated or false. "
    "When someone answers a question or states a claim, others who hear it learn what was said but do not "
    "automatically believe it. A person with no belief of their own may adopt what someone they trust tells them. "
    "Some people may deliberately mislead, especially when they have a reason to. A person who neither saw nor was "
    "told anything about a fact has no belief about it.")

PEOPLE_RULES_R4 = (  # r4 (autonomous block Round 1): each clause is checked against the simulator in tests/test_r4_rules.py
    "How people come to believe things (the same rules apply to everyone):\n"
    "1. A person believes a fact if they saw it happen or were sincerely told it, and keeps that belief until they see "
    "or are told otherwise, so a belief can be outdated or false. A person with no belief of their own may adopt what "
    "someone tells them; if they think that person is obstructive, they assume the opposite of what was said instead. "
    "When someone says whether a person is cooperative or obstructive, listeners adopt that assessment. A person who "
    "neither saw nor was told anything about a fact has no belief about it.\n"
    "2. At the start of the task the recipient knows where they themselves are. Moving does not update anyone's "
    "beliefs, including the mover's own.\n"
    "3. When someone states a value for a fact in front of others (shown in the history as \"fact = value\", or "
    "\"I don't know.\" in answer to a question), everyone else present then thinks the speaker believes that value "
    "(or has no belief), but does not adopt it.\n"
    "4. Remarks in ordinary sentences (for example about where someone was, what someone saw, or an earlier "
    "conversation) change no one's beliefs: listeners do not form beliefs about the speaker's or anyone else's beliefs "
    "from them. They still tell the robot what the speaker said, which may or may not be accurate.\n"
    "5. Seeing someone, or seeing the same thing as someone, does not tell a person what that other person believes. "
    "People form beliefs about others' beliefs only from statements: a listener thinks a speaker believes what the "
    "speaker stated (rules 1 and 3), and a person who told someone a fact before the task thinks that listener now "
    "believes it. Statements made during the task give the speaker no belief about the listeners.\n"
    "6. Some people may deliberately mislead, especially when they have a reason to.")

PEOPLE_RULES_R5 = (  # r5 (Round 1 plan-gate fixes): every clause holds over ALL positive-prior dev-v2 worlds (tests/test_r4_rules.py)
    "How people come to believe things (the same rules apply to everyone):\n"
    "1. Before the task (none of this appears in the robot's history): a person came to believe a fact if they saw it "
    "happen or were sincerely told it, and keeps that belief until they see or are told otherwise, so a belief can be "
    "outdated or false. A person with no belief of their own may have adopted what someone told them; if they thought "
    "that person was obstructive, they instead assumed the opposite and took the speaker to believe the opposite. When "
    "someone said whether a person is cooperative or obstructive, listeners adopted that assessment. A person who "
    "neither saw nor was told anything about a fact has no belief about it.\n"
    "2. At the start of the task the recipient knows where they themselves are. During the task, moving does not update "
    "anyone's beliefs, including the mover's own.\n"
    "3. During the task, when someone states a value for a fact in front of others (shown in the history as "
    "\"fact = value\", or \"I don't know.\" in answer to a question), everyone else present then thinks the speaker "
    "believes that value (or has no belief), but does not adopt it.\n"
    "4. Remarks in ordinary sentences (for example about where someone was, what someone saw, or an earlier "
    "conversation) change no one's beliefs: listeners do not form beliefs about the speaker's or anyone else's beliefs "
    "from them. They still tell the robot what the speaker said, which may or may not be accurate.\n"
    "5. Seeing someone, or seeing the same thing as someone, does not tell a person what that other person believes. "
    "People form beliefs about others' beliefs only from statements: a listener thinks a speaker believes what the "
    "speaker stated (except in the distrust case of rule 1), and a person who told someone a fact before the task "
    "thinks that listener now believes it; but if they later only mentioned an update in passing, they may still think "
    "the listener holds the earlier value. Statements made during the task give the speaker no belief about the "
    "listeners.\n"
    "6. Some people may deliberately mislead, especially when they have a reason to.")


PEOPLE_RULES_R6 = (  # r6 (dev-v3 block): every clause holds over ALL positive-prior dev-v3 worlds (tests/test_dev_v3.py)
    "How people come to believe things (the same rules apply to everyone):\n"
    "1. A person believes a fact if they saw it or heard it announced (an announcement to everyone present, or a quiet "
    "conversation addressed to them), and keeps that belief until they see or are told otherwise, so a belief can be "
    "outdated or false. A quiet conversation (shown as: X talks quietly to Y) is heard only by Y, the person addressed: "
    "others present see it but do not hear it. A person who neither saw nor was told anything about a fact has no belief about it.\n"
    "2. The recipient knows which office they are in. Nobody else learns that someone moved unless they saw it or were "
    "told. Seeing someone in the lobby, arriving there or leaving it, does not change what anyone believes about which "
    "office that person is in.\n"
    "3. When someone states a value for a fact (shown as: X says: \"fact = value\", including answers to the robot's "
    "questions, where \"I don't know.\" means no belief), everyone else present then thinks the speaker believes that "
    "value (or has no belief), but does not adopt it. A statement gives the speaker no belief about the listeners.\n"
    "4. Ordinary remarks (any other sentence) change no one's beliefs and no one's beliefs about beliefs. They still "
    "tell the robot what was said, which may or may not be accurate.\n"
    "5. Seeing someone, or hearing the same announcement as someone, does not tell a person what that other person "
    "believes. People form beliefs about others' beliefs only from statements and announcements: listeners think the "
    "speaker believes what the speaker stated or announced, and the speaker of an announcement or quiet conversation "
    "thinks the listeners now believe it. Watching a quiet conversation tells a bystander nothing about what the "
    "listener now believes.\n"
    "6. Some people may deliberately mislead; the public model of the task says who may, how likely it is, and how "
    "they answer.")


def numbered_public_model(text: str) -> tuple[str, list[str]]:
    """r7: give every bullet line of the PUBLIC MODEL paragraph a stable visible ID [PM1], [PM2], ... (in order)."""
    out, ids = [], []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("- "):
            ids.append(f"PM{len(ids) + 1}")
            line = line[: len(line) - len(stripped)] + f"- [{ids[-1]}] " + stripped[2:]
        out.append(line)
    return "\n".join(out), ids


def task_card(cfg: WorldConfig, brief: str, rev: int | None = None) -> str:
    rev = RENDER_REVISION if rev is None else rev
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
    if rev >= 6:
        lines.append(PEOPLE_RULES_R6)
        if cfg.public_model:
            lines.append(numbered_public_model(cfg.public_model)[0] if rev >= 7 else cfg.public_model)
    elif rev >= 5:
        lines.append(PEOPLE_RULES_R5)
    elif rev == 4:
        lines.append(PEOPLE_RULES_R4)
    elif rev >= 3:
        lines.append(PEOPLE_RULES)
    return "\n".join(lines)


RENDER_REVISION = 5  # default for NEW runs only; every script records the revision it rendered in its manifest
# r2: utterance IDs t{t}:said{i} (r1 appended ":{speaker}"; the model cited the short form and valid citations
#     were rejected); action/outcome IDs are citable too. Used by the pilot-v1 full run (kept reproducible: rev=2).
# r3 (pilot review A/C/D, shared by ALL arms and packages): public people-rules paragraph in the task card; mind
#     notes show status, per-hypothesis support or cited evidence IDs, and short excerpts of the cited lines;
#     physical refutation marks K(speaker) `fact_refuted` instead of forcing a refresh.
# r4 (autonomous block Round 1, shared by ALL arms and packages): numbered people-rules that state the simulator's
#     belief contract (statements vs. ordinary remarks; beliefs about beliefs only from statements; recipient
#     self-location at the start only). Notes rendering is unchanged from r3.
# r6 (dev-v3 block, D-014): dev-v3 only. Rules restated for the dev-v3 event semantics (announcements and quiet
#     conversations during the visible prologue) plus the task's declared PUBLIC MODEL. Same rule numbering themes.
#     Ledger: dev-v3 prologue notices render as [t0:note<i>] lines with who else was present (only dev-v3 has them).
# r5 (Round 1 plan gate): r4 clauses were tested only on realized draws; over the full prior, rule 5 failed for
#     backstory updates passed on as claims and for distrusting listeners. r5 scopes rule 1 to before the task,
#     rule 2/3 to during it, and qualifies rule 5. Rule numbering is unchanged (pilot-v2.1 cites RULE1..RULE6).


def ledger(hist: VisibleHistory) -> tuple[str, list[str]]:
    """Visible event ledger; every bracketed ID shown is a citable evidence ID."""
    lines, ids = [], []
    for a, o in hist.steps:
        if a is not None:
            ids.append(f"t{o.t}:action")
            lines.append(f"  [t{o.t}:action] robot did {a}")
        for i, (_, _, text, others) in enumerate(o.notices):  # dev-v3 only
            eid = f"t{o.t}:note{i}"
            ids.append(eid)
            lines.append(f"  [{eid}] {text} ({'others present: ' + ', '.join(others) if others else 'nobody else present'})")
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


STATUS_TEXT = {
    "fact_refuted": "the robot later observed that what this person said is not true now; this does NOT show "
                    "the person does not believe it (they may hold a false belief)",
    "stale": "new evidence about this person has appeared since the note was written",
}


def _excerpts(hist: VisibleHistory, ids: list[str], width: int = 110) -> str:
    text, _ = ledger(hist)
    lines = {l.strip().split("]")[0][1:]: l.strip() for l in text.splitlines()[1:] if l.strip().startswith("[")}
    return " ".join(lines[i][:width] for i in ids if i in lines)


def notes_text(graph: PerspectiveGraph | None, hist: VisibleHistory | None = None, rev: int | None = None,
               cfg: WorldConfig | None = None) -> str:
    rev = RENDER_REVISION if rev is None else rev
    if graph is None:
        return "MIND NOTES: (none; this agent does not use separate mind-inference steps)"
    view = graph.policy_view()
    if not view:
        return "MIND NOTES: (none instantiated)"
    if rev >= 7:
        return matched_notes_text(view, cfg)
    lines = []
    for r in view:
        out = r["output"]
        unres = "; ".join(out.get("unresolved", [])) if isinstance(out, dict) else ""
        if rev < 3:  # r2 rendering, exactly as in the pilot-v1 full run
            hyps = ", ".join(f"{h['value']}: {h['p']:.2f}" for h in out.get("hypotheses", [])) if isinstance(out, dict) else ""
            lines.append(f"  {r['unit']} about {out.get('about', '?')} (as of step {r['as_of']}, status {r['status']}): "
                         f"{hyps}" + (f" | unresolved: {unres}" if unres else ""))
            continue
        head = f"  {r['unit']} about {out.get('about', '?')} (as of step {r['as_of']}, note status {r['status']}"
        head += f": {STATUS_TEXT[r['status']]})" if r["status"] in STATUS_TEXT else ")"
        if out.get("status") in ABSTAIN_STATUSES:
            head += " INFERENCE ABSTAINED: the robot's evidence does not settle this person's state"
        elif out.get("status") == "uncertain":
            head += " INFERENCE UNCERTAIN: several of this person's possible states remain plausible"
        hyp_parts = []
        for h in out.get("hypotheses", []):
            sup = h.get("support")
            s = f"{h['value']}: {h['p']:.2f}"
            if sup is not None:
                s += " [" + ("; ".join(f"{x['evidence_id']} {x['kind']}" for x in sup) or "no support given") + "]"
            hyp_parts.append(s)
        ev = out.get("evidence_ids", [])
        line = head + "\n    hypotheses: " + ", ".join(hyp_parts)
        line += "\n    cited evidence: " + (", ".join(ev) or "none")
        if ev and hist is not None:
            line += "\n    excerpts: " + _excerpts(hist, ev)
        if unres:
            line += "\n    unresolved: " + unres
        lines.append(line)
    return "MIND NOTES (from separate inference steps; may be wrong or outdated):\n" + "\n".join(lines)


INTENT_ORDER = ("cooperative", "obstructive", "unknown")


def matched_notes_text(view: list[dict], cfg: WorldConfig) -> str:
    """r7 matched typed-content template (D-015; repair-block plan RC7-RC9). Every note source renders through the same
    canonical fields, built only from the unit definition and the hypothesis distribution:
      - unit label and `about` from the unit definition (describe_unit), never from model output;
      - values in a fixed order (fact-domain order then "unknown"; or cooperative, obstructive, unknown), each value's
        mass summed, rounded to 2 dp, values below 0.005 after rounding omitted;
      - one confidence line derived from the UNROUNDED distribution by one rule (high if one value >= 0.8, else low),
        worded as the robot's confidence in its estimate, never as the belief being true;
      - an abstained inferred output shows its distribution and the abstain banner instead of the confidence line;
      - graph statuses other than fresh (STATUS_TEXT) are shown identically for every source.
    Never shown for any source: citations, excerpts, unresolved items, source labels, model-chosen status, correctness."""
    lines = []
    for r in view:
        out = r["output"]
        u = Unit(tuple(r["unit"][2:-1].split("->")), KNOWLEDGE if r["unit"].startswith("K(") else "reliability")
        _, about = describe_unit(u, cfg)
        order = (list(cfg.fact_domains[cfg.query_facts[0]]) + ["unknown"]) if u.variable == KNOWLEDGE else list(INTENT_ORDER)
        mass: dict[str, float] = {}
        for h in out.get("hypotheses", []):
            mass[h["value"]] = mass.get(h["value"], 0.0) + float(h["p"])
        dist = ", ".join(f"{v}: {mass[v]:.2f}" for v in order if v in mass and round(mass[v], 2) >= 0.005)
        who = u.path[0]
        what = (f"{who}'s belief" if u.variable == KNOWLEDGE and u.depth == 1 else
                f"what {who} thinks {u.path[1]} believes" if u.variable == KNOWLEDGE else
                f"{who}'s intent" if u.depth == 1 else f"{who}'s assessment of {u.path[1]}")
        line = f"  {u} about {about} (as of step {r['as_of']}): {dist}"
        if r.get("status") in STATUS_TEXT:
            line += f"\n    note status: {STATUS_TEXT[r['status']]}"
        if out.get("status") in ABSTAIN_STATUSES:
            line += "\n    INFERENCE ABSTAINED: the robot's evidence does not settle this person's state"
        else:
            high = max(mass.values(), default=0.0) >= 0.8
            line += (f"\n    robot's confidence in this estimate of {what}: "
                     + ("high (one value has probability at least 0.8)" if high else "low (several values remain possible)"))
        lines.append(line)
    return ("MIND NOTES (estimates of people's mental states from separate inference steps; they may be wrong, and a "
            "person's belief can itself be false or outdated):\n" + "\n".join(lines))


def describe_unit(u: Unit, cfg: WorldConfig) -> tuple[str, str]:
    fact = cfg.query_facts[0]
    if u.variable == KNOWLEDGE:
        if u.depth == 1:
            return f"knowledge of {u.path[0]}: what {u.path[0]} believes about {fact}", fact
        return f"knowledge path {u.path[0]} -> {u.path[1]}: what {u.path[0]} believes {u.path[1]} believes about {fact}", fact
    if u.depth == 1:
        return f"reliability of {u.path[0]}: is {u.path[0]} cooperative or obstructive", u.path[0]
    return f"reliability path {u.path[0]} -> {u.path[1]}: how {u.path[0]} assesses {u.path[1]}", u.path[1]


def policy_messages(prompts, cfg, brief, hist, graph, rev: int | None = None) -> tuple[list[dict], list[str]]:
    led, _ = ledger(hist)
    acts = [str(a) for a in legal_actions(cfg, hist.last)]
    user = "\n\n".join([task_card(cfg, brief, rev), led, physical_summary(hist), notes_text(graph, hist, rev, cfg),
                        "LEGAL ACTIONS NOW: " + ", ".join(acts), 'Respond as JSON: {"action": "<one legal action>"}'])
    return [{"role": "system", "content": prompts["policy_system"]}, {"role": "user", "content": user}], acts


def policy_schema(acts):
    return {"type": "object", "properties": {"action": {"type": "string", "enum": acts}},
            "required": ["action"], "additionalProperties": False}


def unit_messages(prompts, cfg, brief, hist, u, package: str = "pilot-v1",
                  rev: int | None = None) -> tuple[list[dict], list[str], set[str]]:
    led, ids = ledger(hist)
    if (rev if rev is not None else RENDER_REVISION) >= 7 and cfg.public_model:
        ids = ids + numbered_public_model(cfg.public_model)[1]  # PM<n> IDs are citable (pilot-v2.2)
    desc, about = describe_unit(u, cfg)
    domain = list(cfg.fact_domains[cfg.query_facts[0]])
    user = "\n\n".join([task_card(cfg, brief, rev), led, physical_summary(hist),
                        f"ASPECT TO INFER: {desc}.", PACKAGES[package].fields_hint(u, about, hist.last.t)])
    return [{"role": "system", "content": prompts["unit_system"]}, {"role": "user", "content": user}], domain, set(ids)


def router_messages(prompts, cfg, brief, hist, graph, cands, remaining, rev: int | None = None):
    led, _ = ledger(hist)
    lines = [f"  {u}: {describe_unit(u, cfg)[0]}" for u in cands]
    user = "\n\n".join([task_card(cfg, brief, rev), led, physical_summary(hist), notes_text(graph, hist, rev, cfg),
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
                    initial_units: list[Unit] | None = None, allocate: bool = True, seed: int = 0,
                    package: str = "pilot-v1", rev: int | None = None, unit_client=None,
                    frozen_notes: dict[str, dict] | None = None) -> EpisodeResult:
    """One controlled episode. `initial_units` + allocate=False gives the fixed-graph continuation used by
    paired interventions (instantiate exactly those units at t0, then no further allocation).
    `unit_client` (default: `client`) produces mental notes; `client` makes routing and policy decisions.
    Mixed clients are a DIAGNOSTIC only (pilot review): main experiments use one backbone for both.
    `frozen_notes` (autonomous block Round 2): unit -> a note payload frozen BEFORE any policy outcome. Those
    initial units are instantiated from the payload with no inference call in this episode (the note's generation
    cost is accounted where it was produced). Requires refutation_mode fact_only (r>=3), under which no note is
    ever forced into a refresh, so frozen notes stay exactly as frozen; any refresh would raise."""
    rev = RENDER_REVISION if rev is None else rev
    unit_client = unit_client or client
    prompts = load_prompts(package)
    pkg = PACKAGES[package]
    sc, cfg = inst.scenario, inst.scenario.config
    world: World = sc.build(inst.hidden)
    hist = VisibleHistory(sc.brief, [(None, world.reset())])
    graph = None if arm == "direct" else PerspectiveGraph(
        recipient=cfg.recipient, refutation_mode="fact_only" if rev >= 3 else "contradict")
    rng = random.Random(f"{seed}:{inst.instance_id}:{arm}")
    used, calls, fidelity, actions = 0, [], [], []
    stopped_router = 0
    start = time.monotonic()

    def infer(u: Unit, kind: str):
        msgs, domain, ids = unit_messages(prompts, cfg, sc.brief, hist, u, package, rev)
        rec = call_with_protocol(unit_client, kind, hist.last.t, str(u), msgs, pkg.schema(domain, u.variable),
                                 lambda t: pkg.validate(t, u.path, u.variable, domain, ids), decoding)
        calls.append(rec)
        truth = content(world, u)  # PRIVILEGED: fidelity scoring only, never shown to the agent
        top = max(rec.parsed["hypotheses"], key=lambda h: h["p"])["value"] if rec.ok else None
        fidelity.append({"unit": str(u), "step": hist.last.t, "kind": kind, "ok": rec.ok, "top": top,
                         "truth": list(truth), "top_matches_truth": rec.ok and top == truth[0],
                         "output": rec.parsed, "history_steps": len(hist.steps)})
        return rec

    if frozen_notes and rev < 3:
        raise ValueError("frozen notes need refutation_mode fact_only (render revision >= 3)")
    for u in initial_units or []:
        if frozen_notes is not None and str(u) in frozen_notes:
            note = frozen_notes[str(u)]
            graph.instantiate(u, note, note.get("evidence_ids", []), t=hist.last.t, cost=0.0)
            truth = content(world, u)  # PRIVILEGED: fidelity scoring only
            top = max(note["hypotheses"], key=lambda h: h["p"])["value"]
            fidelity.append({"unit": str(u), "step": hist.last.t, "kind": "frozen", "ok": True, "top": top,
                             "truth": list(truth), "top_matches_truth": top == truth[0], "output": note,
                             "history_steps": len(hist.steps)})
            continue
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
                    if frozen_notes is not None:
                        raise RuntimeError("a frozen note was contradicted; frozen-note runs must not refresh")
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
                msgs, schema = router_messages(prompts, cfg, sc.brief, hist, graph, cands, BUDGET - used, rev)
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
        msgs, acts = policy_messages(prompts, cfg, sc.brief, hist, graph, rev)
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
