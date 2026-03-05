# flows/urls.py
from django.urls import path

from .views import (
    ProcessFlowListCreateView,
    ProcessFlowQuestionsView,
    ProcessFlowAnswersView,
    ProcessFlowProgressView,
    ProcessFlowValidateAnswerView,
    TypoCheckView,
    ExportRopaExcelView,
    ExportProcessFlowDocxView,
)

urlpatterns = [
    # list + create
    path("process-flows/", ProcessFlowListCreateView.as_view(), name="process-flow-list-create"),

    # questions list
    path("process-flow-questions/", ProcessFlowQuestionsView.as_view(), name="process-flow-questions"),

    # answers
    path("process-flows/<int:flow_id>/answers/", ProcessFlowAnswersView.as_view(), name="process-flow-answers"),

    # progress
    path("process-flows/<int:flow_id>/progress/", ProcessFlowProgressView.as_view(), name="process-flow-progress"),

    # AI validate
    path("process-flows/<int:flow_id>/validate-answer/", ProcessFlowValidateAnswerView.as_view(), name="process-flow-validate"),

    # typo check
    path("typo-check/", TypoCheckView.as_view(), name="typo-check"),

    # export
    path("process-flows/<int:flow_id>/export-ropa/", ExportRopaExcelView.as_view(), name="export-ropa"),

    path("process-flows/<int:flow_id>/export-processflow-docx/", ExportProcessFlowDocxView.as_view(), name="export-processflow-docx",),
]
