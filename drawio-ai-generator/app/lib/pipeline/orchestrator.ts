import OpenAI from "openai";
import { DiagramSchema, PipelineResult } from "../schemas/diagram";
import { extractDiagramSchema } from "./extract";
import { layoutDiagram } from "./dagre-layout";
import { renderDiagramXml } from "./render";
import { validateSchema, repairSchema } from "./validate";

const MAX_REPAIR_ITERATIONS = 2;

export async function runPipeline(
  client: OpenAI,
  model: string,
  userPrompt: string,
  existingSchema?: DiagramSchema
): Promise<PipelineResult> {
  const warnings: string[] = [];

  // Stage 1: Extract — LLM produces DiagramSchema JSON
  let schema = await extractDiagramSchema(
    client,
    model,
    userPrompt,
    existingSchema
  );

  // Stage 4 (pre-layout validation + repair loop)
  for (let i = 0; i < MAX_REPAIR_ITERATIONS; i++) {
    const validation = validateSchema(schema);
    if (validation.valid) break;

    if (i === MAX_REPAIR_ITERATIONS - 1) {
      warnings.push(
        `Diagram has unresolved issues after ${MAX_REPAIR_ITERATIONS} repair attempts: ${validation.errors.join("; ")}`
      );
      // Try to salvage: remove bad relationships
      schema = {
        ...schema,
        relationships: schema.relationships.filter((rel) => {
          const entityIds = new Set(schema.entities.map((e) => e.id));
          return entityIds.has(rel.source) && entityIds.has(rel.target);
        }),
      };
      break;
    }

    schema = await repairSchema(client, model, schema, validation.errors);
  }

  // Stage 2: Layout — dagre positions all entities
  const positionedSchema = layoutDiagram(schema);

  // Stage 3: Render — positioned JSON → draw.io XML
  const xml = renderDiagramXml(positionedSchema);

  return {
    xml,
    schema: positionedSchema,
    warnings: warnings.length > 0 ? warnings : undefined,
  };
}
