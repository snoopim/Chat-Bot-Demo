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

GOAL:
Make a clear diagram that is not "too simple".
Do NOT collapse everything into 1 node per lane unless the narrative truly has no other systems.

STRUCTURE RULES:
- Exactly 3 swimlanes.
- Target 2–4 nodes in the Systems lane.
- Target 1–3 nodes in People and Partners lanes.
- Total nodes: 5–9 (aim for 6–8).
- Total edges: 5–8.

EDGE RULES:
- Avoid duplicate reverse edges (A->B and B->A).
- Systems should normally act as the hub.

LANE LOGIC:
The 3 lanes represent these conceptual roles:

lane_people   → humans / roles / actors  
lane_systems  → internal company systems  
lane_partners → external vendors / services / third parties  

BUT:

The **lane DISPLAY NAMES must be derived from the narrative**.

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
Edges may cross **at most one lane boundary**.

Allowed
People → Systems  
Systems → Partners  
People → Systems → Partners

NOT allowed
People → Partners directly.

NODE NAMING RULES:
Nodes must be **specific systems or roles**.

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

DATA LABEL RULES:
data_label is OPTIONAL.

If used:
- 1–2 words
- noun
- no commas

Examples:
Signups
Subscribers
Assets
Content
Tickets
Leads
Analytics

EDGE LABEL RULES:
Simple verbs.

Examples:
submit
store
send
sync
publish
track
create
view
update

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
    { "from": "n1", "to": "n2", "label": "submit", "data_label": "Signups" }
  ]
}

Return JSON only.
"""


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

    # Safe JSON parsing
    try:
        return json.loads(text)

    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])

        raise