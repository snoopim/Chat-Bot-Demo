"use client";

import type { ProcessFlow, Progress } from "../../lib/types";
import { SavedProcessList } from "./SavedProcessList";
import { CreateProcessSection } from "./CreateProcessSection";
import { ProgressPanel } from "./ProgressPanel";

type SidebarProps = {
  flows: ProcessFlow[];
  flow: ProcessFlow | null;
  progress: Progress | null;
  processName: string;
  customName: string;
  loadingStart: boolean;
  skippedCount: number;
  onResume: (f: ProcessFlow) => void;
  onExportRopa: (id: number) => void;
  onExportDocx: (id: number) => void;
  onSelectProcess: (name: string) => void;
  onCustomNameChange: (value: string) => void;
  onUseCustomName: () => void;
  onStartRopa: () => void;
  onContinueSkipped: () => void;
};

export function Sidebar({
  flows,
  flow,
  progress,
  processName,
  customName,
  loadingStart,
  skippedCount,
  onResume,
  onExportRopa,
  onExportDocx,
  onSelectProcess,
  onCustomNameChange,
  onUseCustomName,
  onStartRopa,
  onContinueSkipped,
}: SidebarProps) {
  return (
    <aside className="w-95 border-r border-zinc-800 p-4 overflow-y-auto">
      <h2 className="text-lg font-semibold">RoPA processes</h2>
      <p className="text-sm text-zinc-400 mt-1">
        Pick a process, answer any order, skip and return later.
      </p>

      <SavedProcessList
        flows={flows}
        currentFlowId={flow?.id ?? null}
        onResume={onResume}
        onExportRopa={onExportRopa}
        onExportDocx={onExportDocx}
      />

      <CreateProcessSection
        processName={processName}
        customName={customName}
        flow={flow}
        loadingStart={loadingStart}
        onSelectProcess={onSelectProcess}
        onCustomNameChange={onCustomNameChange}
        onUseCustomName={onUseCustomName}
        onStartRopa={onStartRopa}
      />

      {flow && progress && (
        <ProgressPanel
          flow={flow}
          progress={progress}
          skippedCount={skippedCount}
          onContinueSkipped={onContinueSkipped}
        />
      )}
    </aside>
  );
}
