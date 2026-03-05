import { NextResponse } from "next/server";
import { createOpenAIClient } from "../../lib/openai-client";
import { runPipeline } from "../../lib/pipeline/orchestrator";
import { parseDrawioXml } from "../../lib/drawio/xml-parser";

export async function POST(req: Request) {
  try {
    const { prompt, existingXml, model, apiKey } = await req.json();

    if (!apiKey) {
      return NextResponse.json(
        { error: "API key is required" },
        { status: 400 }
      );
    }

    if (!prompt) {
      return NextResponse.json(
        { error: "Prompt is required" },
        { status: 400 }
      );
    }

    const client = createOpenAIClient(apiKey);
    const selectedModel = model || "gpt-4.1-mini";

    // Parse existing XML to schema for edit context
    let existingSchema = undefined;
    if (existingXml) {
      existingSchema = parseDrawioXml(existingXml) ?? undefined;
    }

    const result = await runPipeline(
      client,
      selectedModel,
      prompt,
      existingSchema
    );

    return NextResponse.json(result);
  } catch (err: unknown) {
    const message =
      err instanceof Error ? err.message : "Pipeline failed";

    // Check for OpenAI-specific errors
    if (message.includes("Incorrect API key") || message.includes("401")) {
      return NextResponse.json(
        { error: "Invalid API key. Please check your OpenAI API key." },
        { status: 401 }
      );
    }

    return NextResponse.json({ error: message }, { status: 500 });
  }
}
