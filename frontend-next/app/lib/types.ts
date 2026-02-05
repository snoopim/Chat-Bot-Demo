// app/lib/types.ts

export type FlowQuestion = {
    key: string;
    text: string;
    required?: boolean;
  };
  
  export type ProcessFlow = {
    id: number;
    name: string;
    description: string;
    status: "not_completed" | "in_progress" | "completed";
    created_at: string;
    updated_at: string;
  };
  
  export type Progress = {
    status: "not_completed" | "in_progress" | "completed";
    total: number;
    answered: number;
    skipped: number;
    unanswered: number;
    percent: number;
    remaining_keys: string[];
    next_recommended_key: string | null;
  };
  
  export type AiResult = {
    is_clear: boolean;
    score: number;
    reason: string;
    follow_up_question: string;
    suggested_answer_format: string;
  };

  export type FlowAnswer = {
    question_key: string;
    status: "unanswered" | "skipped" | "answered";
    answer_text?: string | null;
  };

  export type TypoCheckResult = {
    has_typo: boolean;
    suggested_text?: string;
    fixed_text?: string;
  };
  