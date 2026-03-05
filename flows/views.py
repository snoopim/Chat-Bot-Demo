# flows/views.py
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import re
import subprocess
import shutil

from django.conf import settings
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from openpyxl import Workbook
from docx import Document
from docx.shared import Inches

from .models import ProcessFlow, ProcessFlowAnswer
from .serializers import ProcessFlowSerializer, ProcessFlowAnswerSerializer
from .questions import PROCESS_FLOW_QUESTIONS
from .ai import judge_flow_answer, typo_check_text
from .openai_ropa_excel import ROPA_HEADERS, generate_ropa_row_openai

# Old diagram generator (fallback)
from .drawio import build_drawio_from_answers

# Render draw.io XML -> PNG
from .drawio_render import render_drawio_png, DrawioRenderResult

# NEW: OpenAI interpreter + plan->drawio builder
from .openai_interpreter import interpret_diagram_plan_openai
from .drawio_from_plan import build_drawio_from_plan


# -----------------------------
# Constants
# -----------------------------
QUESTION_BY_KEY = {q["key"]: q for q in PROCESS_FLOW_QUESTIONS}
QUESTION_KEYS = [q["key"] for q in PROCESS_FLOW_QUESTIONS]
REQUIRED_KEYS = [q["key"] for q in PROCESS_FLOW_QUESTIONS if q.get("required")]


# -----------------------------
# Helpers
# -----------------------------
def _clean(s: str) -> str:
    return (s or "").strip()


def normalize_yes_no(text: str) -> str:
    t = (text or "").strip().lower()
    if t.startswith("y"):
        return "yes"
    if t.startswith("n"):
        return "no"
    return ""


def _split_assets(text: str):
    raw = _clean(text)
    if not raw:
        return []
    parts = []
    for chunk in raw.replace(";", "\n").splitlines():
        for p in chunk.split(","):
            p = p.strip()
            if p:
                parts.append(p)

    # de-dup keep order
    seen = set()
    out = []
    for p in parts:
        k = p.lower()
        if k not in seen:
            seen.add(k)
            out.append(p)
    return out


def recompute_status(flow: ProcessFlow):
    """
    COMPLETED only when ALL questions are answered.
    Skipped does NOT count.
    NOTE: depends_on children may be auto-answered "Not applicable" (counts as answered).
    """
    qs = ProcessFlowAnswer.objects.filter(process_flow=flow)
    answered_keys = set(qs.filter(status="answered").values_list("question_key", flat=True))
    remaining = [k for k in QUESTION_KEYS if k not in answered_keys]

    if len(remaining) == 0:
        flow.status = "completed"
    elif len(answered_keys) > 0:
        flow.status = "in_progress"
    else:
        flow.status = "not_completed"

    flow.save(update_fields=["status"])


def apply_depends_on(flow: ProcessFlow):
    """
    If a child depends_on parent=yes but parent is NO,
    auto-answer child as "Not applicable" so it won't block completion/export.
    If parent later becomes YES, reset child back to unanswered.
    """
    answers = {a.question_key: a for a in ProcessFlowAnswer.objects.filter(process_flow=flow)}

    for q in PROCESS_FLOW_QUESTIONS:
        dep = q.get("depends_on")
        if not dep:
            continue

        child_key = q["key"]
        parent_key = dep.get("key")
        need_value = str(dep.get("value", "")).lower()

        parent_ans = answers.get(parent_key)
        parent_val = normalize_yes_no(parent_ans.answer_text if parent_ans else "")

        child_obj, _ = ProcessFlowAnswer.objects.get_or_create(
            process_flow=flow,
            question_key=child_key,
            defaults={"status": "unanswered"},
        )

        # parent answered and doesn't match -> Not applicable
        if parent_val and parent_val != need_value:
            child_obj.status = "answered"
            child_obj.answer_text = "Not applicable"
            child_obj.save(update_fields=["status", "answer_text"])

        # parent matches -> reset if previously auto-filled
        elif parent_val == need_value:
            if (child_obj.answer_text or "").strip().lower() == "not applicable":
                child_obj.status = "unanswered"
                child_obj.answer_text = None
                child_obj.save(update_fields=["status", "answer_text"])


def build_textual_description(flow: ProcessFlow, answer_map: dict) -> str:
    """
    Fallback narrative if user didn't fill process_flow_narrative.
    Uses YOUR questions.py keys.
    """
    purpose = _clean(answer_map.get("process_purpose", ""))
    subjects = _clean(answer_map.get("data_subjects", ""))
    source = _clean(answer_map.get("data_source", ""))
    systems = _clean(answer_map.get("systems_assets", ""))

    sharing_internal = _clean(answer_map.get("sharing_internal", ""))
    third_party_access = _clean(answer_map.get("third_party_access", ""))

    retention = _clean(answer_map.get("retention", ""))
    access = _clean(answer_map.get("who_has_access", ""))
    access_control = _clean(answer_map.get("access_control", ""))
    outside_uk_eaa = _clean(answer_map.get("outside_uk_eaa", ""))

    steps = []
    if subjects:
        steps.append(f"Data subjects: {subjects}.")
    if source:
        steps.append(f"Data source: {source}.")
    if purpose:
        steps.append(f"Purpose: {purpose}.")
    if systems:
        steps.append(f"Systems/assets used: {systems}.")
    if access:
        steps.append(f"Who has access: {access}.")
    if access_control:
        steps.append(f"Access control: {access_control}.")
    if sharing_internal:
        steps.append(f"Internal sharing: {sharing_internal}.")
    if third_party_access:
        steps.append(f"External parties/vendors: {third_party_access}.")
    if outside_uk_eaa:
        steps.append(f"Outside UK/EEA: {outside_uk_eaa}.")
    if retention:
        steps.append(f"Retention: {retention}.")

    if not steps:
        steps.append(
            "Describe the steps from start to finish: who provides the data, where it is stored, and who can access it."
        )

    return "\n".join(steps)


# -----------------------------
# Mermaid helpers (optional / unused here)
# -----------------------------
@dataclass
class MermaidRenderResult:
    ok: bool
    png_path: Optional[Path] = None
    mmd_path: Optional[Path] = None
    cmd: Optional[list] = None
    error: Optional[str] = None


def render_mermaid_png(mermaid_text: str, out_dir: Path, name: str) -> MermaidRenderResult:
    out_dir.mkdir(parents=True, exist_ok=True)

    mmd_path = out_dir / f"{name}.mmd"
    png_path = out_dir / f"{name}.png"
    mmd_path.write_text(mermaid_text, encoding="utf-8")

    mmdc = shutil.which("mmdc")
    if not mmdc:
        return MermaidRenderResult(
            ok=False,
            png_path=None,
            mmd_path=mmd_path,
            cmd=None,
            error=(
                "mmdc not found in PATH.\n"
                "Install it:\n"
                "  npm i -g @mermaid-js/mermaid-cli\n"
                "Then restart your terminal and restart Django.\n"
            ),
        )

    cmd = [mmdc, "-i", str(mmd_path), "-o", str(png_path), "-b", "transparent"]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )



# -----------------------------
# Views
# -----------------------------
class ProcessFlowListCreateView(APIView):
    # GET /api/process-flows/
    def get(self, request):
        flows = ProcessFlow.objects.all().order_by("-updated_at")
        return Response(ProcessFlowSerializer(flows, many=True).data)

    # POST /api/process-flows/
    def post(self, request):
        name = (request.data.get("name") or "").strip()
        description = (request.data.get("description") or "").strip()
        ai_provider = (request.data.get("ai_provider") or "openai").strip()

        if not name:
            return Response({"error": "name is required"}, status=status.HTTP_400_BAD_REQUEST)

        flow = ProcessFlow.objects.create(name=name, description=description, ai_provider=ai_provider)

        apply_depends_on(flow)
        recompute_status(flow)
        return Response(ProcessFlowSerializer(flow).data, status=status.HTTP_201_CREATED)


class ProcessFlowQuestionsView(APIView):
    # GET /api/process-flow-questions/
    def get(self, request):
        return Response(PROCESS_FLOW_QUESTIONS, status=status.HTTP_200_OK)


class ProcessFlowAnswersView(APIView):
    # GET /api/process-flows/<id>/answers/
    def get(self, request, flow_id: int):
        try:
            flow = ProcessFlow.objects.get(id=flow_id)
        except ProcessFlow.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        answers = ProcessFlowAnswer.objects.filter(process_flow=flow)
        return Response(ProcessFlowAnswerSerializer(answers, many=True).data)

    # POST /api/process-flows/<id>/answers/
    def post(self, request, flow_id: int):
        try:
            flow = ProcessFlow.objects.get(id=flow_id)
        except ProcessFlow.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        question_key = request.data.get("question_key")
        status_in = request.data.get("status")
        answer_text = request.data.get("answer_text", "")

        if question_key not in QUESTION_KEYS:
            return Response({"error": "Invalid question_key"}, status=status.HTTP_400_BAD_REQUEST)

        if status_in not in ["answered", "skipped"]:
            return Response({"error": "status must be answered or skipped"}, status=status.HTTP_400_BAD_REQUEST)

        obj, _ = ProcessFlowAnswer.objects.get_or_create(
            process_flow=flow,
            question_key=question_key,
            defaults={"status": "unanswered"},
        )

        obj.status = status_in
        obj.answer_text = (answer_text or "").strip() if status_in == "answered" else None
        obj.save()

        apply_depends_on(flow)
        recompute_status(flow)

        return Response({"ok": True, "flow_status": flow.status}, status=status.HTTP_200_OK)


class ProcessFlowProgressView(APIView):
    # GET /api/process-flows/<id>/progress/
    def get(self, request, flow_id: int):
        try:
            flow = ProcessFlow.objects.get(id=flow_id)
        except ProcessFlow.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        apply_depends_on(flow)
        recompute_status(flow)

        qs = ProcessFlowAnswer.objects.filter(process_flow=flow)
        answered_keys = set(qs.filter(status="answered").values_list("question_key", flat=True))
        skipped_keys = set(qs.filter(status="skipped").values_list("question_key", flat=True))

        total = len(QUESTION_KEYS)
        answered = len(answered_keys)
        skipped = len(skipped_keys)

        unanswered_keys = [k for k in QUESTION_KEYS if (k not in answered_keys and k not in skipped_keys)]
        remaining_for_completion = [k for k in QUESTION_KEYS if k not in answered_keys]

        if len(remaining_for_completion) == 0:
            status_out = "completed"
        elif answered > 0 or skipped > 0:
            status_out = "in_progress"
        else:
            status_out = "not_completed"

        percent = int(round((answered / total) * 100)) if total else 0
        next_key = unanswered_keys[0] if unanswered_keys else (list(skipped_keys)[0] if skipped_keys else None)
        remaining_keys = unanswered_keys + list(skipped_keys)

        return Response(
            {
                "status": status_out,
                "total": total,
                "answered": answered,
                "skipped": skipped,
                "unanswered": len(unanswered_keys),
                "percent": percent,
                "remaining_keys": remaining_keys,
                "next_recommended_key": next_key,
            },
            status=status.HTTP_200_OK,
        )


class ProcessFlowValidateAnswerView(APIView):
    # POST /api/process-flows/<id>/validate-answer/
    def post(self, request, flow_id: int):
        question_key = request.data.get("question_key")
        answer = request.data.get("answer", "")

        if question_key not in QUESTION_BY_KEY:
            return Response({"error": "Invalid question_key"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            flow = ProcessFlow.objects.get(id=flow_id)
        except ProcessFlow.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        saved = ProcessFlowAnswer.objects.filter(process_flow=flow, status="answered")
        context_lines = []
        for a in saved:
            if a.answer_text:
                context_lines.append(f"{a.question_key}: {a.answer_text}")
        flow_context = "\n".join(context_lines)[:2500]

        qmeta = QUESTION_BY_KEY[question_key]
        question_text = qmeta.get("text", "")
        help_text = qmeta.get("help_text", "") or ""

        result = judge_flow_answer(
            question_key=question_key,
            question_text=question_text,
            help_text=help_text,
            user_answer=answer,
            flow_context=flow_context,
        )

        return Response(result, status=status.HTTP_200_OK)


class TypoCheckView(APIView):
    # POST /api/typo-check/
    def post(self, request):
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"has_typo": False, "suggested_text": ""}, status=status.HTTP_200_OK)

        result = typo_check_text(text)
        has_fix = bool(result.get("has_fix", False))
        fixed_text = (result.get("fixed_text") or text).strip()

        payload = {
            "has_typo": has_fix and fixed_text != text,
            "suggested_text": fixed_text if has_fix else "",
            "has_fix": has_fix,
            "fixed_text": fixed_text,
            "note": result.get("note", ""),
        }
        return Response(payload, status=status.HTTP_200_OK)


from .openai_ropa_excel import ROPA_HEADERS, generate_ropa_row_openai

class ExportRopaExcelView(APIView):
    def get(self, request, flow_id: int):
        try:
            flow = ProcessFlow.objects.get(id=flow_id)
        except ProcessFlow.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if flow.status != "completed":
            return Response({"error": "Flow is not completed"}, status=status.HTTP_400_BAD_REQUEST)

        answers = ProcessFlowAnswer.objects.filter(process_flow=flow)

        # Collect known answers (your existing keys)
        answer_map = {
            a.question_key: (a.answer_text or "").strip()
            for a in answers
            if a.status == "answered" and a.answer_text
        }

        narrative = (answer_map.get("process_flow_narrative") or "").strip()

        # If you generate diagrams, you can set this based on whether a diagram exists
        # Simple rule: if narrative exists, assume there is a process map OR check your tmp file
        has_process_map = True  # or set False if you want strict file-checking

        # Ask OpenAI to produce full RoPA row for your custom headers
        ropa_dict = generate_ropa_row_openai(
            flow_name=flow.name,
            known_answers=answer_map,
            narrative=narrative,
            has_process_map=has_process_map,
        )

        # Convert to row in exact header order
        row = [ropa_dict.get(h, "Unknown") for h in ROPA_HEADERS]

        wb = Workbook()
        ws = wb.active
        ws.title = "RoPA"
        ws.append(ROPA_HEADERS)
        ws.append(row)

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)

        filename = f"RoPA_{flow.id}.xlsx"
        resp = HttpResponse(
            buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp


class ExportProcessFlowDocxView(APIView):
    # GET /api/process-flows/<id>/export-processflow-docx/
    def get(self, request, flow_id: int):
        try:
            flow = ProcessFlow.objects.get(id=flow_id)
        except ProcessFlow.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if flow.status != "completed":
            return Response({"error": "Flow is not completed"}, status=status.HTTP_400_BAD_REQUEST)

        qs = ProcessFlowAnswer.objects.filter(process_flow=flow)
        answer_map = {a.question_key: a.answer_text for a in qs if a.status == "answered" and a.answer_text}

        def ans(key: str) -> str:
            return _clean(answer_map.get(key, ""))

        process_owner = ans("process_owner")
        process_purpose = ans("process_purpose")
        narrative = ans("process_flow_narrative")

        data_subjects = ans("data_subjects")
        data_source = ans("data_source")
        data_collected = ans("data_collected")

        personal_data = ans("personal_data")
        financial_data = ans("financial_data")
        childrens_data = ans("childrens_data")
        special_category_data = ans("special_category_data")

        lawful_basis = ans("lawful_basis")
        retention = ans("retention")
        disposal = ans("disposal")

        systems_assets = ans("systems_assets")
        who_has_access = ans("who_has_access")
        access_control = ans("access_control")

        sharing_internal = ans("sharing_internal")
        third_party_access = ans("third_party_access")

        outside_uk_eaa = ans("outside_uk_eaa")
        transborder_agreement = ans("transborder_agreement")

        org_status = ans("org_status")
        data_shared_other_orgs = ans("data_shared_other_orgs")
        data_shared_other_orgs_details = ans("data_shared_other_orgs_details")
        data_sharing_agreement = ans("data_sharing_agreement")

        outsourced = ans("outsourced")
        dpa_in_place = ans("dpa_in_place")

        adm = ans("adm")
        other_info = ans("other_info")

        assets_list = _split_assets(systems_assets)
        assets_block = "\n".join([f"{i+1}. {x}" for i, x in enumerate(assets_list)]) if assets_list else systems_assets

        auto_description = build_textual_description(flow, answer_map)
        narrative_to_use = narrative or auto_description

        template_path = Path(__file__).resolve().parent / "templates" / "Portal Processflow template.docx"
        if template_path.exists():
            doc = Document(str(template_path))
            if (doc.paragraphs and any(p.text.strip() for p in doc.paragraphs)) or doc.tables:
                doc.add_page_break()
        else:
            doc = Document()

        # =====================================================
        # NEW diagram pipeline:
        # OpenAI -> plan -> drawio XML -> drawio PNG
        # =====================================================
        diagram_inputs = {
            **answer_map,
            "process_flow_narrative": narrative_to_use,
            "data_subjects": data_subjects,
            "systems_assets": systems_assets,
            "sharing_internal": sharing_internal,
            "third_party_access": third_party_access,
            "outside_uk_eaa": outside_uk_eaa,
            "who_has_access": who_has_access,
            "access_control": access_control,
        }

        plan = None
        plan_error = None
        drawio_xml = None

        try:
            # If your interpreter only needs narrative, keep this.
            # If it needs more context, change to: interpret_diagram_plan_openai(flow.name, diagram_inputs)
            plan = interpret_diagram_plan_openai(flow.name, narrative_to_use)
            drawio_xml = build_drawio_from_plan(plan)
        except Exception as e:
            plan_error = f"{type(e).__name__}: {e}"

        tmp_dir = Path(settings.BASE_DIR) / "tmp_drawio"
        name = f"process_flow_{flow.id}"

        if drawio_xml:
            render = render_drawio_png(drawio_xml, tmp_dir, name)
        else:
            # fallback: old generator
            try:
                fallback_xml = build_drawio_from_answers(flow.name, diagram_inputs)
                render = render_drawio_png(fallback_xml, tmp_dir, name)
                if not render.ok:
                    raise Exception(render.error or "fallback render failed")
            except Exception:
                class _FakeRender:
                    ok = False
                    png_path = None
                    drawio_path = tmp_dir / f"{name}.drawio"
                    cmd = None
                    error = plan_error or "Diagram could not be generated."

                render = _FakeRender()

        # =========================
        # SECTION 1: PROCESS OVERVIEW
        # =========================
        doc.add_heading("Process Overview", level=1)

        doc.add_heading("Name of the Process", level=2)
        doc.add_paragraph(_clean(flow.name) or "Not provided")

        doc.add_heading("Process Owner", level=2)
        doc.add_paragraph(process_owner or "Not provided")

        doc.add_heading("What is the purpose of the process", level=2)
        doc.add_paragraph(process_purpose or "Not provided")

        # =========================
        # SECTION 2: DIAGRAM
        # =========================
        doc.add_heading("Process Flow Diagram", level=1)

        if getattr(render, "ok", False) and getattr(render, "png_path", None):
            doc.add_picture(str(render.png_path), width=Inches(6.7)) #png
        else:
            doc.add_paragraph("Diagram could not be generated.")
            if getattr(render, "error", None):
                doc.add_paragraph("Debug details:")
                for line in str(render.error).splitlines()[:120]:
                    doc.add_paragraph(line)

        
        # =========================
        # SECTION 3: DATA PROCESS FLOW (NARRATIVE)
        # =========================
        doc.add_heading("Data Process Flow", level=1)
        doc.add_heading("Textual Description of the data flow", level=2)

        if narrative_to_use:
            for line in narrative_to_use.splitlines():
                line = line.strip()
                if line:
                    doc.add_paragraph(line)
        else:
            doc.add_paragraph("Not provided")

        # =========================
        # SECTION 4: DATA SUBJECTS AND DATA SOURCE
        # =========================
        doc.add_heading("Data Subjects and Data Source", level=1)

        doc.add_heading("Who are the Data Subjects", level=2)
        doc.add_paragraph(data_subjects or "Not provided")

        doc.add_heading("Where does the data come from", level=2)
        doc.add_paragraph(data_source or "Not provided")

        # =========================
        # SECTION 5: DATA COLLECTED AND DATA TYPES
        # =========================
        doc.add_heading("Data Collected and Data Types", level=1)

        doc.add_heading("What Data are you collecting", level=2)
        doc.add_paragraph(data_collected or "Not provided")

        doc.add_heading("Personal Data", level=2)
        doc.add_paragraph(personal_data or "Not provided")

        doc.add_heading("Financial Data", level=2)
        doc.add_paragraph(financial_data or "Not provided")

        doc.add_heading("Children’s Data", level=2)
        doc.add_paragraph(childrens_data or "Not provided")

        # =========================
        # SECTION 6: LAWFUL BASIS AND SPECIAL DATA
        # =========================
        doc.add_heading("Lawful Basis and Special Data", level=1)

        doc.add_heading("Lawful basis for processing", level=2)
        doc.add_paragraph(lawful_basis or "Not provided")

        doc.add_heading("Special Category Data or Criminal Conviction Data", level=2)
        doc.add_paragraph(special_category_data or "Not provided")

        # =========================
        # SECTION 7: RETENTION AND DISPOSAL
        # =========================
        doc.add_heading("Retention and Disposal", level=1)

        doc.add_heading("Retention Period", level=2)
        doc.add_paragraph(retention or "Not provided")

        doc.add_heading("Disposal", level=2)
        doc.add_paragraph(disposal or "Not provided")

        # =========================
        # SECTION 8: SYSTEMS AND ACCESS CONTROL
        # =========================
        doc.add_heading("Systems and Access Control", level=1)

        doc.add_heading("List the Assets used", level=2)
        doc.add_paragraph(assets_block or "Not provided")

        doc.add_heading("Who has access to the information", level=2)
        doc.add_paragraph(who_has_access or "Not provided")

        doc.add_heading("Is Access Control Applied", level=2)
        doc.add_paragraph(access_control or "Not provided")

        # =========================
        # SECTION 9: DATA SHARING AND TRANSFERS
        # =========================
        doc.add_heading("Data Sharing and Transfers", level=1)

        doc.add_heading("Sharing inside the organisation", level=2)
        doc.add_paragraph(sharing_internal or "Not provided")

        doc.add_heading("Third party or vendor access", level=2)
        doc.add_paragraph(third_party_access or "Not provided")

        doc.add_heading("Is the data stored or accessed outside the UK or EAA", level=2)
        doc.add_paragraph(outside_uk_eaa or "Not provided")

        doc.add_heading("If outside UK or EAA, is there an agreement in place", level=2)
        doc.add_paragraph(transborder_agreement or "Not provided")

        # =========================
        # SECTION 10: ORGANISATIONAL ROLE AND SHARING WITH OTHERS
        # =========================
        doc.add_heading("Organisational Role and Sharing with Others", level=1)

        doc.add_heading("Organisation’s Status", level=2)
        doc.add_paragraph(org_status or "Not provided")

        doc.add_heading("Is data shared with other organisations", level=2)
        doc.add_paragraph(data_shared_other_orgs or "Not provided")

        doc.add_heading("If yes, who is it shared with and why", level=2)
        doc.add_paragraph(data_shared_other_orgs_details or "Not provided")

        doc.add_heading("Is there a data sharing agreement", level=2)
        doc.add_paragraph(data_sharing_agreement or "Not provided")

        # =========================
        # SECTION 11: OUTSOURCING AND AUTOMATION
        # =========================
        doc.add_heading("Outsourcing and Automation", level=1)

        doc.add_heading("Is the processing outsourced", level=2)
        doc.add_paragraph(outsourced or "Not provided")

        doc.add_heading("If outsourced, is there a data processing agreement in place", level=2)
        doc.add_paragraph(dpa_in_place or "Not provided")

        doc.add_heading("Automatic decision making", level=2)
        doc.add_paragraph(adm or "Not provided")

        # =========================
        # SECTION 12: OTHER INFORMATION
        # =========================
        doc.add_heading("Other Information", level=1)

        doc.add_heading("Any other relevant information", level=2)
        doc.add_paragraph(other_info or "Not provided")

        # ---- Return DOCX ----
        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)

        filename = f"ProcessFlow_{flow.id}.docx"
        resp = HttpResponse(
            buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
