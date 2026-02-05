"use client";

import { useState, useCallback } from "react";
import { api } from "../lib/api";
import type { ProcessFlow, FlowQuestion, Progress, FlowAnswer } from "../lib/types";
import { downloadBlob } from "../lib/utils";

export function useRopaFlow() {
  const [mode, setMode] = useState<"controller" | "processor">("controller");
  const [processName, setProcessName] = useState<string>("");
  const [customName, setCustomName] = useState("");

  const [flows, setFlows] = useState<ProcessFlow[]>([]);
  const [flow, setFlow] = useState<ProcessFlow | null>(null);

  const [questions, setQuestions] = useState<FlowQuestion[]>([]);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [answers, setAnswers] = useState<FlowAnswer[]>([]);

  const [currentKey, setCurrentKey] = useState<string | null>(null);
  const [loadingStart, setLoadingStart] = useState(false);

  // local draft for each key
  const [draftByKey, setDraftByKey] = useState<Record<string, string>>({});

  const resetLocalSession = useCallback(() => {
    setFlow(null);
    setProgress(null);
    setAnswers([]);
    setCurrentKey(null);
    setDraftByKey({});
  }, []);

  const loadFlows = useCallback(async () => {
    const res = await api.get<ProcessFlow[]>("/process-flows/");
    setFlows(res.data);
  }, []);

  const loadQuestions = useCallback(async () => {
    const res = await api.get<FlowQuestion[]>("/process-flow-questions/");
    setQuestions(res.data);
  }, []);

  const loadAnswers = useCallback(async (flowId: number) => {
    const res = await api.get<FlowAnswer[]>(`/process-flows/${flowId}/answers/`);
    setAnswers(res.data);
  }, []);

  const refreshProgress = useCallback(async (flowId: number) => {
    const res = await api.get<Progress>(`/process-flows/${flowId}/progress/`);
    setProgress(res.data);
    return res.data;
  }, []);

  const useCustomProcessName = useCallback(() => {
    const name = customName.trim();
    if (!name) return;
    setProcessName(name);
    resetLocalSession();
    setCustomName("");
  }, [customName, resetLocalSession]);

  const startRopa = useCallback(async () => {
    if (!processName) return;

    setLoadingStart(true);
    setCurrentKey(null);

    try {
      const created = await api.post<ProcessFlow>("/process-flows/", {
        name: processName,
        description: `Mode: ${mode}`,
      });

      setFlow(created.data);

      await Promise.all([
        loadAnswers(created.data.id),
        loadFlows(),
      ]);
      const p = await refreshProgress(created.data.id);
      setCurrentKey(p.next_recommended_key);
    } finally {
      setLoadingStart(false);
    }
  }, [processName, mode, loadAnswers, loadFlows, refreshProgress]);

  const resumeFlow = useCallback(async (f: ProcessFlow) => {
    setFlow(f);
    setProcessName(f.name);
    setCurrentKey(null);

    await loadAnswers(f.id);
    const p = await refreshProgress(f.id);
    setCurrentKey(p.next_recommended_key);
  }, [loadAnswers, refreshProgress]);

  const goNextByBackend = useCallback(async (flowId: number) => {
    await Promise.all([loadAnswers(flowId), loadFlows()]);
    const p = await refreshProgress(flowId);
    setCurrentKey(p.next_recommended_key);
  }, [loadAnswers, loadFlows, refreshProgress]);

  const generateRopaExcel = useCallback(async (flowId: number) => {
    const res = await api.get(`/process-flows/${flowId}/export-ropa/`, {
      responseType: "blob",
    });

    const blob = new Blob([res.data], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    downloadBlob(blob, `RoPA_${flowId}.xlsx`);
  }, []);

  const generateProcessFlowDocx = useCallback(async (flowId: number) => {
    const res = await api.get(`/process-flows/${flowId}/export-processflow-docx/`, {
      responseType: "blob",
    });

    const blob = new Blob([res.data], {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });

    downloadBlob(blob, `ProcessFlow_${flowId}.docx`);
  }, []);

  const selectProcessName = useCallback((name: string) => {
    setProcessName(name);
    resetLocalSession();
  }, [resetLocalSession]);

  return {
    // State
    mode,
    setMode,
    processName,
    setProcessName,
    customName,
    setCustomName,
    flows,
    flow,
    questions,
    progress,
    answers,
    currentKey,
    setCurrentKey,
    loadingStart,
    draftByKey,
    setDraftByKey,

    // Actions
    resetLocalSession,
    loadFlows,
    loadQuestions,
    loadAnswers,
    refreshProgress,
    useCustomProcessName,
    startRopa,
    resumeFlow,
    goNextByBackend,
    generateRopaExcel,
    generateProcessFlowDocx,
    selectProcessName,
  };
}
