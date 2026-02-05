# flows/drawio_from_plan.py
"""
Build draw.io (mxGraph XML) from an interpreted "plan" (lanes + nodes + edges).
Plan schema (from OpenAI):
{
  "title": "...",
  "lanes": [{"id":"lane_ds","name":"Data Subject","color":"#DFF3E3"}, ...],
  "nodes": [{"id":"n1","lane":"lane_ds","label":"Submit web form"}, ...],
  "edges": [{"from":"n1","to":"n2","label":"send"}, ...]
}

Key rendering rules:
- Nodes must be the same fillColor as their lane color.
- Edges must render BEHIND nodes (so arrows don't overlap boxes).
  In draw.io/mxGraph: cells written later are drawn on top.
  => We write edges first, then nodes last.
"""
from __future__ import annotations

import html


def _esc(s: str) -> str:
    return html.escape((s or "").strip(), quote=True)


def _short(s: str, max_len: int = 32) -> str:
    s = (s or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


def build_drawio_from_plan(plan: dict) -> str:
    title = _esc(plan.get("title") or "Process Flow")

    lanes = plan.get("lanes") or []
    nodes = plan.get("nodes") or []
    edges = plan.get("edges") or []

    # -----------------------
    # Layout constants
    # -----------------------
    START_X = 40
    START_Y = 40
    LANE_WIDTH = 1040
    LANE_HEIGHT = 140
    LANE_GAP = 18

    NODE_W = 170
    NODE_H = 56
    NODE_GAP_X = 70
    NODE_GAP_Y = 22
    LANE_PAD_X = 60
    LANE_PAD_Y = 52

    # draw.io cell ids
    cells = []
    cid = 2

    def next_id() -> int:
        nonlocal cid
        x = cid
        cid += 1
        return x

    # -----------------------
    # Title band
    # -----------------------
    title_id = next_id()
    cells.append(f"""
    <mxCell id="{title_id}" value="{title}" style="rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontStyle=1;fontSize=16;strokeWidth=2;fillColor=#1a1a2e;strokeColor=#16213e;fontColor=#ffffff;" vertex="1" parent="1">
      <mxGeometry x="{START_X}" y="{START_Y}" width="{LANE_WIDTH}" height="55" as="geometry"/>
    </mxCell>
    """)

    # -----------------------
    # Lanes (swimlanes)
    # -----------------------
    lane_y = START_Y + 75
    lane_cell_id_by_lane = {}
    lane_color_by_lane = {}

    for ln in lanes:
        lane_id = ln.get("id") or ""
        lane_name = _esc(ln.get("name") or lane_id or "Lane")
        lane_color = (ln.get("color") or "#f5f5f5").strip()

        lid = next_id()
        lane_cell_id_by_lane[lane_id] = lid
        lane_color_by_lane[lane_id] = lane_color

        # swimlane fillColor affects header + lane background
        cells.append(f"""
        <mxCell id="{lid}" value="{lane_name}" style="swimlane;rounded=1;whiteSpace=wrap;html=1;startSize=26;horizontal=0;align=left;verticalAlign=top;fontStyle=1;fontSize=12;fillColor={lane_color};strokeColor=#d0d0d0;" vertex="1" parent="1">
          <mxGeometry x="{START_X}" y="{lane_y}" width="{LANE_WIDTH}" height="{LANE_HEIGHT}" as="geometry"/>
        </mxCell>
        """)

        lane_y += LANE_HEIGHT + LANE_GAP

    # If plan had no lanes, create a default lane (so we don't crash)
    if not lanes:
        lane_id = "lane_default"
        lane_name = "Lane"
        lane_color = "#f5f5f5"
        lid = next_id()
        lane_cell_id_by_lane[lane_id] = lid
        lane_color_by_lane[lane_id] = lane_color
        lanes = [{"id": lane_id, "name": lane_name, "color": lane_color}]

        # also render it
        lane_y = START_Y + 75
        cells.append(f"""
        <mxCell id="{lid}" value="{_esc(lane_name)}" style="swimlane;rounded=1;whiteSpace=wrap;html=1;startSize=26;horizontal=0;align=left;verticalAlign=top;fontStyle=1;fontSize=12;fillColor={lane_color};strokeColor=#d0d0d0;" vertex="1" parent="1">
          <mxGeometry x="{START_X}" y="{lane_y}" width="{LANE_WIDTH}" height="{LANE_HEIGHT}" as="geometry"/>
        </mxCell>
        """)

    # -----------------------
    # Lane top y lookup
    # -----------------------
    lane_top_y = {}
    lane_y = START_Y + 75
    for ln in lanes:
        lane_top_y[ln["id"]] = lane_y
        lane_y += LANE_HEIGHT + LANE_GAP

    # -----------------------
    # Precompute node ids + layout (DO NOT append node cells yet)
    # This lets us write EDGES first (behind), then nodes last (on top).
    # -----------------------
    node_cell_id_by_node = {}
    node_layout = []  # list of dicts: {id, label, lane_id, x, y, fill}

    # packing state per lane
    lane_next_x = {ln["id"]: START_X + LANE_PAD_X for ln in lanes}
    lane_row_used = {ln["id"]: 0 for ln in lanes}

    for n in nodes:
        plan_node_id = n.get("id") or ""
        lane_id = n.get("lane")

        if lane_id not in lane_cell_id_by_lane:
            lane_id = lanes[0]["id"]

        # reserve a numeric mxCell id for this node (needed for edges)
        mx_node_id = next_id()
        node_cell_id_by_node[plan_node_id] = mx_node_id

        label = _esc(_short(n.get("label") or plan_node_id or "Step"))

        x = lane_next_x[lane_id]
        row = lane_row_used[lane_id]

        # wrap row if too far right
        if x + NODE_W > START_X + LANE_WIDTH - 40:
            row += 1
            lane_row_used[lane_id] = row
            x = START_X + LANE_PAD_X
            lane_next_x[lane_id] = x

        y = lane_top_y[lane_id] + LANE_PAD_Y + row * (NODE_H + NODE_GAP_Y)

        # move next x
        lane_next_x[lane_id] = x + NODE_W + NODE_GAP_X

        fill = lane_color_by_lane.get(lane_id, "#ffffff")

        node_layout.append(
            {
                "mx_id": mx_node_id,
                "label": label,
                "lane_id": lane_id,
                "x": x,
                "y": y,
                "fill": fill,
            }
        )

    # -----------------------
    # EDGES FIRST (so they render BEHIND nodes)
    # -----------------------
    # Labels: add labelBackgroundColor so text is readable
    for e in edges:
        eid = next_id()
        src = node_cell_id_by_node.get(e.get("from"))
        tgt = node_cell_id_by_node.get(e.get("to"))
        if not src or not tgt:
            continue

        elabel = _esc(_short(e.get("label") or "", 18))

        edge_style = (
            "edgeStyle=orthogonalEdgeStyle;"
            "rounded=0;"
            "orthogonalLoop=1;"
            "jettySize=auto;"
            "html=1;"
            "strokeColor=#000000;"
            "strokeWidth=2;"
            "endArrow=classic;"
            "endFill=1;"
            "fontSize=10;"
            "labelBackgroundColor=#ffffff;"
        )

        cells.append(f"""
        <mxCell id="{eid}" value="{elabel}" style="{edge_style}" edge="1" parent="1" source="{src}" target="{tgt}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        """)

    # -----------------------
    # NODES LAST (so they render ON TOP of edges)
    # Boxes share SAME fillColor as lane header color.
    # -----------------------
    for info in node_layout:
        mx_node_id = info["mx_id"]
        label = info["label"]
        x = info["x"]
        y = info["y"]
        fill = info["fill"]

        node_style = (
            "rounded=1;"
            "whiteSpace=wrap;"
            "html=1;"
            "align=center;"
            "verticalAlign=middle;"
            "strokeWidth=2;"
            "strokeColor=#2b2b2b;"
            f"fillColor={fill};"
            "fontStyle=1;"
            "fontSize=11;"
        )

        cells.append(f"""
        <mxCell id="{mx_node_id}" value="{label}" style="{node_style}" vertex="1" parent="1">
          <mxGeometry x="{x}" y="{y}" width="{NODE_W}" height="{NODE_H}" as="geometry"/>
        </mxCell>
        """)

    cells_xml = "\n".join(cells)

    # -----------------------
    # Page size
    # -----------------------
    page_h = (START_Y + 75) + len(lanes) * (LANE_HEIGHT + LANE_GAP) + 80
    page_w = START_X + LANE_WIDTH + 80

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{title}" agent="ProcessFlow Export" version="21.0.0" type="device">
  <diagram name="Process Flow" id="process-flow-diagram">
    <mxGraphModel dx="{page_w}" dy="{page_h}" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{page_w}" pageHeight="{page_h}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {cells_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
