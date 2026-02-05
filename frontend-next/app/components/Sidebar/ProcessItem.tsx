"use client";

import type { ProcessFlow } from "../../lib/types";
import { Tag } from "../Tag";

type ProcessItemProps = {
  process: ProcessFlow;
  isActive: boolean;
  onResume: (f: ProcessFlow) => void;
  onExportRopa: (id: number) => void;
  onExportDocx: (id: number) => void;
};

function statusBadge(s: string) {
  if (s === "completed") return <Tag variant="status">Completed</Tag>;
  if (s === "in_progress") return <Tag variant="status">In progress</Tag>;
  return <Tag variant="status">Not completed</Tag>;
}

export function ProcessItem({
  process,
  isActive,
  onResume,
  onExportRopa,
  onExportDocx,
}: ProcessItemProps) {
  const isCompleted = process.status === "completed";

  return (
    <div
      className={`w-full rounded-2xl border px-3 py-2 flex items-center justify-between gap-3
        ${isActive ? "border-zinc-600 bg-zinc-900" : "border-zinc-900 bg-zinc-950 hover:border-zinc-700"}
      `}
    >
      <button onClick={() => onResume(process)} className="flex-1 text-left">
        <div className="font-medium">{process.name}</div>
        <div className="text-xs text-zinc-500">
          Updated: {new Date(process.updated_at).toLocaleString()}
        </div>
      </button>

      <div className="flex flex-col items-end gap-2">
        {statusBadge(process.status)}

        {isCompleted && (
          <div className="flex flex-col gap-2 w-45">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onExportRopa(process.id);
              }}
              className="w-full rounded-xl px-3 py-2 text-xs font-semibold bg-white text-black"
            >
              Export RoPA (Excel)
            </button>

            <button
              onClick={(e) => {
                e.stopPropagation();
                onExportDocx(process.id);
              }}
              className="w-full rounded-xl px-3 py-2 text-xs font-semibold border border-zinc-600 text-zinc-200 hover:bg-zinc-900"
            >
              Export Process Flow (DOCX)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
