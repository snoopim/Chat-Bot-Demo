"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useDiagramStore } from "../stores/diagram-store";

const FALLBACK_MODELS = [
  "gpt-5",
  "gpt-5-mini",
  "gpt-5-nano",
  "gpt-4.1",
  "gpt-4.1-mini",
  "gpt-4.1-nano",
  "gpt-4o",
  "gpt-4o-mini",
  "gpt-4.5-preview",
  "gpt-4-turbo",
  "gpt-4",
  "gpt-3.5-turbo",
  "o4-mini",
  "o3",
  "o3-mini",
  "o3-pro",
  "o1",
  "o1-mini",
  "o1-preview",
];

export default function ModelSelector() {
  const { selectedModel, setSelectedModel, availableModels } =
    useDiagramStore();

  const models =
    availableModels.length > 0 ? availableModels : FALLBACK_MODELS;

  return (
    <Select value={selectedModel} onValueChange={setSelectedModel}>
      <SelectTrigger className="h-8 text-xs w-[180px]">
        <SelectValue placeholder="Select model" />
      </SelectTrigger>
      <SelectContent>
        {models.map((model) => (
          <SelectItem key={model} value={model} className="text-xs">
            {model}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
