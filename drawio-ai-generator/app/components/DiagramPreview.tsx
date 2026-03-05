"use client";

import { useEffect, useRef } from "react";
import { DrawIoEmbed, DrawIoEmbedRef } from "react-drawio";
import { useDiagramStore } from "../stores/diagram-store";

export default function DiagramPreview() {
  const drawioRef = useRef<DrawIoEmbedRef>(null);
  const { currentXml } = useDiagramStore();
  const prevXmlRef = useRef("");

  useEffect(() => {
    if (currentXml && currentXml !== prevXmlRef.current && drawioRef.current) {
      prevXmlRef.current = currentXml;
      // Load XML into draw.io iframe
      const action = {
        action: "load",
        xml: currentXml,
        autosave: 0,
      };
      // Access the iframe and post the message
      const iframe = document.querySelector<HTMLIFrameElement>(
        'iframe[src*="embed.diagrams.net"]'
      );
      if (iframe?.contentWindow) {
        iframe.contentWindow.postMessage(JSON.stringify(action), "*");
      }
    }
  }, [currentXml]);

  return (
    <div className="h-full w-full">
      <DrawIoEmbed
        ref={drawioRef}
        xml={currentXml || undefined}
        configuration={{
          defaultFonts: [],
        }}
        urlParameters={{
          spin: true,
          libraries: true,
          saveAndExit: false,
          noSaveBtn: true,
          noExitBtn: true,
        }}
      />
    </div>
  );
}
