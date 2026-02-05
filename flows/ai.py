# flows/ai.py
import os
import json
from openai import OpenAI

# ------------------------------------------------------------
# OpenAI client (safe to create even if key is missing)
# ------------------------------------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------------------------------------
# Allowed RoPA headings (used for formatting)
# ------------------------------------------------------------
ROPA_HEADINGS = [
    "Name of the Process",
    "What does the process do",
    "Is there a Process Flow",
    "Who are the Data Subjects",
    "Organisation’s Status",
    "List the Assets used",
    "Process Owner",
    "Who Has Access",
    "Is Access Control Applied",
    "Personal Data",
    "Financial Data",
    "Children’s Data",
    "Data Source",
    "What is your lawful basis for processing",
    "What is the Retention Period",
    "Special Category Data Used",
    "Is the Data shared with other organisations",
    "Is the processing outsourced",
    "Is the process using automatic decision-making",
    "Is the data held outside the UK/EAA",
]

# ------------------------------------------------------------
# Map each question_key -> ONE matching heading
# (This makes the AI suggestion always match the current question)
# ------------------------------------------------------------
HEADING_BY_KEY = {
    # note: you removed process_name question, but keep mapping if you add later
    "process_name": "Name of the Process",
    "process_purpose": "What does the process do",
    "process_owner": "Process Owner",
    "data_subjects": "Who are the Data Subjects",
    "data_categories": "Personal Data",
    "systems_assets": "List the Assets used",
    "data_source": "Data Source",
    "sharing": "Is the Data shared with other organisations",
    "outsourcing": "Is the processing outsourced",
    "retention": "What is the Retention Period",
    "outside_uk_eaa": "Is the data held outside the UK/EAA",
    "adm": "Is the process using automatic decision-making",
}

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def strip_emdash(s: str) -> str:
    return (s or "").replace("—", "-")


def safe_json_load(text: str) -> dict:
    """
    Load JSON safely from model output.
    Supports mixed text + JSON.
    """
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def enforce_short_heading_suggestion(s: str, allowed_headings: list[str]) -> str:
    """
    Keep suggestions short and ONLY using allowed headings.
    """
    if not s:
        return ""

    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    keep: list[str] = []

    for ln in lines:
        for h in allowed_headings:
            if ln.startswith(h + ":") or ln.startswith(h + " :"):
                keep.append(ln)
                break

    keep = keep[:4]  # max 4 lines
    if keep:
        return "\n".join(keep)

    # fallback if AI returned something else
    h0 = allowed_headings[0] if allowed_headings else "Answer"
    return f'{h0}: [Write a short, clear answer].'


# ------------------------------------------------------------
# MAIN: Judge answer quality for RoPA / Process Flow
# ------------------------------------------------------------
def judge_flow_answer(
    question_key: str,
    question_text: str,
    help_text: str,
    user_answer: str,
    flow_context: str = "",
) -> dict:
    """
    Check if a user's answer is clear enough for RoPA documentation.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    # ---- Safe fallback (NO AI, NO CRASH) ----
    if not api_key:
        return {
            "is_clear": True,
            "score": 100,
            "reason": "AI check skipped (OPENAI_API_KEY not configured).",
            "follow_up_question": "",
            "suggested_answer_format": "",
        }

    #  Only allow the ONE heading that matches this question_key
    preferred_heading = HEADING_BY_KEY.get(question_key, "What does the process do")
    allowed_headings = [preferred_heading]

    system = (
        "You help a user describe a personal data process so it can be used in a GDPR RoPA.\n"
        "Judge ONE question at a time.\n"
        "Be kind, patient, and practical.\n"
        "Do not use the em dash character.\n"
        "Do NOT rewrite the answer fully.\n"
        "If unclear, explain briefly and give an example format.\n\n"
        "IMPORTANT RULES:\n"
        "1) Return STRICT JSON only.\n"
        "2) suggested_answer_format must use ONLY the allowed heading.\n"
        "3) Each line must start with the allowed heading followed by ':'.\n"
        "4) 1–4 lines maximum.\n\n"
        "JSON keys:\n"
        "is_clear (boolean), score (0–100), reason (string), "
        "follow_up_question (string), suggested_answer_format (string)\n"
        "Assume the user is a general employee.\n"
        "Do NOT require technical IDs (bucket name, region, database name).\n"
        "If info is missing, prefer gentle guidance with an example: say 'You can try answering like this: ...'\n"
        "Mark as clear if they named the system + where they access it + owner/team.\n"
    )

    payload = {
        "question_key": question_key,
        "question_text": question_text,
        "help_text": help_text or "",
        "user_answer": user_answer or "",
        "flow_context": flow_context or "",
        "allowed_headings": allowed_headings,
    }

    schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "flow_judge",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "is_clear": {"type": "boolean"},
                    "score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "reason": {"type": "string"},
                    "follow_up_question": {"type": "string"},
                    "suggested_answer_format": {"type": "string"},
                },
                "required": [
                    "is_clear",
                    "score",
                    "reason",
                    "follow_up_question",
                    "suggested_answer_format",
                ],
            },
        },
    }

    #  model name configurable (avoid "model not found" issues)
    model_name = os.getenv("OPENAI_MODEL", "gpt-5.2")

    try:
        resp = client.responses.create(
            model=model_name,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format=schema,
        )
        data = safe_json_load(resp.output_text)

    except TypeError:
        # Older SDK fallback
        resp = client.responses.create(
            model=model_name,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        )
        data = safe_json_load(resp.output_text)

    out = {
        "is_clear": bool(data.get("is_clear", True)),
        "score": int(data.get("score", 0)),
        "reason": strip_emdash(str(data.get("reason", ""))),
        "follow_up_question": strip_emdash(str(data.get("follow_up_question", ""))),
        "suggested_answer_format": strip_emdash(str(data.get("suggested_answer_format", ""))),
    }

    out["score"] = max(0, min(100, out["score"]))
    out["suggested_answer_format"] = enforce_short_heading_suggestion(
        out["suggested_answer_format"],
        allowed_headings,
    )

    return out


# ------------------------------------------------------------
# Typo / grammar helper (NON-DESTRUCTIVE)
# ------------------------------------------------------------
def typo_check_text(user_text: str) -> dict:
    """
    Light typo / grammar helper only.
    Does NOT change meaning.
    """

    text = (user_text or "").strip()
    if not text:
        return {"has_fix": False, "fixed_text": "", "note": "Empty text."}

    if not os.getenv("OPENAI_API_KEY"):
        return {
            "has_fix": False,
            "fixed_text": text,
            "note": "OPENAI_API_KEY not set; typo check skipped.",
        }

    prompt = f"""
You are a careful copyeditor.
Fix spelling and grammar ONLY.
Do NOT change meaning.
Keep GDPR terms exactly (GDPR, RoPA, DPIA, DSAR, controller, processor).
If already correct, return has_fix=false.

Return JSON only:
has_fix (boolean), fixed_text (string), note (string)

Text:
{text}
""".strip()

    model_name = os.getenv("OPENAI_MODEL", "gpt-5.2")

    resp = client.responses.create(
        model=model_name,
        input=prompt,
    )

    raw = resp.output_text.strip()

    try:
        data = json.loads(raw)
        has_fix = bool(data.get("has_fix", False))
        fixed_text = str(data.get("fixed_text", "") or "")
        note = str(data.get("note", "") or "")

        if has_fix and not fixed_text.strip():
            return {"has_fix": False, "fixed_text": text, "note": "No usable fix."}

        return {
            "has_fix": has_fix,
            "fixed_text": fixed_text if has_fix else text,
            "note": note,
        }

    except Exception:
        return {
            "has_fix": False,
            "fixed_text": text,
            "note": "Typo check returned non-JSON output (fallback).",
        }
