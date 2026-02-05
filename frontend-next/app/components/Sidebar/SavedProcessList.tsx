"use client";

import type { ProcessFlow } from "../../lib/types";
import { ProcessItem } from "./ProcessItem";

type SavedProcessListProps = {
  flows: ProcessFlow[];
  currentFlowId: number | null;
  onResume: (f: ProcessFlow) => void;
  onExportRopa: (id: number) => void;
  onExportDocx: (id: number) => void;
};

export function SavedProcessList({
  flows,
  currentFlowId,
  onResume,
  onExportRopa,
  onExportDocx,
}: SavedProcessListProps) {
  return (
    <div className="mt-4">
      <div className="text-xs font-bold text-zinc-300 mb-2">Your saved processes</div>

      <div className="space-y-2">
        {flows.map((f) => (
          <ProcessItem
            key={f.id}
            process={f}
            isActive={currentFlowId === f.id}
            onResume={onResume}
            onExportRopa={onExportRopa}
            onExportDocx={onExportDocx}
          />
        ))}

        {flows.length === 0 && (
          <div className="text-sm text-zinc-500 border border-zinc-900 rounded-2xl p-3 bg-zinc-950">
            No processes yet. Create one below.
          </div>
        )}
      </div>
    </div>
  );
}
