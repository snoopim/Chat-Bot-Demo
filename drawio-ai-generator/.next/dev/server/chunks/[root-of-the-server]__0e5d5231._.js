module.exports = [
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/@opentelemetry/api [external] (next/dist/compiled/@opentelemetry/api, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/@opentelemetry/api", () => require("next/dist/compiled/@opentelemetry/api"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/after-task-async-storage.external.js [external] (next/dist/server/app-render/after-task-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/after-task-async-storage.external.js", () => require("next/dist/server/app-render/after-task-async-storage.external.js"));

module.exports = mod;
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/openai-client.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "chatCompletion",
    ()=>chatCompletion,
    "createOpenAIClient",
    ()=>createOpenAIClient,
    "listModels",
    ()=>listModels
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$openai$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/openai/index.mjs [app-route] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/openai/client.mjs [app-route] (ecmascript) <export OpenAI as default>");
;
function createOpenAIClient(apiKey) {
    return new __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__["default"]({
        apiKey
    });
}
async function chatCompletion(client, model, systemPrompt, userPrompt, jsonMode = true) {
    // o-series reasoning models don't support temperature or system role
    const isReasoningModel = /^o[0-9]/.test(model);
    const messages = isReasoningModel ? [
        {
            role: "user",
            content: `${systemPrompt}\n\n${userPrompt}`
        }
    ] : [
        {
            role: "system",
            content: systemPrompt
        },
        {
            role: "user",
            content: userPrompt
        }
    ];
    const response = await client.chat.completions.create({
        model,
        messages,
        ...jsonMode && !isReasoningModel && {
            response_format: {
                type: "json_object"
            }
        },
        ...!isReasoningModel && {
            temperature: 0.3
        }
    });
    return response.choices[0]?.message?.content ?? "";
}
async function listModels(apiKey) {
    const client = createOpenAIClient(apiKey);
    const list = await client.models.list();
    const models = [];
    for await (const model of list){
        models.push(model.id);
    }
    // Filter to chat-capable models and sort
    const chatModels = models.filter((id)=>id.startsWith("gpt-") || id.startsWith("o1") || id.startsWith("o3") || id.startsWith("o4")).sort();
    return chatModels;
}
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/prompts/extract-system.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "EXTRACT_EDIT_CONTEXT",
    ()=>EXTRACT_EDIT_CONTEXT,
    "EXTRACT_SYSTEM_PROMPT",
    ()=>EXTRACT_SYSTEM_PROMPT
]);
const EXTRACT_SYSTEM_PROMPT = `You are a diagram structure extractor. Given a user's description, output a JSON object following the DiagramSchema format.

Your task:
1. Extract ALL entities mentioned (boxes, nodes, systems, people, processes, steps, etc.)
2. Extract ALL relationships between entities (connections, arrows, data flows, dependencies)
3. Identify any grouping or categorization — these become swim lanes
4. Assign appropriate labels to all elements
5. Choose colors and shapes that make the diagram visually clear

Output a JSON object with this exact structure:
{
  "title": "Diagram Title",
  "lanes": [
    {
      "id": "lane_1",
      "label": "Lane Name",
      "color": "#hex_color",
      "order": 0
    }
  ],
  "entities": [
    {
      "id": "entity_1",
      "label": "Entity Name",
      "lane": "lane_1",
      "style": {
        "fillColor": "#hex_color",
        "fontColor": "#000000",
        "rounded": true,
        "shape": "rectangle"
      }
    }
  ],
  "relationships": [
    {
      "id": "rel_1",
      "source": "entity_1",
      "target": "entity_2",
      "label": "Connection Label",
      "style": "orthogonal",
      "direction": "forward"
    }
  ]
}

Rules:
- Use unique, descriptive IDs (e.g., "user_service", "login_step")
- If no swim lanes are needed, omit the "lanes" field or set it to []
- Only use "lane" on entities when lanes are defined
- Available shapes: "rectangle" (default), "ellipse" (start/end), "diamond" (decision), "cylinder" (database), "hexagon" (process)
- Use distinct, visually pleasant colors for different groups
- Every entity MUST have a unique ID
- Every relationship source and target MUST reference valid entity IDs
- Output ONLY valid JSON, no markdown fences, no explanation`;
const EXTRACT_EDIT_CONTEXT = `You are editing an existing diagram. The current diagram structure is provided below.
Merge the user's requested changes while preserving all unchanged elements.
- Keep existing entity IDs unchanged
- Add new entities with new unique IDs
- Remove entities only if explicitly requested
- Update labels, styles, or connections as requested
- Return the COMPLETE updated diagram, not just the changes

Current diagram:
`;
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/pipeline/extract.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "extractDiagramSchema",
    ()=>extractDiagramSchema
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$openai$2d$client$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/openai-client.ts [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$prompts$2f$extract$2d$system$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/prompts/extract-system.ts [app-route] (ecmascript)");
;
;
async function extractDiagramSchema(client, model, userPrompt, existingSchema) {
    let systemPrompt = __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$prompts$2f$extract$2d$system$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["EXTRACT_SYSTEM_PROMPT"];
    if (existingSchema) {
        systemPrompt += "\n\n" + __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$prompts$2f$extract$2d$system$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["EXTRACT_EDIT_CONTEXT"] + JSON.stringify(existingSchema, null, 2);
    }
    const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$openai$2d$client$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["chatCompletion"])(client, model, systemPrompt, userPrompt, true);
    const parsed = JSON.parse(response);
    // Basic validation
    if (!parsed.entities || !Array.isArray(parsed.entities)) {
        throw new Error("LLM output missing entities array");
    }
    if (!parsed.relationships) {
        parsed.relationships = [];
    }
    if (!parsed.title) {
        parsed.title = "Untitled Diagram";
    }
    return parsed;
}
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/pipeline/dagre-layout.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "layoutDiagram",
    ()=>layoutDiagram
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f40$dagrejs$2f$dagre$2f$dist$2f$dagre$2e$esm$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/@dagrejs/dagre/dist/dagre.esm.js [app-route] (ecmascript)");
;
const NODE_WIDTH_PER_CHAR = 10;
const NODE_MIN_WIDTH = 120;
const NODE_MAX_WIDTH = 250;
const NODE_HEIGHT = 50;
const LANE_HEADER_HEIGHT = 40;
const LANE_PADDING = 30;
const LANE_GAP = 20;
function estimateNodeSize(label) {
    const width = Math.min(NODE_MAX_WIDTH, Math.max(NODE_MIN_WIDTH, label.length * NODE_WIDTH_PER_CHAR + 40));
    return {
        width,
        height: NODE_HEIGHT
    };
}
function layoutDiagram(schema) {
    const g = new __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f40$dagrejs$2f$dagre$2f$dist$2f$dagre$2e$esm$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["default"].graphlib.Graph({
        compound: true
    });
    g.setGraph({
        rankdir: "TB",
        nodesep: 60,
        ranksep: 80,
        marginx: 40,
        marginy: 40
    });
    g.setDefaultEdgeLabel(()=>({}));
    // Add nodes
    for (const entity of schema.entities){
        const size = estimateNodeSize(entity.label);
        g.setNode(entity.id, {
            label: entity.label,
            width: size.width,
            height: size.height
        });
    }
    // Add edges
    for (const rel of schema.relationships){
        if (g.hasNode(rel.source) && g.hasNode(rel.target)) {
            g.setEdge(rel.source, rel.target, {
                label: rel.label || ""
            });
        }
    }
    // Run dagre layout
    __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f40$dagrejs$2f$dagre$2f$dist$2f$dagre$2e$esm$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["default"].layout(g);
    // Extract positions back to entities
    const positionedEntities = schema.entities.map((entity)=>{
        const node = g.node(entity.id);
        if (node) {
            return {
                ...entity,
                x: Math.round(node.x - node.width / 2),
                y: Math.round(node.y - node.height / 2),
                width: Math.round(node.width),
                height: Math.round(node.height)
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
        entities: positionedEntities
    };
}
function layoutWithLanes(schema, positionedEntities) {
    const lanes = [
        ...schema.lanes || []
    ].sort((a, b)=>a.order - b.order);
    const laneEntityMap = new Map();
    // Group entities by lane
    for (const entity of positionedEntities){
        const laneId = entity.lane || "__no_lane__";
        if (!laneEntityMap.has(laneId)) {
            laneEntityMap.set(laneId, []);
        }
        laneEntityMap.get(laneId).push(entity);
    }
    let currentY = 0;
    const adjustedEntities = [];
    for (const lane of lanes){
        const laneEntities = laneEntityMap.get(lane.id) || [];
        if (laneEntities.length === 0) {
            currentY += LANE_HEADER_HEIGHT + LANE_PADDING * 2 + LANE_GAP;
            continue;
        }
        // Find bounding box of entities in this lane
        let minY = Infinity;
        let maxY = -Infinity;
        for (const e of laneEntities){
            if (e.y !== undefined && e.height !== undefined) {
                minY = Math.min(minY, e.y);
                maxY = Math.max(maxY, e.y + e.height);
            }
        }
        const yOffset = currentY + LANE_HEADER_HEIGHT + LANE_PADDING - minY;
        for (const entity of laneEntities){
            adjustedEntities.push({
                ...entity,
                y: (entity.y || 0) + yOffset
            });
        }
        const laneHeight = maxY - minY + LANE_HEADER_HEIGHT + LANE_PADDING * 2;
        currentY += laneHeight + LANE_GAP;
    }
    // Add entities without lanes
    const noLaneEntities = laneEntityMap.get("__no_lane__") || [];
    for (const entity of noLaneEntities){
        adjustedEntities.push({
            ...entity,
            y: (entity.y || 0) + currentY
        });
    }
    return {
        ...schema,
        entities: adjustedEntities
    };
}
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/drawio/xml-builder.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "buildDrawioXml",
    ()=>buildDrawioXml,
    "wrapInMxFile",
    ()=>wrapInMxFile
]);
function escapeXml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}
function getShapeStyle(entity) {
    const parts = [];
    const shape = entity.style?.shape || "rectangle";
    switch(shape){
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
function darkenColor(hex) {
    const r = Math.max(0, parseInt(hex.slice(1, 3), 16) - 40);
    const g = Math.max(0, parseInt(hex.slice(3, 5), 16) - 40);
    const b = Math.max(0, parseInt(hex.slice(5, 7), 16) - 40);
    return `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
}
function getEdgeStyle(rel) {
    const parts = [];
    switch(rel.style){
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
function buildLaneCell(lane, x, y, width, height) {
    const style = `swimlane;fillColor=${lane.color};strokeColor=${darkenColor(lane.color)};fontColor=#333333;startSize=30;html=1;collapsible=0;`;
    return `    <mxCell id="${escapeXml(lane.id)}" value="${escapeXml(lane.label)}" style="${style}" vertex="1" parent="1">
      <mxGeometry x="${x}" y="${y}" width="${width}" height="${height}" as="geometry" />
    </mxCell>`;
}
function buildEntityCell(entity, parent = "1") {
    const style = getShapeStyle(entity);
    const x = entity.x ?? 0;
    const y = entity.y ?? 0;
    const width = entity.width ?? 120;
    const height = entity.height ?? 50;
    return `    <mxCell id="${escapeXml(entity.id)}" value="${escapeXml(entity.label)}" style="${style}" vertex="1" parent="${escapeXml(parent)}">
      <mxGeometry x="${x}" y="${y}" width="${width}" height="${height}" as="geometry" />
    </mxCell>`;
}
function buildEdgeCell(rel) {
    const style = getEdgeStyle(rel);
    const labelAttr = rel.label ? ` value="${escapeXml(rel.label)}"` : ' value=""';
    return `    <mxCell id="${escapeXml(rel.id)}"${labelAttr} style="${style}" edge="1" source="${escapeXml(rel.source)}" target="${escapeXml(rel.target)}" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>`;
}
function buildDrawioXml(schema) {
    const cells = [
        '    <mxCell id="0" />',
        '    <mxCell id="1" parent="0" />'
    ];
    // Build lane cells if present
    if (schema.lanes && schema.lanes.length > 0) {
        const laneEntities = new Map();
        for (const entity of schema.entities){
            if (entity.lane) {
                if (!laneEntities.has(entity.lane)) {
                    laneEntities.set(entity.lane, []);
                }
                laneEntities.get(entity.lane).push(entity);
            }
        }
        for (const lane of schema.lanes){
            const entities = laneEntities.get(lane.id) || [];
            if (entities.length === 0) {
                cells.push(buildLaneCell(lane, 0, lane.order * 200, 800, 180));
                continue;
            }
            // Compute lane bounds from its entities
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            for (const e of entities){
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
            for (const entity of entities){
                const relEntity = {
                    ...entity,
                    x: (entity.x ?? 0) - laneX,
                    y: (entity.y ?? 0) - laneY
                };
                cells.push(buildEntityCell(relEntity, lane.id));
            }
        }
        // Add entities not in any lane
        for (const entity of schema.entities){
            if (!entity.lane) {
                cells.push(buildEntityCell(entity));
            }
        }
    } else {
        // No lanes — add all entities directly
        for (const entity of schema.entities){
            cells.push(buildEntityCell(entity));
        }
    }
    // Add edges
    for (const rel of schema.relationships){
        cells.push(buildEdgeCell(rel));
    }
    return `<mxGraphModel dx="1422" dy="762" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827">
  <root>
${cells.join("\n")}
  </root>
</mxGraphModel>`;
}
function wrapInMxFile(xml) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<mxfile version="1.0">
  <diagram name="Page-1">
    ${xml}
  </diagram>
</mxfile>`;
}
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/pipeline/render.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "renderDiagramXml",
    ()=>renderDiagramXml
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$drawio$2f$xml$2d$builder$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/drawio/xml-builder.ts [app-route] (ecmascript)");
;
function renderDiagramXml(schema) {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$drawio$2f$xml$2d$builder$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["buildDrawioXml"])(schema);
}
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/prompts/repair-system.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "REPAIR_SYSTEM_PROMPT",
    ()=>REPAIR_SYSTEM_PROMPT
]);
const REPAIR_SYSTEM_PROMPT = `You are a diagram structure repair assistant. You receive a DiagramSchema JSON that has validation errors.

Fix the errors and return the corrected JSON. Common issues:
- Relationships referencing non-existent entity IDs → either fix the reference or add the missing entity
- Duplicate IDs → make them unique
- Missing required fields → add sensible defaults
- Entities assigned to non-existent lanes → either fix the lane reference or remove the lane assignment

Return ONLY the corrected JSON, no explanation.`;
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/pipeline/validate.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "repairSchema",
    ()=>repairSchema,
    "validateSchema",
    ()=>validateSchema
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$openai$2d$client$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/openai-client.ts [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$prompts$2f$repair$2d$system$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/prompts/repair-system.ts [app-route] (ecmascript)");
;
;
function validateSchema(schema) {
    const errors = [];
    const entityIds = new Set(schema.entities.map((e)=>e.id));
    // Check for duplicate entity IDs
    if (entityIds.size !== schema.entities.length) {
        errors.push("Duplicate entity IDs found");
    }
    // Check relationship references
    for (const rel of schema.relationships){
        if (!entityIds.has(rel.source)) {
            errors.push(`Relationship "${rel.id}" references non-existent source "${rel.source}"`);
        }
        if (!entityIds.has(rel.target)) {
            errors.push(`Relationship "${rel.id}" references non-existent target "${rel.target}"`);
        }
    }
    // Check lane references
    if (schema.lanes && schema.lanes.length > 0) {
        const laneIds = new Set(schema.lanes.map((l)=>l.id));
        for (const entity of schema.entities){
            if (entity.lane && !laneIds.has(entity.lane)) {
                errors.push(`Entity "${entity.id}" references non-existent lane "${entity.lane}"`);
            }
        }
    }
    // Check for empty entities
    if (schema.entities.length === 0) {
        errors.push("Diagram has no entities");
    }
    // Check duplicate relationship IDs
    const relIds = new Set();
    for (const rel of schema.relationships){
        if (relIds.has(rel.id)) {
            errors.push(`Duplicate relationship ID "${rel.id}"`);
        }
        relIds.add(rel.id);
    }
    return {
        valid: errors.length === 0,
        errors
    };
}
async function repairSchema(client, model, schema, errors) {
    const userPrompt = `Fix this DiagramSchema JSON. Errors found:\n${errors.map((e)=>`- ${e}`).join("\n")}\n\nCurrent JSON:\n${JSON.stringify(schema, null, 2)}`;
    const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$openai$2d$client$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["chatCompletion"])(client, model, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$prompts$2f$repair$2d$system$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["REPAIR_SYSTEM_PROMPT"], userPrompt, true);
    return JSON.parse(response);
}
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/pipeline/orchestrator.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "runPipeline",
    ()=>runPipeline
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$extract$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/pipeline/extract.ts [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$dagre$2d$layout$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/pipeline/dagre-layout.ts [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$render$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/pipeline/render.ts [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$validate$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/pipeline/validate.ts [app-route] (ecmascript)");
;
;
;
;
const MAX_REPAIR_ITERATIONS = 2;
async function runPipeline(client, model, userPrompt, existingSchema) {
    const warnings = [];
    // Stage 1: Extract — LLM produces DiagramSchema JSON
    let schema = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$extract$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["extractDiagramSchema"])(client, model, userPrompt, existingSchema);
    // Stage 4 (pre-layout validation + repair loop)
    for(let i = 0; i < MAX_REPAIR_ITERATIONS; i++){
        const validation = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$validate$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["validateSchema"])(schema);
        if (validation.valid) break;
        if (i === MAX_REPAIR_ITERATIONS - 1) {
            warnings.push(`Diagram has unresolved issues after ${MAX_REPAIR_ITERATIONS} repair attempts: ${validation.errors.join("; ")}`);
            // Try to salvage: remove bad relationships
            schema = {
                ...schema,
                relationships: schema.relationships.filter((rel)=>{
                    const entityIds = new Set(schema.entities.map((e)=>e.id));
                    return entityIds.has(rel.source) && entityIds.has(rel.target);
                })
            };
            break;
        }
        schema = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$validate$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["repairSchema"])(client, model, schema, validation.errors);
    }
    // Stage 2: Layout — dagre positions all entities
    const positionedSchema = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$dagre$2d$layout$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["layoutDiagram"])(schema);
    // Stage 3: Render — positioned JSON → draw.io XML
    const xml = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$render$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["renderDiagramXml"])(positionedSchema);
    return {
        xml,
        schema: positionedSchema,
        warnings: warnings.length > 0 ? warnings : undefined
    };
}
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/drawio/xml-parser.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "parseDrawioXml",
    ()=>parseDrawioXml
]);
function parseDrawioXml(xml) {
    try {
        const parser = new DOMParser();
        const doc = parser.parseFromString(xml, "text/xml");
        const root = doc.querySelector("root");
        if (!root) return null;
        const cells = root.querySelectorAll("mxCell");
        const entities = [];
        const relationships = [];
        const lanes = [];
        let laneOrder = 0;
        cells.forEach((cell)=>{
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
                    style: style.includes("curved") ? "curved" : style.includes("none") ? "straight" : "orthogonal"
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
                        order: laneOrder++
                    });
                } else {
                    const parent = cell.getAttribute("parent") || "1";
                    const fillMatch = style.match(/fillColor=([^;]+)/);
                    const fontMatch = style.match(/fontColor=([^;]+)/);
                    let shape = "rectangle";
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
                            shape
                        }
                    });
                }
            }
        });
        return {
            title: "Parsed Diagram",
            lanes: lanes.length > 0 ? lanes : undefined,
            entities,
            relationships
        };
    } catch  {
        return null;
    }
}
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/api/generate/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "POST",
    ()=>POST
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/next/server.js [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$openai$2d$client$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/openai-client.ts [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$orchestrator$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/pipeline/orchestrator.ts [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$drawio$2f$xml$2d$parser$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/drawio/xml-parser.ts [app-route] (ecmascript)");
;
;
;
;
async function POST(req) {
    try {
        const { prompt, existingXml, model, apiKey } = await req.json();
        if (!apiKey) {
            return __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                error: "API key is required"
            }, {
                status: 400
            });
        }
        if (!prompt) {
            return __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                error: "Prompt is required"
            }, {
                status: 400
            });
        }
        const client = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$openai$2d$client$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["createOpenAIClient"])(apiKey);
        const selectedModel = model || "gpt-4.1-mini";
        // Parse existing XML to schema for edit context
        let existingSchema = undefined;
        if (existingXml) {
            existingSchema = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$drawio$2f$xml$2d$parser$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["parseDrawioXml"])(existingXml) ?? undefined;
        }
        const result = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$pipeline$2f$orchestrator$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["runPipeline"])(client, selectedModel, prompt, existingSchema);
        return __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json(result);
    } catch (err) {
        const message = err instanceof Error ? err.message : "Pipeline failed";
        // Check for OpenAI-specific errors
        if (message.includes("Incorrect API key") || message.includes("401")) {
            return __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                error: "Invalid API key. Please check your OpenAI API key."
            }, {
                status: 401
            });
        }
        return __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            error: message
        }, {
            status: 500
        });
    }
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__0e5d5231._.js.map