"use client";

import { useState, useCallback } from "react";
import { api } from "../lib/api";
import type { TypoCheckResult } from "../lib/types";

export function useTypoCheck() {
  const [typoOpen, setTypoOpen] = useState(false);
  const [typoOriginal, setTypoOriginal] = useState("");
  const [typoSuggested, setTypoSuggested] = useState("");
  const [typoPendingSubmit, setTypoPendingSubmit] = useState(false);

  const checkTypos = useCallback(async (text: string): Promise<TypoCheckResult> => {
    const res = await api.post<TypoCheckResult>("/typo-check/", { text });
    return res.data;
  }, []);

  const openTypoModal = useCallback((original: string, suggested: string, pendingSubmit: boolean) => {
    setTypoOriginal(original);
    setTypoSuggested(suggested);
    setTypoOpen(true);
    setTypoPendingSubmit(pendingSubmit);
  }, []);

  const closeTypoModal = useCallback(() => {
    setTypoOpen(false);
  }, []);

  const resetTypoState = useCallback(() => {
    setTypoOpen(false);
    setTypoOriginal("");
    setTypoSuggested("");
    setTypoPendingSubmit(false);
  }, []);

  return {
    typoOpen,
    typoOriginal,
    typoSuggested,
    typoPendingSubmit,
    checkTypos,
    openTypoModal,
    closeTypoModal,
    resetTypoState,
    setTypoPendingSubmit,
  };
}
