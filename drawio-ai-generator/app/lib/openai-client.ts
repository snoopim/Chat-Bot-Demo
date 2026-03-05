import OpenAI from "openai";

export function createOpenAIClient(apiKey: string): OpenAI {
  return new OpenAI({ apiKey });
}

export async function chatCompletion(
  client: OpenAI,
  model: string,
  systemPrompt: string,
  userPrompt: string,
  jsonMode: boolean = true
): Promise<string> {
  // o-series reasoning models don't support temperature or system role
  const isReasoningModel = /^o[0-9]/.test(model);

  const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = isReasoningModel
    ? [{ role: "user", content: `${systemPrompt}\n\n${userPrompt}` }]
    : [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ];

  const response = await client.chat.completions.create({
    model,
    messages,
    ...(jsonMode && !isReasoningModel && { response_format: { type: "json_object" } }),
    ...(!isReasoningModel && { temperature: 0.3 }),
  });

  return response.choices[0]?.message?.content ?? "";
}

export async function listModels(apiKey: string): Promise<string[]> {
  const client = createOpenAIClient(apiKey);
  const list = await client.models.list();
  const models: string[] = [];
  for await (const model of list) {
    models.push(model.id);
  }
  // Filter to chat-capable models and sort
  const chatModels = models
    .filter(
      (id) =>
        id.startsWith("gpt-") ||
        id.startsWith("o1") ||
        id.startsWith("o3") ||
        id.startsWith("o4")
    )
    .sort();
  return chatModels;
}
