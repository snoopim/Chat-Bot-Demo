"use client";

import { useMemo, useCallback } from "react";
import type { FlowQuestion, FlowAnswer } from "../lib/types";
import { normalizeYesNo } from "../lib/utils";

type UseQuestionNavigationParams = {
  questions: FlowQuestion[];
  answers: FlowAnswer[];
  currentKey: string | null;
  setCurrentKey: (key: string | null) => void;
  setAi: (ai: null) => void;
};

export function useQuestionNavigation({
  questions,
  answers,
  currentKey,
  setCurrentKey,
  setAi,
}: UseQuestionNavigationParams) {
  const answerByKey = useMemo(() => {
    const m = new Map<string, FlowAnswer>();
    for (const a of answers) m.set(a.question_key, a);
    return m;
  }, [answers]);

  const skippedKeys = useMemo(() => {
    return answers.filter((a) => a.status === "skipped").map((a) => a.question_key);
  }, [answers]);

  // Hide questions whose depends_on is not satisfied + hide auto "Not applicable"
  const visibleQuestions = useMemo(() => {
    const getAnswerText = (key: string) => answerByKey.get(key)?.answer_text ?? "";

    return questions.filter((q: FlowQuestion & { depends_on?: { key: string; value: string } }) => {
      const dep = q.depends_on;
      if (dep?.key) {
        const parentVal = normalizeYesNo(getAnswerText(dep.key));
        const need = String(dep.value || "").toLowerCase();
        // if parent answered and does NOT match required => hide child
        if (parentVal && parentVal !== need) return false;
      }

      const myAns = (getAnswerText(q.key) || "").trim().toLowerCase();
      if (myAns === "not applicable") return false;

      return true;
    });
  }, [questions, answerByKey]);

  const current = useMemo(
    () => visibleQuestions.find((q) => q.key === currentKey) || null,
    [visibleQuestions, currentKey]
  );

  const questionIndex = useMemo(() => {
    if (!currentKey) return -1;
    return visibleQuestions.findIndex((q) => q.key === currentKey);
  }, [visibleQuestions, currentKey]);

  const goPrev = useCallback(() => {
    if (questionIndex <= 0) return;
    setAi(null);
    setCurrentKey(visibleQuestions[questionIndex - 1].key);
  }, [questionIndex, visibleQuestions, setAi, setCurrentKey]);

  const continueSkipped = useCallback(() => {
    if (skippedKeys.length === 0) return;
    setAi(null);
    setCurrentKey(skippedKeys[0]);
  }, [skippedKeys, setAi, setCurrentKey]);

  return {
    visibleQuestions,
    current,
    questionIndex,
    skippedKeys,
    answerByKey,
    goPrev,
    continueSkipped,
  };
}
