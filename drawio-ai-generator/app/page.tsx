"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useState } from "react";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { useDiagramStore } from "./stores/diagram-store";
import ChatPanel from "./components/ChatPanel";
import Toolbar from "./components/Toolbar";
import XmlEditor from "./components/XmlEditor";

const DiagramPreview = dynamic(
  () => import("./components/DiagramPreview"),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full items-center justify-center text-muted-foreground text-sm">
        Loading diagram editor...
      </div>
    ),
  }
);

export default function Home() {
  const [showXml, setShowXml] = useState(false);
  const { undo, redo } = useDiagramStore();

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "z") {
        if (e.shiftKey) {
          e.preventDefault();
          redo();
        } else {
          e.preventDefault();
          undo();
        }
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [undo, redo]);

  const toggleXml = useCallback(() => setShowXml((v) => !v), []);

  return (
    <main className="h-screen w-screen overflow-hidden">
      <ResizablePanelGroup orientation="horizontal">
        {/* Left panel: Diagram */}
        <ResizablePanel defaultSize={60} minSize={30}>
          <div className="flex h-full flex-col">
            <Toolbar showXml={showXml} onToggleXml={toggleXml} />
            <div className="relative flex-1">
              {showXml ? <XmlEditor /> : <DiagramPreview />}
            </div>
          </div>
        </ResizablePanel>

        <ResizableHandle withHandle />

        {/* Right panel: Chat */}
        <ResizablePanel defaultSize={40} minSize={25}>
          <ChatPanel />
        </ResizablePanel>
      </ResizablePanelGroup>
    </main>
  );
}
