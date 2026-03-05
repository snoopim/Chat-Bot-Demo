import OpenAI from "openai";
import { DiagramSchema } from "../schemas/diagram";
import { chatCompletion } from "../openai-client";
import {
  EXTRACT_SYSTEM_PROMPT,
  EXTRACT_EDIT_CONTEXT,
} from "../prompts/extract-system";

export async function extractDiagramSchema(
  client: OpenAI,
  model: string,
  userPrompt: string,
  existingSchema?: DiagramSchema
): Promise<DiagramSchema> {
  let systemPrompt = EXTRACT_SYSTEM_PROMPT;

  if (existingSchema) {
    systemPrompt +=
      "\n\n" + EXTRACT_EDIT_CONTEXT + JSON.stringify(existingSchema, null, 2);
  }

  const response = await chatCompletion(
    client,
    model,
    systemPrompt,
    userPrompt,
    true
  );

  const parsed = JSON.parse(response) as DiagramSchema;

  // Basic validation
  if (!parsed.entities || !Array.isArray(parsed.entities)) {
    throw new Error("LLM output missing entities array");
  }
  if (!parsed.relationships) {
    parsed.relationships = [];
  }
  if (!parsed.title) {
    parsed.title = "Untitled Diagram";
  }

  return parsed;
}
