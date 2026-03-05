import dagre from "@dagrejs/dagre";
import { DiagramSchema, Entity } from "../schemas/diagram";

const NODE_WIDTH_PER_CHAR = 10;
const NODE_MIN_WIDTH = 120;
const NODE_MAX_WIDTH = 250;
const NODE_HEIGHT = 50;
const LANE_HEADER_HEIGHT = 40;
const LANE_PADDING = 30;
const LANE_GAP = 20;

function estimateNodeSize(label: string): { width: number; height: number } {
  const width = Math.min(
    NODE_MAX_WIDTH,
    Math.max(NODE_MIN_WIDTH, label.length * NODE_WIDTH_PER_CHAR + 40)
  );
  return { width, height: NODE_HEIGHT };
}

export function layoutDiagram(schema: DiagramSchema): DiagramSchema {
  const g = new dagre.graphlib.Graph({ compound: true });
  g.setGraph({
    rankdir: "TB",
    nodesep: 60,
    ranksep: 80,
    marginx: 40,
    marginy: 40,
  });
  g.setDefaultEdgeLabel(() => ({}));

  // Add nodes
  for (const entity of schema.entities) {
    const size = estimateNodeSize(entity.label);
    g.setNode(entity.id, {
      label: entity.label,
      width: size.width,
      height: size.height,
    });
  }

  // Add edges
  for (const rel of schema.relationships) {
    if (g.hasNode(rel.source) && g.hasNode(rel.target)) {
      g.setEdge(rel.source, rel.target, { label: rel.label || "" });
    }
  }

  // Run dagre layout
  dagre.layout(g);

  // Extract positions back to entities
  const positionedEntities: Entity[] = schema.entities.map((entity) => {
    const node = g.node(entity.id);
    if (node) {
      return {
        ...entity,
        x: Math.round(node.x - node.width / 2),
        y: Math.round(node.y - node.height / 2),
        width: Math.round(node.width),
        height: Math.round(node.height),
      };
    }
    return entity;
  });

  // If lanes exist, offset entities into their lanes
  if (schema.lanes && schema.lanes.length > 0) {
    return layoutWithLanes(schema, positionedEntities);
  }

  return {
    ...schema,
    entities: positionedEntities,
  };
}

function layoutWithLanes(
  schema: DiagramSchema,
  positionedEntities: Entity[]
): DiagramSchema {
  const lanes = [...(schema.lanes || [])].sort((a, b) => a.order - b.order);
  const laneEntityMap = new Map<string, Entity[]>();

  // Group entities by lane
  for (const entity of positionedEntities) {
    const laneId = entity.lane || "__no_lane__";
    if (!laneEntityMap.has(laneId)) {
      laneEntityMap.set(laneId, []);
    }
    laneEntityMap.get(laneId)!.push(entity);
  }

  let currentY = 0;
  const adjustedEntities: Entity[] = [];

  for (const lane of lanes) {
    const laneEntities = laneEntityMap.get(lane.id) || [];
    if (laneEntities.length === 0) {
      currentY += LANE_HEADER_HEIGHT + LANE_PADDING * 2 + LANE_GAP;
      continue;
    }

    // Find bounding box of entities in this lane
    let minY = Infinity;
    let maxY = -Infinity;
    for (const e of laneEntities) {
      if (e.y !== undefined && e.height !== undefined) {
        minY = Math.min(minY, e.y);
        maxY = Math.max(maxY, e.y + e.height);
      }
    }

    const yOffset = currentY + LANE_HEADER_HEIGHT + LANE_PADDING - minY;

    for (const entity of laneEntities) {
      adjustedEntities.push({
        ...entity,
        y: (entity.y || 0) + yOffset,
      });
    }

    const laneHeight = maxY - minY + LANE_HEADER_HEIGHT + LANE_PADDING * 2;
    currentY += laneHeight + LANE_GAP;
  }

  // Add entities without lanes
  const noLaneEntities = laneEntityMap.get("__no_lane__") || [];
  for (const entity of noLaneEntities) {
    adjustedEntities.push({
      ...entity,
      y: (entity.y || 0) + currentY,
    });
  }

  return {
    ...schema,
    entities: adjustedEntities,
  };
}
