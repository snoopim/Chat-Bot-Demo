"use client";

import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { KeyRound, Eye, EyeOff, Check } from "lucide-react";
import { useDiagramStore } from "../stores/diagram-store";

export default function ApiKeyInput() {
  const { apiKey, setApiKey, setAvailableModels } = useDiagramStore();
  const [draft, setDraft] = useState(apiKey);
  const [showKey, setShowKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem("openai_api_key");
    if (stored) {
      setDraft(stored);
      setApiKey(stored);
      fetchModels(stored);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function fetchModels(key: string) {
    try {
      setLoading(true);
      const res = await fetch("/api/models", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ apiKey: key }),
      });
      const data = await res.json();
      if (data.models) {
        setAvailableModels(data.models);
      }
    } catch {
      // silently fail — user can still manually type models
    } finally {
      setLoading(false);
    }
  }

  const handleSave = async () => {
    const trimmed = draft.trim();
    setApiKey(trimmed);
    localStorage.setItem("openai_api_key", trimmed);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    if (trimmed) {
      await fetchModels(trimmed);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <KeyRound className="h-4 w-4 text-muted-foreground shrink-0" />
      <div className="relative flex-1">
        <Input
          type={showKey ? "text" : "password"}
          placeholder="OpenAI API Key"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSave()}
          className="pr-8 h-8 text-xs"
        />
        <button
          type="button"
          onClick={() => setShowKey(!showKey)}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
        >
          {showKey ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
        </button>
      </div>
      <Button
        size="sm"
        variant={saved ? "default" : "secondary"}
        onClick={handleSave}
        disabled={loading || !draft.trim()}
        className="h-8 text-xs"
      >
        {loading ? "..." : saved ? <Check className="h-3.5 w-3.5" /> : "Save"}
      </Button>
    </div>
  );
}
