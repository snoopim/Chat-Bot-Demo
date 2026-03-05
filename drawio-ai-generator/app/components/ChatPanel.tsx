"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Send, Loader2 } from "lucide-react";
import { useDiagramStore } from "../stores/diagram-store";
import MessageBubble from "./MessageBubble";
import ModelSelector from "./ModelSelector";
import ApiKeyInput from "./ApiKeyInput";

export default function ChatPanel() {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const {
    messages,
    addMessage,
    isGenerating,
    setIsGenerating,
    setError,
    setXml,
    currentXml,
    apiKey,
    selectedModel,
    error,
  } = useDiagramStore();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async () => {
    const trimmed = input.trim();
    if (!trimmed || isGenerating) return;

    if (!apiKey) {
      setError("Please enter your OpenAI API key first.");
      return;
    }

    setInput("");
    addMessage({ role: "user", content: trimmed });
    setIsGenerating(true);
    setError(null);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: trimmed,
          existingXml: currentXml || undefined,
          model: selectedModel,
          apiKey,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Generation failed");
      }

      setXml(data.xml, data.schema);

      let assistantMsg = "Diagram generated successfully.";
      if (data.schema?.title) {
        assistantMsg = `Created: **${data.schema.title}** — ${data.schema.entities?.length || 0} entities, ${data.schema.relationships?.length || 0} connections.`;
      }
      if (data.warnings?.length) {
        assistantMsg += `\n\nWarnings: ${data.warnings.join("; ")}`;
      }

      addMessage({ role: "assistant", content: assistantMsg });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Something went wrong";
      setError(message);
      addMessage({ role: "assistant", content: `Error: ${message}` });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="px-4 py-3 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold">AI Chat</h2>
          <ModelSelector />
        </div>
        <ApiKeyInput />
      </div>

      <Separator />

      {/* Messages */}
      <ScrollArea className="flex-1 px-4 py-4">
        {messages.length === 0 && (
          <div className="flex h-full min-h-[200px] items-center justify-center">
            <div className="text-center space-y-2">
              <p className="text-sm text-muted-foreground">
                Describe the diagram you want to create
              </p>
              <p className="text-xs text-muted-foreground/60">
                e.g. &quot;Create a flowchart for user authentication&quot;
              </p>
            </div>
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isGenerating && (
          <div className="flex items-center gap-2 mb-4 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Generating diagram...
          </div>
        )}
        {error && !isGenerating && (
          <div className="mb-4 rounded-lg bg-destructive/10 px-4 py-2 text-sm text-destructive">
            {error}
          </div>
        )}
        <div ref={messagesEndRef} />
      </ScrollArea>

      <Separator />

      {/* Input */}
      <div className="p-4">
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your diagram..."
            rows={2}
            className="resize-none text-sm"
            disabled={isGenerating}
          />
          <Button
            size="icon"
            onClick={handleSubmit}
            disabled={isGenerating || !input.trim()}
            className="self-end shrink-0"
          >
            {isGenerating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
