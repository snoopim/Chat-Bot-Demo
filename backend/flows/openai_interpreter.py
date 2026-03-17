# flows/openai_interpreter.py
import json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

SYSTEM_PROMPT = """
You convert a narrative description into a HIGH-LEVEL data-flow swimlane diagram plan.

IMPORTANT:
You are NOT documenting policy detail.
You are extracting SYSTEM STRUCTURE and KEY DATA FLOWS only.

ZERO HALLUCINATION RULES (CRITICAL):
- ONLY include systems, roles, tools, and services that are EXPLICITLY named in the narrative.
- NEVER invent nodes that are not mentioned. If the narrative says "spreadsheet", use "Spreadsheet" — do NOT add "CRM" or "Database" unless the narrative says so.
- NEVER invent edges/connections not described. Every edge must map to a REAL data flow stated in the text.
- If the narrative mentions only 3 systems, output only 3 system nodes. Do NOT pad with extra nodes.
- When in doubt, LEAVE IT OUT. Fewer accurate nodes are better than more invented ones.
- Re-read the narrative before finalising. Cross-check every node and edge against the text.

GOAL:
Make a clear diagram that is not "too simple".
Do NOT collapse everything into 1 node per lane unless the narrative truly has no other systems.

STRUCTURE RULES:
- Exactly 3 swimlanes.
- Target 2–4 nodes in the Systems lane.
- Target 1–3 nodes in People and Partners lanes.
- Total nodes: 5–9 (aim for 6–8).
- Total edges: 4–6.

EDGE RULES:
- Avoid duplicate reverse edges (A->B and B->A).
- Systems should normally act as the hub.
- Do NOT create a direct edge A->C if an indirect path A->B->C already exists.
  For example, if Admin Staff -> Spreadsheet -> CRM, do NOT also add Admin Staff -> CRM.
- Each (from, to) pair must appear at most once.
- Keep edges SIMPLE. Prefer short, direct connections between adjacent lanes.
- Avoid edges that skip lanes (People → Partners). Route through Systems instead.
- Maximum 6 edges. If the narrative implies more, keep only the most important flows.

LANE LOGIC:
The 3 lanes represent these conceptual roles:

lane_people   → humans / roles / actors
lane_systems  → internal company systems
lane_partners → external vendors / services / third parties

BUT:

The lane DISPLAY NAMES must be derived from the narrative.

Examples:

People lane examples
- Customers
- Marketing Team
- Support Staff
- Website Visitors

Systems lane examples
- Company Platforms
- Internal Systems
- Property Management Systems
- Core Applications

Partners lane examples
- External Vendors
- Payment Providers
- Third Party Services
- Marketing Platforms

Lane names should be:
- 1–3 words
- meaningful for the narrative
- not generic words like "People" or "Systems"

LANE BOUNDARY RULE:
Edges may cross at most one lane boundary.

Allowed
People → Systems
Systems → Partners
People → Systems → Partners

NOT allowed
People → Partners directly.

NODE NAMING RULES:
Nodes must be specific systems or roles.

Bad:
Platform
System
Tool

Good:
Website
CRM
Email Platform
Analytics Tool
Cloud Storage
Ticketing System

EDGE LABEL RULES:
Use SHORT NOUNS, not verbs.

Good examples:
Submission
Transfer
Storage
Synchronization
Export
Import
Migration
Reconciliation
Approval
Access
Reporting
Booking
Payroll
Income
Timesheets
Ledger
Invoices

Bad examples:
submit
store
send
sync
publish
track
create
view
update
record
run
migrate
reconcile

DATA LABEL RULES:
Usually leave data_label EMPTY unless it adds essential meaning.

If used:
- 1 word preferred, max 2 words
- noun only
- no commas
- must add new information beyond edge.label

Good examples:
Payroll
Income
Timesheets
Ledger
Bookings
Invoices
Profiles
Reports

Bad examples:
Data
Information
Records
Items
Stuff

IMPORTANT:
- Prefer putting the main visible meaning in edge.label.
- Do not use verb labels.
- If edge.label already clearly describes the data flow, leave data_label as "".
- Avoid redundant pairs like:
  { "label": "Export", "data_label": "Reports" }
  unless "Reports" is essential and not obvious from the narrative.

DO NOT INCLUDE:
- URLs
- percentages
- legal explanations
- retention commentary
- business commentary

Focus ONLY on:
- where data is stored
- where data moves
- who interacts with systems

ACCURACY CHECK (do this before outputting):
1. For each node: can I point to the exact word/phrase in the narrative? If NO → remove it.
2. For each edge: does the narrative describe this data movement? If NO → remove it.
3. Are there duplicate or near-duplicate nodes? If YES → merge them.

OUTPUT MUST BE VALID JSON ONLY.

JSON SCHEMA:

{
  "title": "...",
  "lanes": [
    { "id": "lane_people", "name": "<people lane name>", "color": "#DFF3E3" },
    { "id": "lane_systems", "name": "<systems lane name>", "color": "#E3F2FD" },
    { "id": "lane_partners", "name": "<partners lane name>", "color": "#FFF3E0" }
  ],
  "nodes": [
    { "id": "n1", "lane": "lane_people", "label": "Marketing Team" }
  ],
  "edges": [
    { "from": "n1", "to": "n2", "label": "Submission", "data_label": "" }
  ]
}

Return JSON only.
"""


def _normalize_edge_labels(plan: Dict[str, Any]) -> Dict[str, Any]:
    verb_to_noun = {
        "submit": "Submission",
        "store": "Storage",
        "send": "Transfer",
        "sync": "Synchronization",
        "publish": "Publication",
        "track": "Tracking",
        "create": "Creation",
        "view": "Access",
        "update": "Update",
        "record": "Record",
        "run": "Execution",
        "export": "Export",
        "import": "Import",
        "migrate": "Migration",
        "reconcile": "Reconciliation",
        "approve": "Approval",
        "review": "Review",
        "validate": "Validation",
        "check": "Check",
    }

    for e in plan.get("edges", []):
        if not isinstance(e, dict):
            continue

        label = str(e.get("label", "")).strip()
        low = label.lower()
        if low in verb_to_noun:
            e["label"] = verb_to_noun[low]

        data_label = str(e.get("data_label", "")).strip()
        if data_label and data_label.lower() == str(e.get("label", "")).strip().lower():
            e["data_label"] = ""

    return plan


def _remove_redundant_edges(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Remove direct A->C edges when an indirect A->B->C path already exists."""
    edges = plan.get("edges") or []
    if not isinstance(edges, list):
        return plan

    # Build adjacency: node -> list of direct targets
    out: Dict[str, set] = {}
    for e in edges:
        if not isinstance(e, dict):
            continue
        src = e.get("from", "")
        tgt = e.get("to", "")
        if src and tgt and src != tgt:
            out.setdefault(src, set()).add(tgt)

    # Find edges that are redundant: A->C exists AND A->B->C exists for some B
    redundant = set()
    for e in edges:
        if not isinstance(e, dict):
            continue
        src = e.get("from", "")
        tgt = e.get("to", "")
        if not src or not tgt or src == tgt:
            continue
        # Check if there's a 2-hop path src -> mid -> tgt
        for mid in out.get(src, set()):
            if mid != tgt and tgt in out.get(mid, set()):
                redundant.add((src, tgt))
                break

    if redundant:
        plan["edges"] = [
            e for e in edges
            if not isinstance(e, dict) or (e.get("from"), e.get("to")) not in redundant
        ]

    return plan


def interpret_diagram_plan_openai(flow_name: str, narrative: str) -> Dict[str, Any]:
    user_prompt = f"""
Flow name: {flow_name}

Narrative:
{narrative}

Return the JSON plan now.
""".strip()

    resp = client.responses.create(
        model="gpt-5.2",
        temperature=0.2,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    text = resp.output_text.strip()

    try:
        plan = json.loads(text)
        return _remove_redundant_edges(_normalize_edge_labels(plan))

    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:
            plan = json.loads(text[start:end + 1])
            return _remove_redundant_edges(_normalize_edge_labels(plan))

        raise