"use client";

import { useEffect, useState } from "react";
import { api } from "./lib/api";
import type { AiResult } from "./lib/types";
import { useRopaFlow } from "./hooks/useRopaFlow";
import { useQuestionNavigation } from "./hooks/useQuestionNavigation";
import { useTypoCheck } from "./hooks/useTypoCheck";
import { Sidebar } from "./components/Sidebar";
import { QuestionPanel } from "./components/QuestionPanel";
import { TypoModal } from "./components/TypoModal";

export default function Page() {
  const ropaFlow = useRopaFlow();
  const typoCheck = useTypoCheck();

  const [answer, setAnswer] = useState("");
  const [ai, setAi] = useState<AiResult | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const questionNav = useQuestionNavigation({
    questions: ropaFlow.questions,
    answers: ropaFlow.answers,
    currentKey: ropaFlow.currentKey,
    setCurrentKey: ropaFlow.setCurrentKey,
    setAi,
  });

  // Initial data load
  useEffect(() => {
    (async () => {
      await Promise.all([ropaFlow.loadFlows(), ropaFlow.loadQuestions()]);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // If currentKey is now hidden, jump to backend recommended key
  useEffect(() => {
    if (!ropaFlow.flow || !ropaFlow.currentKey) return;
    const stillVisible = questionNav.visibleQuestions.some((q) => q.key === ropaFlow.currentKey);
    if (!stillVisible) {
      (async () => {
        const p = await ropaFlow.refreshProgress(ropaFlow.flow!.id);
        ropaFlow.setCurrentKey(p.next_recommended_key);
      })();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [questionNav.visibleQuestions, ropaFlow.currentKey, ropaFlow.flow?.id]);

  // When question changes, restore draft first, else backend answer
  useEffect(() => {
    setAi(null);
    typoCheck.resetTypoState();

    if (!ropaFlow.currentKey) {
      setAnswer("");
      return;
    }

    if (ropaFlow.draftByKey[ropaFlow.currentKey] !== undefined) {
      setAnswer(ropaFlow.draftByKey[ropaFlow.currentKey]);
      return;
    }

    const saved = questionNav.answerByKey.get(ropaFlow.currentKey);
    setAnswer(saved?.answer_text ?? "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ropaFlow.currentKey, questionNav.answerByKey, ropaFlow.draftByKey]);

  async function submitAnsweredCore(finalAnswer: string) {
    if (!ropaFlow.flow || !ropaFlow.currentKey) return;

    setSubmitting(true);
    try {
      const aiRes = await api.post<AiResult>(
        `/process-flows/${ropaFlow.flow.id}/validate-answer/`,
        { question_key: ropaFlow.currentKey, answer: finalAnswer }
      );

      setAi(aiRes.data);

      const isClear = aiRes.data?.is_clear === true;
      if (!isClear) return;

      await api.post(`/process-flows/${ropaFlow.flow.id}/answers/`, {
        question_key: ropaFlow.currentKey,
        status: "answered",
        answer_text: finalAnswer,
      });

      ropaFlow.setDraftByKey((prev) => ({ ...prev, [ropaFlow.currentKey!]: finalAnswer }));

      setAi(null);
      await ropaFlow.goNextByBackend(ropaFlow.flow.id);
    } finally {
      setSubmitting(false);
    }
  }

  async function submitAnswered() {
    if (!ropaFlow.flow || !ropaFlow.currentKey) return;
    if (!answer.trim()) return;

    setAi(null);

    try {
      const typo = await typoCheck.checkTypos(answer);
      const hasTypo = typo.has_typo ?? false;
      const suggested = typo.suggested_text ?? typo.fixed_text ?? "";

      if (hasTypo && suggested && suggested.trim() && suggested !== answer) {
        typoCheck.openTypoModal(answer, suggested, true);
        return;
      }
    } catch {
      // ignore
    }

    await submitAnsweredCore(answer);
  }

  async function applyTypoFix() {
    const fixed = typoCheck.typoSuggested || answer;
    setAnswer(fixed);
    if (ropaFlow.currentKey) {
      ropaFlow.setDraftByKey((prev) => ({ ...prev, [ropaFlow.currentKey!]: fixed }));
    }

    typoCheck.closeTypoModal();

    if (typoCheck.typoPendingSubmit) {
      typoCheck.setTypoPendingSubmit(false);
      await submitAnsweredCore(fixed);
    }
  }

  async function keepMyText() {
    const original = typoCheck.typoOriginal || answer;
    if (ropaFlow.currentKey) {
      ropaFlow.setDraftByKey((prev) => ({ ...prev, [ropaFlow.currentKey!]: original }));
    }

    typoCheck.closeTypoModal();

    if (typoCheck.typoPendingSubmit) {
      typoCheck.setTypoPendingSubmit(false);
      await submitAnsweredCore(original);
    }
  }

  async function skipNow() {
    if (!ropaFlow.flow || !ropaFlow.currentKey) return;

    //  Guard: if already answered, don't overwrite it as skipped
    const existing = questionNav.answerByKey.get(ropaFlow.currentKey);
    if (existing?.status === "answered") {
      // Just move on (or you can show a message if you want)
      await ropaFlow.goNextByBackend(ropaFlow.flow.id);
      return;
    }

    setSubmitting(true);
    try {
      setAi(null);

      await api.post(`/process-flows/${ropaFlow.flow.id}/answers/`, {
        question_key: ropaFlow.currentKey,
        status: "skipped",
        answer_text: "",
      });

      ropaFlow.setDraftByKey((prev) => ({ ...prev, [ropaFlow.currentKey!]: "" }));

      await ropaFlow.goNextByBackend(ropaFlow.flow.id);
    } finally {
      setSubmitting(false);
    }
  }


  function handleAnswerChange(value: string) {
    setAnswer(value);
    if (ropaFlow.currentKey) {
      ropaFlow.setDraftByKey((prev) => ({ ...prev, [ropaFlow.currentKey!]: value }));
    }
  }

  return (
    <div className="h-screen flex bg-black text-white">
      <TypoModal
        open={typoCheck.typoOpen}
        original={typoCheck.typoOriginal}
        suggested={typoCheck.typoSuggested}
        onApplyFix={applyTypoFix}
        onKeepOriginal={keepMyText}
      />

      <Sidebar
        flows={ropaFlow.flows}
        flow={ropaFlow.flow}
        progress={ropaFlow.progress}
        processName={ropaFlow.processName}
        customName={ropaFlow.customName}
        loadingStart={ropaFlow.loadingStart}
        skippedCount={questionNav.skippedKeys.length}
        onResume={ropaFlow.resumeFlow}
        onExportRopa={ropaFlow.generateRopaExcel}
        onExportDocx={ropaFlow.generateProcessFlowDocx}
        onSelectProcess={ropaFlow.selectProcessName}
        onCustomNameChange={ropaFlow.setCustomName}
        onUseCustomName={ropaFlow.useCustomProcessName}
        onStartRopa={ropaFlow.startRopa}
        onContinueSkipped={questionNav.continueSkipped}
      />

      <QuestionPanel
        flow={ropaFlow.flow}
        current={questionNav.current}
        visibleQuestions={questionNav.visibleQuestions}
        questionIndex={questionNav.questionIndex}
        answer={answer}
        ai={ai}
        submitting={submitting}
        typoOpen={typoCheck.typoOpen}
        onAnswerChange={handleAnswerChange}
        onPrevious={questionNav.goPrev}
        onSubmit={submitAnswered}
        onSkip={skipNow}
      />
    </div>
  );
}
