# flows/openai_ropa_excel.py
import json
from typing import Dict, Any, List
from openai import OpenAI

client = OpenAI()

ROPA_HEADERS: List[str] = [
    "List key business processes",
    "What does the process do?",
    "Who are the data subjects? (Describe)",
    "Which Assets are used?",
    "Is there a current process map?",
    "Organisation's status",
    "Personal data",
    "Financial data",
    "Special categories",
    "Children's Data",
    "Data formats",
    "Data source",
    "Data volume",
    "Internal Process Owner",
    "Who has access",
    "Access control",
    "Shared?",
    "Outsourced processing?",
    "Automated processing?",
    "Transborder processing?",
    "Retention Period?",
    "Lawful basis",
    "Appropriate privacy notice",
    "Purpose limitation",
    "Accuracy",
    "Data minimisation",
    "Storage limitation",
    "Security",
    "GDPR compliance?",
    "DPIA",
]

SYSTEM_PROMPT = """
You are a GDPR RoPA assistant.

Task:
Given a process flow name and known answers, generate a complete RoPA row for a fixed set of Excel headers.

Rules:
- Output MUST be valid JSON only. No markdown, no commentary.
- Must include ALL headers exactly as keys (case-sensitive).
- If unknown, use:
  - "N/A" for not applicable,
  - "Unknown" when information is missing.
- For Yes/No fields, use ONLY: "Y" or "N" (or "N/A" if truly not applicable).
- Keep each cell concise.
- "Which Assets are used?" should be a single string separated by semicolons.
- "Data volume" should be one of: Low, Medium, High, Unknown.
- "Data formats" should be one of: Single, Multiple, Unknown.

Output JSON schema:
{
  "List key business processes": "...",
  ...
  "DPIA": "..."
}
"""

def _safe_json_parse(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # salvage between first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise

def generate_ropa_row_openai(
    flow_name: str,
    known_answers: Dict[str, str],
    narrative: str,
    has_process_map: bool = False,
    model: str = "gpt-4o-mini",
) -> Dict[str, str]:
    """
    Returns: dict where keys are ROPA_HEADERS and values are strings.
    """
    # Minimal + useful context (don’t send everything huge)
    compact = {k: (v or "").strip() for k, v in known_answers.items() if (v or "").strip()}
    # Some helpful hints derived from your data:
    hints = {
        "flow_name": flow_name,
        "has_process_map": "Y" if has_process_map else "N",
    }

    user_payload = {
        "headers": ROPA_HEADERS,
        "hints": hints,
        "known_answers": compact,
        "narrative": (narrative or "").strip(),
    }

    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
    )
    text = (resp.choices[0].message.content or "").strip()
    obj = _safe_json_parse(text)

    # Validate: ensure all headers exist
    out: Dict[str, str] = {}
    for h in ROPA_HEADERS:
        v = obj.get(h, "Unknown")
        if v is None or str(v).strip() == "":
            v = "Unknown"
        out[h] = str(v).strip()

    # Normalize Y/N columns (optional strictness)
    yn_headers = {
        "Is there a current process map?",
        "Appropriate privacy notice",
        "Purpose limitation",
        "Accuracy",
        "Data minimisation",
        "Storage limitation",
        "Security",
        "GDPR compliance?",
        "Shared?",
        "Outsourced processing?",
        "Automated processing?",
        "Transborder processing?",
    }
    for h in yn_headers:
        v = out.get(h, "Unknown").strip().upper()
        if v in {"YES", "Y"}:
            out[h] = "Y"
        elif v in {"NO", "N"}:
            out[h] = "N"
        elif v in {"NA", "N/A"}:
            out[h] = "N/A"
        else:
            # keep Unknown if not clearly yes/no
            out[h] = "Unknown"

    # Force process map from your known info (stronger than model guess)
    out["Is there a current process map?"] = "Y" if has_process_map else "N"

    return out
