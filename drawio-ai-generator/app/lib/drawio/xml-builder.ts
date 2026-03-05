import { DiagramSchema, Entity, Lane, Relationship } from "../schemas/diagram";

function escapeXml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function getShapeStyle(entity: Entity): string {
  const parts: string[] = [];
  const shape = entity.style?.shape || "rectangle";

  switch (shape) {
    case "ellipse":
      parts.push("ellipse");
      break;
    case "diamond":
      parts.push("rhombus");
      break;
    case "cylinder":
      parts.push("shape=cylinder3;boundedLbl=1;stencil=1;size=15");
      break;
    case "hexagon":
      parts.push("shape=hexagon;perimeter=hexagonPerimeter2;size=0.25");
      break;
    default:
      if (entity.style?.rounded !== false) {
        parts.push("rounded=1");
      }
      break;
  }

  parts.push("whiteSpace=wrap", "html=1");

  if (entity.style?.fillColor) {
    parts.push(`fillColor=${entity.style.fillColor}`);
    // Derive stroke color (darken the fill)
    parts.push(`strokeColor=${darkenColor(entity.style.fillColor)}`);
  }

  if (entity.style?.fontColor) {
    parts.push(`fontColor=${entity.style.fontColor}`);
  }

  return parts.join(";") + ";";
}

function darkenColor(hex: string): string {
  const r = Math.max(0, parseInt(hex.slice(1, 3), 16) - 40);
  const g = Math.max(0, parseInt(hex.slice(3, 5), 16) - 40);
  const b = Math.max(0, parseInt(hex.slice(5, 7), 16) - 40);
  return `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
}

function getEdgeStyle(rel: Relationship): string {
  const parts: string[] = [];

  switch (rel.style) {
    case "curved":
      parts.push("edgeStyle=elbowEdgeStyle;curved=1");
      break;
    case "straight":
      parts.push("edgeStyle=none");
      break;
    default:
      parts.push("edgeStyle=orthogonalEdgeStyle");
      break;
  }

  parts.push("rounded=1", "html=1");

  if (rel.direction === "both") {
    parts.push("startArrow=classic", "endArrow=classic");
  } else if (rel.direction === "backward") {
    parts.push("startArrow=classic", "endArrow=none");
  }

  return parts.join(";") + ";";
}

function buildLaneCell(lane: Lane, x: number, y: number, width: number, height: number): string {
  const style = `swimlane;fillColor=${lane.color};strokeColor=${darkenColor(lane.color)};fontColor=#333333;startSize=30;html=1;collapsible=0;`;
  return `    <mxCell id="${escapeXml(lane.id)}" value="${escapeXml(lane.label)}" style="${style}" vertex="1" parent="1">
      <mxGeometry x="${x}" y="${y}" width="${width}" height="${height}" as="geometry" />
    </mxCell>`;
}

function buildEntityCell(entity: Entity, parent: string = "1"): string {
  const style = getShapeStyle(entity);
  const x = entity.x ?? 0;
  const y = entity.y ?? 0;
  const width = entity.width ?? 120;
  const height = entity.height ?? 50;

  return `    <mxCell id="${escapeXml(entity.id)}" value="${escapeXml(entity.label)}" style="${style}" vertex="1" parent="${escapeXml(parent)}">
      <mxGeometry x="${x}" y="${y}" width="${width}" height="${height}" as="geometry" />
    </mxCell>`;
}

function buildEdgeCell(rel: Relationship): string {
  const style = getEdgeStyle(rel);
  const labelAttr = rel.label ? ` value="${escapeXml(rel.label)}"` : ' value=""';

  return `    <mxCell id="${escapeXml(rel.id)}"${labelAttr} style="${style}" edge="1" source="${escapeXml(rel.source)}" target="${escapeXml(rel.target)}" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>`;
}

export function buildDrawioXml(schema: DiagramSchema): string {
  const cells: string[] = [
    '    <mxCell id="0" />',
    '    <mxCell id="1" parent="0" />',
  ];

  // Build lane cells if present
  if (schema.lanes && schema.lanes.length > 0) {
    const laneEntities = new Map<string, Entity[]>();
    for (const entity of schema.entities) {
      if (entity.lane) {
        if (!laneEntities.has(entity.lane)) {
          laneEntities.set(entity.lane, []);
        }
        laneEntities.get(entity.lane)!.push(entity);
      }
    }

    for (const lane of schema.lanes) {
      const entities = laneEntities.get(lane.id) || [];
      if (entities.length === 0) {
        cells.push(buildLaneCell(lane, 0, lane.order * 200, 800, 180));
        continue;
      }

      // Compute lane bounds from its entities
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      for (const e of entities) {
        minX = Math.min(minX, e.x ?? 0);
        minY = Math.min(minY, e.y ?? 0);
        maxX = Math.max(maxX, (e.x ?? 0) + (e.width ?? 120));
        maxY = Math.max(maxY, (e.y ?? 0) + (e.height ?? 50));
      }

      const padding = 30;
      const headerHeight = 30;
      const laneX = minX - padding;
      const laneY = minY - padding - headerHeight;
      const laneWidth = maxX - minX + padding * 2;
      const laneHeight = maxY - minY + padding * 2 + headerHeight;

      cells.push(buildLaneCell(lane, laneX, laneY, laneWidth, laneHeight));

      // Add entities with relative position inside the lane
      for (const entity of entities) {
        const relEntity = {
          ...entity,
          x: (entity.x ?? 0) - laneX,
          y: (entity.y ?? 0) - laneY,
        };
        cells.push(buildEntityCell(relEntity, lane.id));
      }
    }

    // Add entities not in any lane
    for (const entity of schema.entities) {
      if (!entity.lane) {
        cells.push(buildEntityCell(entity));
      }
    }
  } else {
    // No lanes — add all entities directly
    for (const entity of schema.entities) {
      cells.push(buildEntityCell(entity));
    }
  }

  // Add edges
  for (const rel of schema.relationships) {
    cells.push(buildEdgeCell(rel));
  }

  return `<mxGraphModel dx="1422" dy="762" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827">
  <root>
${cells.join("\n")}
  </root>
</mxGraphModel>`;
}

export function wrapInMxFile(xml: string): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<mxfile version="1.0">
  <diagram name="Page-1">
    ${xml}
  </diagram>
</mxfile>`;
}
