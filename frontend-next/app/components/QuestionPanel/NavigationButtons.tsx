"use client";

type NavigationButtonsProps = {
  questionIndex: number;
  answer: string;
  submitting: boolean;
  typoOpen: boolean;
  onPrevious: () => void;
  onSubmit: () => void;
  onSkip: () => void;
};

export function NavigationButtons({
  questionIndex,
  answer,
  submitting,
  typoOpen,
  onPrevious,
  onSubmit,
  onSkip,
}: NavigationButtonsProps) {
  return (
    <div className="mt-3 flex flex-wrap gap-2">
      <button
        disabled={questionIndex <= 0}
        onClick={onPrevious}
        className={`rounded-xl px-4 py-2 font-semibold border
          ${
            questionIndex <= 0
              ? "border-zinc-800 text-zinc-500"
              : "border-zinc-600 text-zinc-200 hover:bg-zinc-900"
          }
        `}
      >
        Previous
      </button>

      <button
        disabled={!answer.trim() || submitting || typoOpen}
        onClick={onSubmit}
        className={`rounded-xl px-4 py-2 font-semibold
          ${
            !answer.trim() || submitting || typoOpen
              ? "bg-zinc-800 text-zinc-400"
              : "bg-white text-black"
          }
        `}
      >
        {submitting ? "Saving..." : "Submit answer"}
      </button>

      <button
        disabled={submitting || typoOpen}
        onClick={onSkip}
        className={`rounded-xl px-4 py-2 font-semibold border
          ${
            submitting || typoOpen
              ? "border-zinc-800 text-zinc-500"
              : "border-zinc-600 text-zinc-200 hover:bg-zinc-900"
          }
        `}
      >
        Skip for now
      </button>
    </div>
  );
}
