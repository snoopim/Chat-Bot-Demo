"use client";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Undo2, Redo2, RotateCcw, Download, FileCode2 } from "lucide-react";
import { useDiagramStore } from "../stores/diagram-store";
import { wrapInMxFile } from "../lib/drawio/xml-builder";

interface ToolbarProps {
  showXml: boolean;
  onToggleXml: () => void;
}

export default function Toolbar({ showXml, onToggleXml }: ToolbarProps) {
  const { currentXml, xmlHistory, historyIndex, undo, redo, resetDiagram } =
    useDiagramStore();

  const canUndo = historyIndex > 0;
  const canRedo = historyIndex < xmlHistory.length - 1;

  const handleExport = () => {
    if (!currentXml) return;
    const content = wrapInMxFile(currentXml);
    const blob = new Blob([content], { type: "application/xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "diagram.drawio";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex items-center gap-1 border-b px-3 py-2">
      <span className="mr-auto text-sm font-semibold">Diagram</span>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={undo}
            disabled={!canUndo}
          >
            <Undo2 className="h-4 w-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Undo (Ctrl+Z)</TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={redo}
            disabled={!canRedo}
          >
            <Redo2 className="h-4 w-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Redo (Ctrl+Shift+Z)</TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant={showXml ? "default" : "ghost"}
            size="icon"
            className="h-8 w-8"
            onClick={onToggleXml}
          >
            <FileCode2 className="h-4 w-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Toggle XML Editor</TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={resetDiagram}
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Reset</TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="secondary"
            size="sm"
            className="h-8 text-xs ml-1"
            onClick={handleExport}
            disabled={!currentXml}
          >
            <Download className="h-3.5 w-3.5 mr-1" />
            Export
          </Button>
        </TooltipTrigger>
        <TooltipContent>Download as .drawio</TooltipContent>
      </Tooltip>
    </div>
  );
}
