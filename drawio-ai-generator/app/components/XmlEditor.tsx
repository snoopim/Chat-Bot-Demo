"use client";

import { useEffect, useRef, useState } from "react";
import { useDiagramStore } from "../stores/diagram-store";

export default function XmlEditor() {
  const { currentXml, setXml } = useDiagramStore();
  const [draft, setDraft] = useState(currentXml);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setDraft(currentXml);
    setError(null);
  }, [currentXml]);

  const handleChange = (value: string) => {
    setDraft(value);

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      if (
        value.includes("<mxGraphModel") &&
        value.includes("</mxGraphModel>")
      ) {
        setError(null);
        setXml(value);
      } else if (value.trim()) {
        setError("Invalid mxGraphModel XML");
      }
    }, 800);
  };

  return (
    <div className="flex h-full flex-col">
      {error && (
        <div className="bg-destructive/10 px-3 py-1.5 text-xs text-destructive">
          {error}
        </div>
      )}
      <textarea
        value={draft}
        onChange={(e) => handleChange(e.target.value)}
        spellCheck={false}
        className="flex-1 resize-none bg-zinc-950 p-4 font-mono text-xs leading-relaxed text-green-400 focus:outline-none"
      />
    </div>
  );
}
