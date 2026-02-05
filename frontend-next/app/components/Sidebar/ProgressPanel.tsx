"use client";

import type { ProcessFlow, Progress } from "../../lib/types";
import { Tag } from "../Tag";

type ProgressPanelProps = {
  flow: ProcessFlow;
  progress: Progress;
  skippedCount: number;
  onContinueSkipped: () => void;
};

function statusBadge(s: string) {
  if (s === "completed") return <Tag variant="status">Completed</Tag>;
  if (s === "in_progress") return <Tag variant="status">In progress</Tag>;
  return <Tag variant="status">Not completed</Tag>;
}

export function ProgressPanel({
  flow,
  progress,
  skippedCount,
  onContinueSkipped,
}: ProgressPanelProps) {
  return (
    <div className="mt-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-3">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold">{flow.name}</div>
        {statusBadge(progress.status)}
      </div>

      <div className="mt-2 text-xs text-zinc-400">
        Answered: {progress.answered}/{progress.total} | Skipped: {progress.skipped}
      </div>

      <div className="mt-2 h-2 w-full rounded-full bg-zinc-800 overflow-hidden">
        <div className="h-2 bg-white" style={{ width: `${progress.percent}%` }} />
      </div>
      <div className="mt-1 text-xs text-zinc-400">{progress.percent}% complete</div>

      <button
        onClick={onContinueSkipped}
        disabled={skippedCount === 0}
        className={`mt-3 w-full rounded-xl px-3 py-2 font-semibold border
          ${
            skippedCount === 0
              ? "border-zinc-800 text-zinc-500"
              : "border-zinc-600 text-zinc-200 hover:bg-zinc-900"
          }
        `}
      >
        Continue skipped ({skippedCount})
      </button>
    </div>
  );
}
