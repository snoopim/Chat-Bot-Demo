import { create } from "zustand";
import { DiagramSchema, ChatMessage } from "../lib/schemas/diagram";

interface DiagramStore {
  // Diagram state
  currentSchema: DiagramSchema | null;
  currentXml: string;
  xmlHistory: string[];
  historyIndex: number;

  // Chat state
  messages: ChatMessage[];

  // Config
  apiKey: string;
  selectedModel: string;
  availableModels: string[];

  // UI state
  isGenerating: boolean;
  error: string | null;

  // Actions
  setXml: (xml: string, schema?: DiagramSchema) => void;
  undo: () => void;
  redo: () => void;
  resetDiagram: () => void;
  addMessage: (message: Omit<ChatMessage, "id" | "timestamp">) => void;
  clearMessages: () => void;
  setApiKey: (key: string) => void;
  setSelectedModel: (model: string) => void;
  setAvailableModels: (models: string[]) => void;
  setIsGenerating: (v: boolean) => void;
  setError: (error: string | null) => void;
}

let messageCounter = 0;

export const useDiagramStore = create<DiagramStore>((set, get) => ({
  currentSchema: null,
  currentXml: "",
  xmlHistory: [""],
  historyIndex: 0,

  messages: [],

  apiKey: "",
  selectedModel: "gpt-4.1-mini",
  availableModels: [],

  isGenerating: false,
  error: null,

  setXml: (xml, schema) => {
    const { xmlHistory, historyIndex } = get();
    const truncated = xmlHistory.slice(0, historyIndex + 1);
    const newHistory = [...truncated, xml];
    if (newHistory.length > 50) newHistory.shift();
    set({
      currentXml: xml,
      currentSchema: schema ?? get().currentSchema,
      xmlHistory: newHistory,
      historyIndex: Math.min(newHistory.length - 1, 49),
    });
  },

  undo: () => {
    const { xmlHistory, historyIndex } = get();
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      set({ currentXml: xmlHistory[newIndex], historyIndex: newIndex });
    }
  },

  redo: () => {
    const { xmlHistory, historyIndex } = get();
    if (historyIndex < xmlHistory.length - 1) {
      const newIndex = historyIndex + 1;
      set({ currentXml: xmlHistory[newIndex], historyIndex: newIndex });
    }
  },

  resetDiagram: () =>
    set({
      currentXml: "",
      currentSchema: null,
      xmlHistory: [""],
      historyIndex: 0,
    }),

  addMessage: (msg) => {
    messageCounter++;
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...msg,
          id: `msg_${messageCounter}_${Date.now()}`,
          timestamp: Date.now(),
        },
      ],
    }));
  },

  clearMessages: () => set({ messages: [] }),

  setApiKey: (key) => set({ apiKey: key }),
  setSelectedModel: (model) => set({ selectedModel: model }),
  setAvailableModels: (models) => set({ availableModels: models }),
  setIsGenerating: (v) => set({ isGenerating: v }),
  setError: (error) => set({ error }),
}));
