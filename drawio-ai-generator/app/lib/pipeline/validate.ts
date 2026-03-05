import OpenAI from "openai";
import { DiagramSchema } from "../schemas/diagram";
import { chatCompletion } from "../openai-client";
import { REPAIR_SYSTEM_PROMPT } from "../prompts/repair-system";

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export function validateSchema(schema: DiagramSchema): ValidationResult {
  const errors: string[] = [];
  const entityIds = new Set(schema.entities.map((e) => e.id));

  // Check for duplicate entity IDs
  if (entityIds.size !== schema.entities.length) {
    errors.push("Duplicate entity IDs found");
  }

  // Check relationship references
  for (const rel of schema.relationships) {
    if (!entityIds.has(rel.source)) {
      errors.push(
        `Relationship "${rel.id}" references non-existent source "${rel.source}"`
      );
    }
    if (!entityIds.has(rel.target)) {
      errors.push(
        `Relationship "${rel.id}" references non-existent target "${rel.target}"`
      );
    }
  }

  // Check lane references
  if (schema.lanes && schema.lanes.length > 0) {
    const laneIds = new Set(schema.lanes.map((l) => l.id));
    for (const entity of schema.entities) {
      if (entity.lane && !laneIds.has(entity.lane)) {
        errors.push(
          `Entity "${entity.id}" references non-existent lane "${entity.lane}"`
        );
      }
    }
  }

  // Check for empty entities
  if (schema.entities.length === 0) {
    errors.push("Diagram has no entities");
  }

  // Check duplicate relationship IDs
  const relIds = new Set<string>();
  for (const rel of schema.relationships) {
    if (relIds.has(rel.id)) {
      errors.push(`Duplicate relationship ID "${rel.id}"`);
    }
    relIds.add(rel.id);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

export async function repairSchema(
  client: OpenAI,
  model: string,
  schema: DiagramSchema,
  errors: string[]
): Promise<DiagramSchema> {
  const userPrompt = `Fix this DiagramSchema JSON. Errors found:\n${errors.map((e) => `- ${e}`).join("\n")}\n\nCurrent JSON:\n${JSON.stringify(schema, null, 2)}`;

  const response = await chatCompletion(
    client,
    model,
    REPAIR_SYSTEM_PROMPT,
    userPrompt,
    true
  );

  return JSON.parse(response) as DiagramSchema;
}
