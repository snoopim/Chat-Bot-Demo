import { DiagramSchema, Entity, EntityStyle, Lane, Relationship } from "../schemas/diagram";

/**
 * Parse draw.io XML back into a DiagramSchema.
 * Used for the edit round-trip: existing XML → JSON → LLM merge → re-layout → re-render
 */
export function parseDrawioXml(xml: string): DiagramSchema | null {
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xml, "text/xml");

    const root = doc.querySelector("root");
    if (!root) return null;

    const cells = root.querySelectorAll("mxCell");
    const entities: Entity[] = [];
    const relationships: Relationship[] = [];
    const lanes: Lane[] = [];
    let laneOrder = 0;

    cells.forEach((cell) => {
      const id = cell.getAttribute("id");
      if (!id || id === "0" || id === "1") return;

      const value = cell.getAttribute("value") || "";
      const style = cell.getAttribute("style") || "";
      const isVertex = cell.getAttribute("vertex") === "1";
      const isEdge = cell.getAttribute("edge") === "1";

      if (isEdge) {
        const source = cell.getAttribute("source") || "";
        const target = cell.getAttribute("target") || "";
        relationships.push({
          id,
          source,
          target,
          label: value || undefined,
          style: style.includes("curved")
            ? "curved"
            : style.includes("none")
              ? "straight"
              : "orthogonal",
        });
      } else if (isVertex) {
        const geo = cell.querySelector("mxGeometry");
        const x = parseFloat(geo?.getAttribute("x") || "0");
        const y = parseFloat(geo?.getAttribute("y") || "0");
        const width = parseFloat(geo?.getAttribute("width") || "120");
        const height = parseFloat(geo?.getAttribute("height") || "50");

        if (style.includes("swimlane")) {
          const colorMatch = style.match(/fillColor=([^;]+)/);
          lanes.push({
            id,
            label: value,
            color: colorMatch?.[1] || "#E6F3FF",
            order: laneOrder++,
          });
        } else {
          const parent = cell.getAttribute("parent") || "1";
          const fillMatch = style.match(/fillColor=([^;]+)/);
          const fontMatch = style.match(/fontColor=([^;]+)/);

          let shape: EntityStyle["shape"] = "rectangle";
          if (style.includes("ellipse")) shape = "ellipse";
          else if (style.includes("rhombus")) shape = "diamond";
          else if (style.includes("cylinder")) shape = "cylinder";
          else if (style.includes("hexagon")) shape = "hexagon";

          entities.push({
            id,
            label: value,
            lane: parent !== "1" ? parent : undefined,
            x,
            y,
            width,
            height,
            style: {
              fillColor: fillMatch?.[1] || "#FFFFFF",
              fontColor: fontMatch?.[1],
              rounded: style.includes("rounded=1"),
              shape,
            },
          });
        }
      }
    });

    return {
      title: "Parsed Diagram",
      lanes: lanes.length > 0 ? lanes : undefined,
      entities,
      relationships,
    };
  } catch {
    return null;
  }
}
