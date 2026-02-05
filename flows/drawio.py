# flows/drawio.py
"""
Build draw.io (mxGraph XML) swimlane diagrams from an interpreted plan.
"""
import html
from typing import Dict, Any, List, Tuple


def _clean(s: str) -> str:
    return (s or "").strip()


def _esc(t: str) -> str:
    return html.escape(_clean(t), quote=True)


def _xml_newline(s: str) -> str:
    # draw.io uses &#xa; for newlines inside labels
    return s.replace("\n", "&#xa;")


def _wrap_words(text: str, max_chars: int = 18) -> str:
    words = text.split()
    lines = []
    line = ""
    for w in words:
        if not line:
            line = w
        elif len(line) + 1 + len(w) <= max_chars:
            line += " " + w
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return "&#xa;".join(lines)


def build_drawio_from_answers(plan: Dict[str, Any]) -> str:
    """
    plan schema:
      title: str
      lanes: [{id,name,color}]
      nodes: [{id,lane,label}]
      edges: [{from,to,label}]
    """
    title = _clean(plan.get("title", "Process Flow"))
    lanes = plan.get("lanes", [])
    nodes = plan.get("nodes", [])
    edges = plan.get("edges", [])

    # --- Layout constants (tweak here for structure) ---
    PAGE_X = 40
    PAGE_Y = 40

    TITLE_H = 44
    LANE_H = 120
    LANE_W = 980

    NODE_W = 160
    NODE_H = 54
    NODE_GAP_X = 40

    # left padding inside each lane
    LANE_PAD_X = 90
    LANE_PAD_Y = 36

    # Styles
    STYLES = {
        "title": "rounded=1;whiteSpace=wrap;html=1;fillColor=#1a1a2e;strokeColor=#16213e;"
                 "strokeWidth=2;fontColor=#ffffff;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;",
        "lane":  "swimlane;rounded=1;whiteSpace=wrap;html=1;startSize=34;horizontal=1;"
                 "strokeColor=#cfd8dc;strokeWidth=1;fontColor=#263238;fontSize=12;fontStyle=1;",
        "laneHeader": "text;html=1;align=left;verticalAlign=middle;resizable=0;points=[];"
                      "fontStyle=1;fontSize=12;fontColor=#263238;",
        "node":  "rounded=1;whiteSpace=wrap;html=1;strokeColor=#1f2937;strokeWidth=2;"
                 "fillColor=#3b82f6;fontColor=#ffffff;fontSize=11;fontStyle=1;align=center;verticalAlign=middle;",
        "edge":  "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
                 "html=1;strokeColor=#111827;strokeWidth=2;endArrow=classic;endFill=1;",
        "edgeLabel": "text;html=1;align=center;verticalAlign=middle;fontSize=10;fontStyle=1;"
                     "fontColor=#111827;resizable=0;points=[];",
    }

    # --- ids ---
    cells = []
    cell_id = 2

    def next_id() -> int:
        nonlocal cell_id
        cid = cell_id
        cell_id += 1
        return cid

    # root + parent are fixed 0/1
    # Title block
    title_id = next_id()
    cells.append(f"""
      <mxCell id="{title_id}" value="{_esc(title)}"
        style="{STYLES['title']}" vertex="1" parent="1">
        <mxGeometry x="{PAGE_X}" y="{PAGE_Y}" width="{LANE_W}" height="{TITLE_H}" as="geometry"/>
      </mxCell>
    """)

    # Lanes
    lane_y = PAGE_Y + TITLE_H + 20
    lane_box_ids: Dict[str, int] = {}
    lane_index: Dict[str, int] = {}

    for idx, lane in enumerate(lanes):
        lane_id = _clean(lane.get("id", f"lane_{idx}")) or f"lane_{idx}"
        lane_name = _clean(lane.get("name", f"Lane {idx+1}")) or f"Lane {idx+1}"
        lane_color = _clean(lane.get("color", "#f5f5f5")) or "#f5f5f5"

        box_id = next_id()
        lane_box_ids[lane_id] = box_id
        lane_index[lane_id] = idx

        # Swimlane background fillColor = lane_color
        lane_style = STYLES["lane"] + f"fillColor={lane_color};"

        cells.append(f"""
          <mxCell id="{box_id}" value="{_esc(lane_name)}"
            style="{lane_style}" vertex="1" parent="1">
            <mxGeometry x="{PAGE_X}" y="{lane_y + idx * (LANE_H + 18)}" width="{LANE_W}" height="{LANE_H}" as="geometry"/>
          </mxCell>
        """)

    # Place nodes inside lanes
    # simple: node order as given; pack left->right per lane
    lane_node_counts: Dict[str, int] = {l.get("id"): 0 for l in lanes}
    node_cell_ids: Dict[str, int] = {}

    for n in nodes:
        nid = _clean(n.get("id"))
        lane_id = _clean(n.get("lane"))
        label = _clean(n.get("label", "")) or "Step"

        if not nid or lane_id not in lane_box_ids:
            continue

        count = lane_node_counts.get(lane_id, 0)
        lane_node_counts[lane_id] = count + 1

        x = PAGE_X + LANE_PAD_X + count * (NODE_W + NODE_GAP_X)
        y = (PAGE_Y + TITLE_H + 20) + lane_index[lane_id] * (LANE_H + 18) + LANE_PAD_Y

        node_cell_id = next_id()
        node_cell_ids[nid] = node_cell_id

        short_label = _wrap_words(label, max_chars=18)

        cells.append(f"""
          <mxCell id="{node_cell_id}" value="{short_label}"
            style="{STYLES['node']}" vertex="1" parent="1">
            <mxGeometry x="{x}" y="{y}" width="{NODE_W}" height="{NODE_H}" as="geometry"/>
          </mxCell>
        """)

    # Edges with action labels
    for e in edges:
        src = _clean(e.get("from"))
        dst = _clean(e.get("to"))
        action = _clean(e.get("label", ""))

        if src not in node_cell_ids or dst not in node_cell_ids:
            continue

        edge_id = next_id()
        src_id = node_cell_ids[src]
        dst_id = node_cell_ids[dst]

        # main edge
        cells.append(f"""
          <mxCell id="{edge_id}" style="{STYLES['edge']}"
            edge="1" parent="1" source="{src_id}" target="{dst_id}">
            <mxGeometry relative="1" as="geometry"/>
          </mxCell>
        """)

        # edge label (small text near middle)
        if action:
            label_id = next_id()
            cells.append(f"""
              <mxCell id="{label_id}" value="{_esc(action)}"
                style="{STYLES['edgeLabel']}" vertex="1" parent="{edge_id}">
                <mxGeometry x="0.5" y="-10" relative="1" as="geometry">
                  <mxPoint x="0" y="0" as="offset"/>
                </mxGeometry>
              </mxCell>
            """)

    # Page sizing
    page_h = (PAGE_Y + TITLE_H + 20) + len(lanes) * (LANE_H + 18) + 60
    page_w = PAGE_X + LANE_W + 60

    cells_xml = "\n".join(cells)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{_esc(title)}" agent="ProcessFlow Export" version="21.0.0" type="device">
  <diagram name="Process Flow" id="process-flow-diagram">
    <mxGraphModel dx="{page_w}" dy="{page_h}" grid="1" gridSize="10" guides="1" tooltips="1"
      connect="1" arrows="1" fold="1" page="1" pageScale="1"
      pageWidth="{page_w}" pageHeight="{page_h}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {cells_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""
