"use client";

type TypoModalProps = {
  open: boolean;
  original: string;
  suggested: string;
  onApplyFix: () => void;
  onKeepOriginal: () => void;
};

export function TypoModal({
  open,
  original,
  suggested,
  onApplyFix,
  onKeepOriginal,
}: TypoModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
      <div className="w-full max-w-lg rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
        <div className="text-lg font-semibold">Did you mean?</div>
        <div className="mt-2 text-sm text-zinc-400">
          Apply the suggested fix or keep your original text.
        </div>

        <div className="mt-4 space-y-3">
          <div>
            <div className="text-xs text-zinc-500 mb-1">Your text</div>
            <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-3 text-sm whitespace-pre-wrap">
              {original}
            </div>
          </div>

          <div>
            <div className="text-xs text-zinc-500 mb-1">Suggested fix</div>
            <div className="rounded-xl border border-zinc-700 bg-zinc-950 p-3 text-sm whitespace-pre-wrap">
              {suggested}
            </div>
          </div>
        </div>

        <div className="mt-4 flex gap-2 justify-end">
          <button
            onClick={onKeepOriginal}
            className="rounded-xl px-4 py-2 font-semibold border border-zinc-600 text-zinc-200 hover:bg-zinc-900"
          >
            Keep my text
          </button>

          <button
            onClick={onApplyFix}
            className="rounded-xl px-4 py-2 font-semibold bg-white text-black"
          >
            Apply fix
          </button>
        </div>
      </div>
    </div>
  );
}
