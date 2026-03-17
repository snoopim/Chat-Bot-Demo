# flows/reactflow_from_plan.py
"""
Convert a diagram plan (same JSON as drawio_from_plan) into a standalone
HTML file that renders a ReactFlow-style swimlane diagram using pure
HTML/CSS/SVG — no CDN dependency, headless-Chrome-friendly.

Input  – plan dict  { title, lanes[], nodes[], edges[] }
Output – self-contained HTML string
"""
from __future__ import annotations

import html
import json
import math
from typing import Dict, Any, List, Tuple, Optional


# ==========================================================
# Helpers (shared logic with drawio_from_plan)
# ==========================================================
LANE_COLORS = [
    "#2196F3",  # blue
    "#4CAF50",  # green
    "#FF9800",  # orange
    "#9C27B0",  # purple
    "#00BCD4",  # cyan
    "#FF5722",  # deep orange
    "#8BC34A",  # lime
    "#E91E63",  # pink
]

LANE_BG_COLORS = [
    "#E3F2FD",  # light blue
    "#E8F5E9",  # light green
    "#FFF3E0",  # light orange
    "#F3E5F5",  # light purple
    "#E0F7FA",  # light cyan
    "#FBE9E7",  # light deep orange
    "#F1F8E9",  # light lime
    "#FCE4EC",  # light pink
]


def _esc(s: str) -> str:
    return html.escape((s or "").strip(), quote=True)


def _short(s: str, max_len: int = 32) -> str:
    s = (s or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


def _slug_lane_id(name: str, idx: int) -> str:
    base = "".join(ch.lower() if ch.isalnum() else "_" for ch in (name or "")).strip("_")
    return f"lane_{base}" if base else f"lane_{idx}"


def _is_hex_color(c: str) -> bool:
    if not isinstance(c, str):
        return False
    c = c.strip()
    if len(c) != 7 or not c.startswith("#"):
        return False
    return all(ch in "0123456789abcdefABCDEF" for ch in c[1:])


def _darken_hex(color: str, factor: float = 0.75) -> str:
    if not _is_hex_color(color):
        return "#888888"
    c = color.lstrip("#")
    r = max(0, min(255, int(int(c[0:2], 16) * factor)))
    g = max(0, min(255, int(int(c[2:4], 16) * factor)))
    b = max(0, min(255, int(int(c[4:6], 16) * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


# ==========================================================
# Normalize plan (same logic as drawio_from_plan)
# ==========================================================
def _normalize_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(plan, dict):
        return {"title": " ", "lanes": [], "nodes": [], "edges": []}

    lanes = plan.get("lanes") or []
    if lanes and isinstance(lanes, list) and isinstance(lanes[0], str):
        new_lanes: List[Dict[str, Any]] = []
        for i, name in enumerate(lanes):
            lid = _slug_lane_id(str(name), i)
            new_lanes.append({"id": lid, "name": str(name), "color": LANE_COLORS[i % len(LANE_COLORS)]})
        plan["lanes"] = new_lanes
        lanes = new_lanes

    if not lanes or not isinstance(lanes, list) or not isinstance(lanes[0], dict):
        plan["lanes"] = [{"id": "lane_default", "name": "Lane", "color": "#E3F2FD"}]
        lanes = plan["lanes"]

    for i, ln in enumerate(lanes):
        if not isinstance(ln, dict):
            continue
        if not ln.get("id"):
            ln["id"] = f"lane_{i}"
        if not ln.get("name"):
            ln["name"] = ln["id"]
        ln["color"] = LANE_COLORS[i % len(LANE_COLORS)]

    lane_ids = {l.get("id") for l in lanes if isinstance(l, dict) and l.get("id")}
    default_lane = next(iter(lane_ids), "lane_default")

    nodes = plan.get("nodes") or []
    if not isinstance(nodes, list):
        nodes = []
    for i, n in enumerate(nodes):
        if not isinstance(n, dict):
            continue
        nid = n.get("id")
        if nid is None or str(nid).strip() == "":
            n["id"] = f"n{i+1}"
        else:
            nid_str = str(nid).strip()
            n["id"] = nid_str if nid_str.startswith("n") else f"n{nid_str}"
        lane = n.get("lane")
        if not lane or lane not in lane_ids:
            n["lane"] = default_lane
        if not n.get("label"):
            n["label"] = n["id"]
    plan["nodes"] = nodes

    edges = plan.get("edges") or []
    if not isinstance(edges, list):
        edges = []
    for e in edges:
        if not isinstance(e, dict):
            continue
        f = e.get("from")
        t = e.get("to")
        if f is not None:
            fs = str(f).strip()
            e["from"] = fs if fs.startswith("n") else (f"n{fs}" if fs else fs)
        if t is not None:
            ts = str(t).strip()
            e["to"] = ts if ts.startswith("n") else (f"n{ts}" if ts else ts)
        if e.get("label") is None:
            e["label"] = ""
        if e.get("data_label") in (None, ""):
            for k in ("dataLabel", "datalabel", "data-label", "data", "data_type", "datatype"):
                v = e.get(k)
                if isinstance(v, str) and v.strip():
                    e["data_label"] = v.strip()
                    break
            else:
                e["data_label"] = ""

    merged: Dict[tuple, Dict[str, Any]] = {}
    for e in edges:
        if not isinstance(e, dict):
            continue
        key = (e.get("from"), e.get("to"))
        if key not in merged:
            merged[key] = dict(e)
    plan["edges"] = list(merged.values())
    return plan


def _lane_order_three(lanes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    name_to_rank = {
        "people": 0, "person": 0, "roles": 0,
        "systems": 1, "system": 1,
        "partners": 2, "partner": 2, "external": 2,
    }
    ranked = []
    for ln in lanes:
        nm = (ln.get("name") or "").strip().lower()
        ranked.append((name_to_rank.get(nm, 99), ln))
    ranked.sort(key=lambda x: x[0])
    if any(r[0] != 99 for r in ranked):
        return [r[1] for r in ranked]
    return lanes


def _nounify_edge_label(label: str, data_label: str) -> str:
    dl = (data_label or "").strip()
    lb = (label or "").strip()
    if dl and len(dl) > 2:
        return dl
    verb_to_noun = {
        "submit": "Submission", "store": "Storage", "send": "Transfer",
        "sync": "Synchronization", "publish": "Publication", "track": "Tracking",
        "create": "Creation", "view": "Access", "update": "Update",
        "record": "Record", "run": "Execution", "export": "Export",
        "import": "Import", "migrate": "Migration", "reconcile": "Reconciliation",
        "approve": "Approval", "review": "Review", "validate": "Validation",
        "check": "Check",
    }
    if lb.lower() in verb_to_noun:
        return verb_to_noun[lb.lower()]
    if not lb:
        return ""
    return lb[:1].upper() + lb[1:]


# ==========================================================
# Layout constants
# ==========================================================
LANE_HEADER_W = 28          # vertical header strip width (left side)
LANE_PAD_X = 60
LANE_PAD_Y = 40
NODE_W = 170
NODE_H = 50
COL_GAP = 100
ROW_GAP = 70
LANE_GAP = 60                # gap between lanes for edge routing
TITLE_H = 50
CANVAS_PAD = 30


# ==========================================================
# MAIN – build ReactFlow-style HTML from plan
# ==========================================================
def build_reactflow_html(plan: dict) -> str:
    plan = _normalize_plan(plan)

    title = (plan.get("title") or "Process Flow").strip()
    lanes = plan.get("lanes") or []
    nodes = plan.get("nodes") or []
    edges = plan.get("edges") or []

    # Keep only used lanes
    used_lane_ids = {n.get("lane") for n in nodes if isinstance(n, dict) and n.get("lane")}
    lanes = [ln for ln in lanes if isinstance(ln, dict) and ln.get("id") in used_lane_ids]
    if not lanes:
        lanes = [{"id": "lane_default", "name": "Lane", "color": "#E3F2FD"}]
        for n in nodes:
            if isinstance(n, dict):
                n["lane"] = "lane_default"

    lanes = _lane_order_three(lanes)
    lane_ids = [ln.get("id") for ln in lanes if ln.get("id")]

    for i, ln in enumerate(lanes):
        if not _is_hex_color(ln.get("color")):
            ln["color"] = LANE_COLORS[i % len(LANE_COLORS)]

    default_lane = lane_ids[0] if lane_ids else "lane_default"
    for n in nodes:
        if isinstance(n, dict) and n.get("lane") not in set(lane_ids):
            n["lane"] = default_lane

    # ---- Node map ----
    node_by_id: Dict[str, Dict[str, Any]] = {}
    for n in nodes:
        if isinstance(n, dict) and n.get("id"):
            node_by_id[n["id"]] = n

    # ---- Group by lane ----
    lane_nodes: Dict[str, List[str]] = {lid: [] for lid in lane_ids}
    for nid, n in node_by_id.items():
        lid = n.get("lane") or default_lane
        if lid in lane_nodes:
            lane_nodes[lid].append(nid)

    # Sort nodes alphabetically within each lane
    for lid in lane_ids:
        lane_nodes[lid].sort(key=lambda nid: (node_by_id[nid].get("label") or "").strip().lower())

    # ---- Compute lane width ----
    max_cols = max((len(nids) for nids in lane_nodes.values()), default=1)
    max_cols = max(max_cols, 1)
    lane_content_w = max_cols * NODE_W + (max_cols - 1) * COL_GAP
    lane_w = max(600, lane_content_w + LANE_PAD_X * 2)

    # ---- Compute positions ----
    # node_id -> {x, y, w, h, cx, cy}
    node_geom: Dict[str, Dict[str, float]] = {}
    lane_rects: List[Dict[str, Any]] = []

    current_y = CANVAS_PAD + TITLE_H + 16

    for lane_idx, lid in enumerate(lane_ids):
        ln = lanes[lane_idx]
        lane_color = ln.get("color", LANE_COLORS[lane_idx % len(LANE_COLORS)])
        lane_bg = LANE_BG_COLORS[lane_idx % len(LANE_BG_COLORS)]
        lane_name = (ln.get("name") or lid).strip()

        nids = lane_nodes.get(lid, [])
        cols_per_row = max(1, min(len(nids), 3))
        num_rows = max(1, (len(nids) + cols_per_row - 1) // cols_per_row) if nids else 1
        lane_content_h = num_rows * NODE_H + (num_rows - 1) * ROW_GAP
        lane_h = LANE_PAD_Y * 2 + lane_content_h

        lane_x = CANVAS_PAD
        lane_y = current_y

        lane_rects.append({
            "id": lid,
            "name": lane_name,
            "color": lane_color,
            "bg": lane_bg,
            "x": lane_x,
            "y": lane_y,
            "w": lane_w,
            "h": lane_h,
        })

        # Place nodes (offset right to clear vertical header strip)
        node_area_x = lane_x + LANE_HEADER_W
        node_area_w = lane_w - LANE_HEADER_W

        for i, nid in enumerate(nids):
            col = i % cols_per_row
            row = i // cols_per_row

            # How many nodes in this row
            row_start = row * cols_per_row
            row_count = min(cols_per_row, len(nids) - row_start)
            total_row_w = row_count * NODE_W + (row_count - 1) * COL_GAP
            start_x = node_area_x + (node_area_w - total_row_w) / 2.0

            nx = start_x + col * (NODE_W + COL_GAP)
            ny = lane_y + LANE_PAD_Y + row * (NODE_H + ROW_GAP)

            node_geom[nid] = {
                "x": nx,
                "y": ny,
                "w": NODE_W,
                "h": NODE_H,
                "cx": nx + NODE_W / 2.0,
                "cy": ny + NODE_H / 2.0,
                "lane_id": lid,
                "color": lane_color,
                "row": row,
                "col": col,
            }

        current_y += lane_h + LANE_GAP

    total_w = CANVAS_PAD * 2 + lane_w
    total_h = current_y + CANVAS_PAD

    # ---- Build lane lookup for gap routing ----
    lane_rect_by_id: Dict[str, Dict[str, Any]] = {lr["id"]: lr for lr in lane_rects}
    lane_index: Dict[str, int] = {lid: i for i, lid in enumerate(lane_ids)}

    # ---- Grid-based Dijkstra pathfinding for edges ----
    import heapq as _hq

    edge_svgs: List[str] = []
    edge_labels: List[str] = []
    placed_labels: List[Tuple[float, float, float, float]] = []
    edge_route_records: List[Dict[str, Any]] = []

    # Port offset tracking
    edge_port_counter: Dict[Tuple[str, str], int] = {}

    def _next_port_offset(nid: str, side: str) -> float:
        key = (nid, side)
        idx = edge_port_counter.get(key, 0)
        edge_port_counter[key] = idx + 1
        if idx == 0:
            return 0.0
        sign = 1.0 if idx % 2 == 1 else -1.0
        return sign * ((idx + 1) // 2) * 18.0

    # Grid setup
    GRID = 16
    gcols = int(total_w / GRID) + 2
    grows = int(total_h / GRID) + 2

    # Block grid cells occupied by nodes (with padding)
    blocked_cells: set = set()
    NPAD = 12
    for _nid_b, _gb in node_geom.items():
        gx1 = max(0, int((_gb["x"] - NPAD) / GRID))
        gy1 = max(0, int((_gb["y"] - NPAD) / GRID))
        gx2 = min(gcols - 1, int((_gb["x"] + _gb["w"] + NPAD) / GRID) + 1)
        gy2 = min(grows - 1, int((_gb["y"] + _gb["h"] + NPAD) / GRID) + 1)
        for _gy in range(gy1, gy2 + 1):
            for _gx in range(gx1, gx2 + 1):
                blocked_cells.add((_gx, _gy))

    # Block the title bar area and everything above it
    title_bottom_gy = int((CANVAS_PAD + TITLE_H + 8) / GRID) + 1
    for _gy in range(0, title_bottom_gy):
        for _gx in range(0, gcols):
            blocked_cells.add((_gx, _gy))

    # Block area below the last lane
    last_lane_bottom = current_y - LANE_GAP + 10
    bottom_gy = int(last_lane_bottom / GRID) + 1
    for _gy in range(bottom_gy, grows):
        for _gx in range(0, gcols):
            blocked_cells.add((_gx, _gy))

    # Block the left edge (lane header strip) — edges should not route
    # through the lane name labels
    header_gx = int((CANVAS_PAD + LANE_HEADER_W + 4) / GRID) + 1
    for _gy in range(0, grows):
        for _gx in range(0, header_gx):
            blocked_cells.add((_gx, _gy))

    # Block the right edge — keep edges inside the canvas
    right_gx = int((CANVAS_PAD + lane_w + 4) / GRID)
    for _gy in range(0, grows):
        for _gx in range(right_gx, gcols):
            blocked_cells.add((_gx, _gy))

    # Heatmap: penalise cells near already-routed edges
    edge_heat: Dict[Tuple[int, int], int] = {}

    def _dijkstra(sx: float, sy: float, ex: float, ey: float
                  ) -> Optional[List[Tuple[int, int]]]:
        sgx = max(0, min(gcols - 1, round(sx / GRID)))
        sgy = max(0, min(grows - 1, round(sy / GRID)))
        egx = max(0, min(gcols - 1, round(ex / GRID)))
        egy = max(0, min(grows - 1, round(ey / GRID)))
        if sgx == egx and sgy == egy:
            return [(sgx, sgy)]

        # Allow cells at/near ports even if blocked by node padding
        allowed: set = set()
        for _dx in range(-2, 3):
            for _dy in range(-2, 3):
                allowed.add((sgx + _dx, sgy + _dy))
                allowed.add((egx + _dx, egy + _dy))

        # (cost, x, y, direction)  direction: 0=start 1=horiz 2=vert
        pq: list = [(0, sgx, sgy, 0)]
        done: Dict[Tuple[int, int, int], float] = {}
        dist: Dict[Tuple[int, int, int], float] = {(sgx, sgy, 0): 0}
        parent: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}
        goal = None

        while pq:
            cost, cx, cy, cd = _hq.heappop(pq)
            st = (cx, cy, cd)
            if st in done:
                continue
            done[st] = cost
            if cx == egx and cy == egy:
                goal = st
                break
            for ddx, ddy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = cx + ddx, cy + ddy
                if nx < 0 or nx >= gcols or ny < 0 or ny >= grows:
                    continue
                cell = (nx, ny)
                if cell in blocked_cells and cell not in allowed:
                    continue
                nd = 1 if ddx != 0 else 2
                step = 1
                if cd != 0 and nd != cd:
                    step += 8          # turn penalty — prefer straight routes
                h = edge_heat.get(cell, 0)
                if h > 0:
                    step += h * 12     # overlap penalty
                nc = cost + step
                ns = (nx, ny, nd)
                if ns not in done and nc < dist.get(ns, 1e9):
                    dist[ns] = nc
                    parent[ns] = st
                    _hq.heappush(pq, (nc, nx, ny, nd))

        if goal is None:
            return None

        path: List[Tuple[int, int]] = []
        s = goal
        while s in parent:
            path.append((s[0], s[1]))
            s = parent[s]
        path.append((s[0], s[1]))
        path.reverse()
        return path

    def _grid_to_px(gpath: List[Tuple[int, int]],
                    sx: float, sy: float, ex: float, ey: float
                    ) -> List[Tuple[float, float]]:
        if not gpath or len(gpath) < 2:
            return [(sx, sy), (ex, ey)]
        # Simplify: keep only turning points
        simple = [gpath[0]]
        for i in range(1, len(gpath) - 1):
            p, c, n = gpath[i - 1], gpath[i], gpath[i + 1]
            if c[0] - p[0] != n[0] - c[0] or c[1] - p[1] != n[1] - c[1]:
                simple.append(c)
        simple.append(gpath[-1])
        # Convert to pixel coordinates
        pts: List[Tuple[float, float]] = []
        for i, (gx, gy) in enumerate(simple):
            if i == 0:
                pts.append((sx, sy))
            elif i == len(simple) - 1:
                pts.append((ex, ey))
            else:
                pts.append((gx * GRID + GRID / 2.0, gy * GRID + GRID / 2.0))
        # Fix any diagonal segments to maintain orthogonality
        clean: List[Tuple[float, float]] = [pts[0]]
        for i in range(1, len(pts)):
            px, py = pts[i]
            lx_c, ly_c = clean[-1]
            if abs(px - lx_c) > 3 and abs(py - ly_c) > 3:
                clean.append((px, ly_c))
            clean.append((px, py))
        return clean

    def _mark_heat(gpath: List[Tuple[int, int]]):
        for gx, gy in gpath:
            for ddx in range(-2, 3):
                for ddy in range(-2, 3):
                    c = (gx + ddx, gy + ddy)
                    edge_heat[c] = edge_heat.get(c, 0) + 1

    # ---- Route each edge ----
    for e in edges:
        if not isinstance(e, dict):
            continue
        src_id = (e.get("from") or "").strip()
        tgt_id = (e.get("to") or "").strip()
        if not src_id or not tgt_id or src_id == tgt_id:
            continue
        if src_id not in node_geom or tgt_id not in node_geom:
            continue

        sg = node_geom[src_id]
        tg = node_geom[tgt_id]
        same_lane = sg.get("lane_id") == tg.get("lane_id")

        raw_label = (e.get("label") or "").strip()
        raw_data_label = (e.get("data_label") or "").strip()
        visible_label = _short(_nounify_edge_label(raw_label, raw_data_label), 48)

        src_cx, src_cy = sg["cx"], sg["cy"]
        tgt_cx, tgt_cy = tg["cx"], tg["cy"]

        # Pick exit/entry sides
        if same_lane:
            sr, tr = sg.get("row", 0), tg.get("row", 0)
            if sr == tr:
                dx = tgt_cx - src_cx
                s_side = "right" if dx >= 0 else "left"
                t_side = "left" if dx >= 0 else "right"
            else:
                s_side = "bottom" if sr < tr else "top"
                t_side = "top" if sr < tr else "bottom"
        else:
            s_side = "bottom" if src_cy < tgt_cy else "top"
            t_side = "top" if src_cy < tgt_cy else "bottom"

        s_off = _next_port_offset(src_id, s_side)
        t_off = _next_port_offset(tgt_id, t_side)

        if s_side == "right":
            sx, sy = sg["x"] + sg["w"], src_cy + s_off
        elif s_side == "left":
            sx, sy = sg["x"], src_cy + s_off
        elif s_side == "bottom":
            sx, sy = src_cx + s_off, sg["y"] + sg["h"]
        else:
            sx, sy = src_cx + s_off, sg["y"]

        if t_side == "right":
            ex, ey = tg["x"] + tg["w"], tgt_cy + t_off
        elif t_side == "left":
            ex, ey = tg["x"], tgt_cy + t_off
        elif t_side == "top":
            ex, ey = tgt_cx + t_off, tg["y"]
        else:
            ex, ey = tgt_cx + t_off, tg["y"] + tg["h"]

        gpath = _dijkstra(sx, sy, ex, ey)
        if gpath:
            points = _grid_to_px(gpath, sx, sy, ex, ey)
            _mark_heat(gpath)
        else:
            points = [(sx, sy), (ex, ey)]

        # --- Fix arrow alignment: ensure the last segment enters the
        #     target node perpendicular to its face, and the first segment
        #     exits the source node perpendicular to its face. ---
        if len(points) >= 2:
            # Fix LAST segment → arrow must point into the target face
            pre_x, pre_y = points[-2]
            if t_side in ("top", "bottom"):
                # Need vertical last segment
                if abs(pre_x - ex) > 3:
                    points.insert(-1, (ex, pre_y))
            else:
                # Need horizontal last segment
                if abs(pre_y - ey) > 3:
                    points.insert(-1, (pre_x, ey))

        if len(points) >= 2:
            # Fix FIRST segment → exit perpendicular to the source face
            nxt_x, nxt_y = points[1]
            if s_side in ("top", "bottom"):
                if abs(nxt_x - sx) > 3:
                    points.insert(1, (sx, nxt_y))
            else:
                if abs(nxt_y - sy) > 3:
                    points.insert(1, (nxt_x, sy))

        # --- Final strict orthogonality: break ALL diagonal segments ---
        def _enforce_ortho(pts: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
            changed = True
            while changed:
                changed = False
                out: List[Tuple[float, float]] = [pts[0]]
                for i in range(1, len(pts)):
                    px, py = pts[i]
                    lx_o, ly_o = out[-1]
                    if abs(px - lx_o) > 1.5 and abs(py - ly_o) > 1.5:
                        # Diagonal — choose L-bend direction based on
                        # which neighbor is already axis-aligned
                        if i + 1 < len(pts):
                            nx, ny = pts[i + 1]
                            # If next point shares x with current → go horizontal first
                            if abs(nx - px) < 2:
                                out.append((px, ly_o))
                            else:
                                out.append((lx_o, py))
                        else:
                            out.append((px, ly_o))
                        changed = True
                    out.append((px, py))
                pts = out
            return pts

        points = _enforce_ortho(points)

        # Remove redundant colinear points (same x or same y in a row)
        if len(points) > 2:
            trimmed: List[Tuple[float, float]] = [points[0]]
            for i in range(1, len(points) - 1):
                px, py = points[i]
                lx_t, ly_t = trimmed[-1]
                nx, ny = points[i + 1]
                # Skip if all three are on the same horizontal or vertical line
                if abs(px - lx_t) < 2 and abs(nx - px) < 2:
                    continue
                if abs(py - ly_t) < 2 and abs(ny - py) < 2:
                    continue
                trimmed.append((px, py))
            trimmed.append(points[-1])
            points = trimmed

        edge_route_records.append({
            "points": points,
            "label": visible_label,
        })

    # ---- Render edge SVGs and labels ----
    for rec in edge_route_records:
        points = rec["points"]
        visible_label = rec["label"]

        d_parts = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
        for i in range(1, len(points)):
            d_parts.append(f"L {points[i][0]:.1f} {points[i][1]:.1f}")
        d_str = " ".join(d_parts)

        edge_svgs.append(
            f'<path d="{d_str}" fill="none" stroke="#333" stroke-width="2" '
            f'marker-end="url(#arrowhead)" '
            f'style="stroke-linejoin: round; stroke-linecap: round;"/>'
        )

        if visible_label:
            label_esc = _esc(visible_label)
            lbl_w = max(len(visible_label) * 5.5 + 12, 32)
            lbl_h = 15

            best_seg = 0
            best_len = 0.0
            for si in range(len(points) - 1):
                seg_len = (abs(points[si+1][0] - points[si][0])
                           + abs(points[si+1][1] - points[si][1]))
                if seg_len > best_len:
                    best_len = seg_len
                    best_seg = si

            lx = (points[best_seg][0] + points[best_seg + 1][0]) / 2.0
            ly = (points[best_seg][1] + points[best_seg + 1][1]) / 2.0

            def _hits_node_o(cx: float, cy: float) -> bool:
                hx1 = cx - lbl_w / 2.0 - 4
                hy1 = cy - lbl_h / 2.0 - 4
                hx2 = cx + lbl_w / 2.0 + 4
                hy2 = cy + lbl_h / 2.0 + 4
                for g2 in node_geom.values():
                    if (hx2 > g2["x"] and hx1 < g2["x"] + g2["w"]
                            and hy2 > g2["y"] and hy1 < g2["y"] + g2["h"]):
                        return True
                return False

            def _hits_label_o(cx: float, cy: float) -> bool:
                for px, py, pw, ph in placed_labels:
                    if (abs(cx - px) < (lbl_w + pw) / 2.0 + 4
                            and abs(cy - py) < (lbl_h + ph) / 2.0 + 3):
                        return True
                return False

            all_segs: List[Tuple[int, float]] = []
            for si2 in range(len(points) - 1):
                sa, sb = points[si2], points[si2 + 1]
                slen = abs(sb[0] - sa[0]) + abs(sb[1] - sa[1])
                all_segs.append((si2, slen))
            all_segs.sort(key=lambda s: -s[1])

            found_clear = False
            for seg_idx, _ in all_segs:
                sa, sb = points[seg_idx], points[seg_idx + 1]
                smx = (sa[0] + sb[0]) / 2.0
                smy = (sa[1] + sb[1]) / 2.0
                seg_horiz = abs(sa[1] - sb[1]) < 2

                for offset in [0, 20, -20, 40, -40]:
                    if seg_horiz:
                        cx, cy = smx + offset, smy - 10
                    else:
                        cx, cy = smx + 10, smy + offset
                    if not _hits_node_o(cx, cy) and not _hits_label_o(cx, cy):
                        lx, ly = cx, cy
                        found_clear = True
                        break
                if found_clear:
                    break

            placed_labels.append((lx, ly, lbl_w, lbl_h))

            edge_labels.append(
                f'<rect x="{lx - lbl_w/2:.1f}" y="{ly - lbl_h/2:.1f}" '
                f'width="{lbl_w}" height="{lbl_h}" rx="3" ry="3" '
                f'fill="#ffffff" fill-opacity="0.92" stroke="#ccc" stroke-width="0.6"/>'
                f'<text x="{lx:.1f}" y="{ly + 4:.1f}" '
                f'text-anchor="middle" font-size="8" font-weight="600" '
                f'fill="#333" font-family="-apple-system, BlinkMacSystemFont, sans-serif">'
                f'{label_esc}</text>'
            )

    # ---- Build HTML ----
    title_esc = _esc(title)
    title_x = CANVAS_PAD + lane_w / 2.0
    title_y = CANVAS_PAD

    # Build lane SVG rects (vertical header on left, like drawio swimlanes)
    lane_svgs: List[str] = []
    for lr in lane_rects:
        border_color = _darken_hex(lr["color"], 0.85)
        lx, ly, lw, lh = lr["x"], lr["y"], lr["w"], lr["h"]

        # Lane body (full rect with light bg)
        lane_svgs.append(
            f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" '
            f'rx="4" ry="4" fill="{lr["bg"]}" stroke="{border_color}" stroke-width="2"/>'
        )
        # Vertical header strip on left side
        lane_svgs.append(
            f'<rect x="{lx}" y="{ly}" width="{LANE_HEADER_W}" height="{lh}" '
            f'rx="4" ry="4" fill="{lr["color"]}"/>'
        )
        # Fix right corners of header strip (square join with body)
        lane_svgs.append(
            f'<rect x="{lx + LANE_HEADER_W - 4}" y="{ly}" width="4" height="{lh}" '
            f'fill="{lr["color"]}"/>'
        )
        # Rotated header text (bottom-to-top, centered in strip)
        text_cx = lx + LANE_HEADER_W / 2.0
        text_cy = ly + lh / 2.0
        # Shrink font if the name is too long for the lane height
        name_esc = _esc(lr["name"])
        name_len = len(lr["name"].strip())
        font_size = 12 if name_len * 8 < lh else max(9, int(lh / name_len * 0.9))
        lane_svgs.append(
            f'<text x="{text_cx:.1f}" y="{text_cy:.1f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-size="{font_size}" font-weight="700" fill="#ffffff" '
            f'font-family="-apple-system, BlinkMacSystemFont, sans-serif" '
            f'transform="rotate(-90 {text_cx:.1f} {text_cy:.1f})">'
            f'{name_esc}</text>'
        )

    # Build node SVG rects
    node_svgs: List[str] = []
    for nid, g in node_geom.items():
        n = node_by_id.get(nid, {})
        label = _esc(_short(n.get("label") or nid, 40))
        color = g.get("color", "#2196F3")
        border_color = _darken_hex(color, 0.78)

        node_svgs.append(
            f'<rect x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" '
            f'rx="10" ry="10" fill="{color}" stroke="{border_color}" stroke-width="2" '
            f'filter="url(#shadow)"/>'
        )
        node_svgs.append(
            f'<text x="{g["cx"]}" y="{g["cy"] + 4}" '
            f'text-anchor="middle" font-size="12" font-weight="700" fill="#ffffff" '
            f'font-family="-apple-system, BlinkMacSystemFont, sans-serif">'
            f'{label}</text>'
        )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>{title_esc}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #ffffff;
    width: {total_w:.0f}px;
    height: {total_h:.0f}px;
  }}
  svg {{ display: block; }}
</style>
</head>
<body>
<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" viewBox="0 0 {total_w:.0f} {total_h:.0f}">
  <defs>
    <filter id="shadow" x="-4%" y="-4%" width="108%" height="116%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000000" flood-opacity="0.12"/>
    </filter>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto" fill="#333">
      <polygon points="0 0, 10 3.5, 0 7"/>
    </marker>
  </defs>

  <!-- Background dots pattern -->
  <pattern id="dots" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="0.8" fill="#e0e0e0"/>
  </pattern>
  <rect width="100%" height="100%" fill="url(#dots)"/>

  <!-- Title bar -->
  <rect x="{CANVAS_PAD}" y="{title_y}" width="{lane_w}" height="{TITLE_H}" rx="10" ry="10" fill="#1a1a2e"/>
  <text x="{title_x:.0f}" y="{title_y + TITLE_H/2 + 6}" text-anchor="middle"
        font-size="18" font-weight="700" fill="#ffffff"
        font-family="-apple-system, BlinkMacSystemFont, sans-serif">{title_esc}</text>

  <!-- Lanes -->
  {"".join(lane_svgs)}

  <!-- Edges -->
  {"".join(edge_svgs)}

  <!-- Edge labels -->
  {"".join(edge_labels)}

  <!-- Nodes -->
  {"".join(node_svgs)}
</svg>

<script>
  window.__REACTFLOW_RENDERED__ = true;
</script>
</body>
</html>"""

    return html_content
