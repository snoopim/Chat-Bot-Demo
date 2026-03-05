export interface DiagramSchema {
  title: string;
  lanes?: Lane[];
  entities: Entity[];
  relationships: Relationship[];
}

export interface Lane {
  id: string;
  label: string;
  color: string;
  order: number;
}

export interface Entity {
  id: string;
  label: string;
  lane?: string;
  style?: EntityStyle;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
}

export interface EntityStyle {
  fillColor: string;
  fontColor?: string;
  rounded?: boolean;
  shape?: "rectangle" | "ellipse" | "diamond" | "cylinder" | "hexagon";
}

export interface Relationship {
  id: string;
  source: string;
  target: string;
  label?: string;
  style?: "orthogonal" | "curved" | "straight";
  direction?: "forward" | "backward" | "both";
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
}

export interface PipelineResult {
  xml: string;
  schema: DiagramSchema;
  warnings?: string[];
}
