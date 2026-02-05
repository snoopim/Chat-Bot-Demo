"use client";

import type { AiResult } from "../lib/types";

export function BotBubble({ data }: { data: AiResult | null }) {
  if (!data) return null;

  return (
    <div className="mt-4 rounded-2xl border border-zinc-700 bg-zinc-900 p-4 text-zinc-100 shadow">
      {data.reason && <div className="mb-3 opacity-90">{data.reason}</div>}

      

      {data.suggested_answer_format && (
        <div>
          <div className="mb-1 text-xs opacity-70">Example you can use</div>
          <pre className="whitespace-pre-wrap rounded-xl border border-zinc-700 bg-zinc-950 p-3 text-sm">
            {data.suggested_answer_format}
          </pre>
        </div>
      )}
    </div>
  );
}
