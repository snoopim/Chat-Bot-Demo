# flows/openai_ropa_excel.py
import json
import re
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
    "DPIA",
]

SYSTEM_PROMPT = """
You are a GDPR RoPA assistant.

Goal:
Generate ONE complete RoPA Excel row using the provided headers.

How to answer:
1. First, use DIRECT matches from known_answers if available.
2. If a header was NOT asked directly:
   - Infer the answer by analysing:
     • the process_flow_narrative
     • all other known_answers together
3. Only infer when there is clear logical support.
4. If inference is weak, unclear, or not supported:
   - Use "Unknown"
   - Use "N/A" only when clearly not applicable.

STRICT RULES:
- Output MUST be valid JSON only.
- ALL headers must be present exactly as provided.
- Do NOT invent facts.
- Do NOT assume compliance without evidence.
- Keep answers concise (Excel-friendly).

YES/NO RULE:
- For these Yes/No fields, use ONLY: "Yes" or "No" (or "N/A" if truly not applicable):
  - Is there a current process map?
  - Shared?
  - Outsourced processing?
  - Automated processing?
  - Transborder processing?
  - Appropriate privacy notice
  - Purpose limitation
  - Accuracy
  - Data minimisation
  - Storage limitation
  - Security
  - Personal data
  - Financial data
  - Special categories
  - Children’s Data

Access control rule:
- For "Access control":
  - Use "Controlled" if access is restricted (role-based, permissions, limited staff, etc.)
  - Use "Uncontrolled" if access is open, shared, or not restricted
  - Use "Unknown" if unclear

DPIA and GDPR rule:
- Do NOT guess DPIA.
- If clearly stated in known_answers/narrative, you may answer "Yes" or "No".
- Otherwise use "Unknown".

Formatting rules:
- "Which Assets are used?":
  • Output ONLY system/tool names
  • One system per line
  • No explanation text
  • Keep original names if provided (do not rewrite)
- "Data formats" → Single | Multiple | Unknown
- "Data volume" → Low | Medium | High | Unknown

Never guess GDPR compliance or security without evidence.
"""


def _safe_json_parse(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def _to_yes_no(v: str) -> str:
    t = (v or "").strip().lower()
    if t in {"yes", "y", "true", "1"}:
        return "Yes"
    if t in {"no", "n", "false", "0"}:
        return "No"
    if t in {"n/a", "na"}:
        return "N/A"
    if not t or t == "unknown":
        return "Unknown"
    return "Unknown"


def _to_yes_no_strict(v: str) -> str:
    """
    Stricter: ONLY accept explicit yes/no/n/a/unknown.
    Anything else becomes Unknown.
    """
    t = (v or "").strip().lower()
    if t in {"yes", "y"}:
        return "Yes"
    if t in {"no", "n"}:
        return "No"
    if t in {"n/a", "na"}:
        return "N/A"
    if t in {"unknown", ""}:
        return "Unknown"
    return "Unknown"


def _to_yes_no_from_sentence(v: str) -> str:
    """
    For columns where the model may write 'Yes. Types: ...'
    We extract the leading decision only.
    """
    t = (v or "").strip().lower()
    if t.startswith("yes"):
        return "Yes"
    if t.startswith("no"):
        return "No"
    if t.startswith("n/a") or t.startswith("na"):
        return "N/A"
    if not t or t.startswith("unknown"):
        return "Unknown"
    return "Unknown"


def _to_access_control(v: str) -> str:
    t = (v or "").strip().lower()

    # direct tokens
    if t in {"controlled", "control"}:
        return "Controlled"
    if t in {"uncontrolled"}:
        return "Uncontrolled"

    # if model returned yes/no by mistake
    if t in {"yes", "y", "true", "1"}:
        return "Controlled"
    if t in {"no", "n", "false", "0"}:
        return "Uncontrolled"

    if not t or t in {"unknown", "n/a", "na"}:
        return "Unknown"

    # keyword inference (cautious)
    if any(
        k in t
        for k in [
            "role-based",
            "role based",
            "rbac",
            "permission",
            "restricted",
            "limited",
            "least privilege",
            "access control",
        ]
    ):
        return "Controlled"
    if any(
        k in t
        for k in [
            "anyone",
            "everyone",
            "public",
            "no restriction",
            "unrestricted",
            "shared drive",
            "open access",
        ]
    ):
        return "Uncontrolled"

    return "Unknown"


def _format_assets_one_per_line(v: str) -> str:
    """
    Convert to one system per line.
    - Split on newlines and semicolons always.
    - Split on commas only if there are no parentheses
      (avoid breaking 'MS 365 (email, SharePoint)').
    """
    raw = (v or "").strip()
    if not raw or raw.lower() in {"unknown", "n/a", "na"}:
        return "Unknown"

    chunks: List[str] = []
    for part in re.split(r"[\n;]+", raw):
        part = part.strip()
        if part:
            chunks.append(part)

    # if still a single chunk and comma-separated list without parentheses, split by commas
    if len(chunks) == 1 and "," in chunks[0] and "(" not in chunks[0] and ")" not in chunks[0]:
        chunks = [p.strip() for p in chunks[0].split(",") if p.strip()]

    # de-dup preserve order
    seen = set()
    out = []
    for c in chunks:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            out.append(c)

    return "\n".join(out) if out else "Unknown"


def generate_ropa_row_openai(
    flow_name: str,
    known_answers: Dict[str, str],
    narrative: str,
    has_process_map: bool = False,
    model: str = "gpt-4o-mini",
) -> Dict[str, str]:
    compact = {k: (v or "").strip() for k, v in known_answers.items() if (v or "").strip()}

    hints = {
        "flow_name": flow_name,
        "has_process_map": "Yes" if has_process_map else "No",
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

    # Ensure all headers exist
    out: Dict[str, str] = {}
    for h in ROPA_HEADERS:
        v = obj.get(h, "Unknown")
        if v is None or str(v).strip() == "":
            v = "Unknown"
        out[h] = str(v).strip()

    # Normalize core Yes/No headers (NOT Access control, NOT DPIA here)
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
        out[h] = _to_yes_no(out.get(h, "Unknown"))

    # Data classification columns: ONLY Yes/No/Unknown/N/A (strip extra text)
    data_class_headers = {
        "Personal data",
        "Financial data",
        "Special categories",
        "Children's Data",
    }
    for h in data_class_headers:
        out[h] = _to_yes_no_from_sentence(out.get(h, "Unknown"))

    # Access control: Controlled/Uncontrolled/Unknown
    out["Access control"] = _to_access_control(out.get("Access control", "Unknown"))

    # DPIA: STRICT yes/no/n/a/unknown only (else Unknown)
    out["DPIA"] = _to_yes_no_strict(out.get("DPIA", "Unknown"))

    # Assets formatting: one system per line
    out["Which Assets are used?"] = _format_assets_one_per_line(out.get("Which Assets are used?", "Unknown"))

    # Force process map from backend signal
    out["Is there a current process map?"] = "Yes" if has_process_map else "No"

    return out
