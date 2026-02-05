# flows/openai_interpreter.py
import json
from typing import Dict, Any
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You convert a narrative data-flow description into a swimlane flow diagram plan.

Rules:
- Output MUST be valid JSON only (no markdown).
- Use 4-7 steps maximum.
- Node labels must be SHORT (<= 5 words if possible).
- Edge labels must be VERBS/ACTIONS only (1-3 words): submit, send, store, push API, forward, import CSV, etc.
- Group nodes into lanes (rows). Typical lanes: Data Subject, Website/DB, CRM, Marketing, Other Dept/Vendors.
- Prefer lanes named from narrative; if missing, infer reasonable ones.
- Avoid copying long sentences into node labels.
- Keep only the key flow; avoid too much detail.

JSON schema:
{
  "title": "...",
  "lanes": [
    { "id": "lane_ds", "name": "Data Subject", "color": "#DFF3E3" }
  ],
  "nodes": [
    { "id": "n1", "lane": "lane_ds", "label": "Submit web form" }
  ],
  "edges": [
    { "from": "n1", "to": "n2", "label": "send" }
  ]
}
"""

def interpret_diagram_plan_openai(flow_name: str, narrative: str) -> Dict[str, Any]:
    user_prompt = f"""
Flow name: {flow_name}

Narrative:
{narrative}

Return the JSON plan now.
""".strip()

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = (resp.choices[0].message.content or "").strip()

    # Parse JSON safely
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise
