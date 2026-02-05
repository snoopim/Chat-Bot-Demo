"use client";

import { PROCESS_GROUPS } from "../../lib/processes";
import { Tag } from "../Tag";

type CreateProcessSectionProps = {
  processName: string;
  customName: string;
  flow: { id: number } | null;
  loadingStart: boolean;
  onSelectProcess: (name: string) => void;
  onCustomNameChange: (value: string) => void;
  onUseCustomName: () => void;
  onStartRopa: () => void;
};

export function CreateProcessSection({
  processName,
  customName,
  flow,
  loadingStart,
  onSelectProcess,
  onCustomNameChange,
  onUseCustomName,
  onStartRopa,
}: CreateProcessSectionProps) {
  return (
    <div className="mt-6">
      <div className="text-xs font-bold text-zinc-300 mb-2">Create a new process</div>

      <div className="space-y-4">
        {PROCESS_GROUPS.map((grp) => (
          <div key={grp.group}>
            <div className="text-xs font-bold text-zinc-300 mb-2">{grp.group}</div>
            <div className="space-y-2">
              {grp.items.map((p) => {
                const active = processName === p.label && !flow;
                return (
                  <button
                    key={p.label}
                    onClick={() => onSelectProcess(p.label)}
                    className={`w-full rounded-2xl border px-3 py-2 text-left flex items-center justify-between gap-3
                      ${active ? "border-zinc-600 bg-zinc-900" : "border-zinc-900 bg-zinc-950 hover:border-zinc-700"}
                    `}
                  >
                    <span className="font-medium">{p.label}</span>
                    {p.common && <Tag variant="common">Common</Tag>}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Custom name UI */}
      <div className="mt-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-3">
        <div className="text-xs font-bold text-zinc-300">Or create your own</div>
        <div className="text-xs text-zinc-500 mt-1">
          Type any process name that is not in the list.
        </div>

        <div className="mt-3 flex gap-2">
          <input
            value={customName}
            onChange={(e) => onCustomNameChange(e.target.value)}
            placeholder="e.g., Vendor onboarding, Access review..."
            className="flex-1 rounded-xl border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-white outline-none"
          />

          <button
            onClick={onUseCustomName}
            disabled={!customName.trim()}
            className={`rounded-xl px-3 py-2 text-sm font-semibold
              ${!customName.trim() ? "bg-zinc-800 text-zinc-400" : "bg-white text-black"}
            `}
          >
            Use
          </button>
        </div>
      </div>

      <button
        onClick={onStartRopa}
        disabled={!processName || loadingStart}
        className={`mt-3 w-full rounded-xl px-3 py-2 font-semibold
          ${!processName || loadingStart ? "bg-zinc-800 text-zinc-400" : "bg-white text-black"}
        `}
      >
        {loadingStart ? "Starting..." : "Start RoPA questions"}
      </button>
    </div>
  );
}
