"use client";

import type { AiResult, FlowQuestion, ProcessFlow } from "../../lib/types";
import { Tag } from "../Tag";
import { BotBubble } from "../BotBubble";
import { NavigationButtons } from "./NavigationButtons";

type QuestionPanelProps = {
  flow: ProcessFlow | null;
  current: FlowQuestion | null;
  visibleQuestions: FlowQuestion[];
  questionIndex: number;
  answer: string;
  ai: AiResult | null;
  submitting: boolean;
  typoOpen: boolean;
  onAnswerChange: (value: string) => void;
  onPrevious: () => void;
  onSubmit: () => void;
  onSkip: () => void;
};

export function QuestionPanel({
  flow,
  current,
  visibleQuestions,
  questionIndex,
  answer,
  ai,
  submitting,
  typoOpen,
  onAnswerChange,
  onPrevious,
  onSubmit,
  onSkip,
}: QuestionPanelProps) {
  const displayIndex = questionIndex >= 0 ? questionIndex + 1 : 0;

  return (
    <main className="flex-1 p-6 overflow-y-auto">
      <div className="max-w-3xl rounded-2xl border border-zinc-800 bg-zinc-950 p-5 shadow">
        {!flow || !current ? (
          <div className="text-zinc-300">
            Select or create a process, then start/resume to answer questions.
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between gap-3">
              <div className="text-sm text-zinc-400">
                Question <b className="text-zinc-200">{displayIndex}</b> / {visibleQuestions.length}
              </div>
              <Tag>{flow.name}</Tag>
            </div>

            <h3 className="mt-3 text-lg font-semibold">{current.text}</h3>

            <textarea
              rows={5}
              value={answer}
              onChange={(e) => onAnswerChange(e.target.value)}
              placeholder="Type your answer here..."
              className={`mt-3 w-full rounded-xl border bg-zinc-900 p-3 text-white outline-none
                ${ai && ai.is_clear === false ? "border-red-400" : "border-zinc-700"}
              `}
            />

            <NavigationButtons
              questionIndex={questionIndex}
              answer={answer}
              submitting={submitting}
              typoOpen={typoOpen}
              onPrevious={onPrevious}
              onSubmit={onSubmit}
              onSkip={onSkip}
            />

            <BotBubble data={ai} />
          </>
        )}
      </div>
    </main>
  );
}
