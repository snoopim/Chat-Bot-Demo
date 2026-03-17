# flows/drawio_from_plan.py
from __future__ import annotations

import html
import math
from typing import Dict, Any, List, Tuple, Optional, DefaultDict
from collections import defaultdict, Counter

Point = Tuple[float, float]
Seg = Tuple[str, float, float, float]  # (kind, fixed, a, b) => H: y, x1, x2 | V: x, y1, y2


# ==========================================================
# Basic helpers
# ==========================================================
def _is_hex_color(c: str) -> bool:
    if not isinstance(c, str):
        return False
    c = c.strip()
    if len(c) != 7 or not c.startswith("#"):
        return False
    return all(ch in "0123456789abcdefABCDEF" for ch in c[1:])


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


# Stronger, more saturated palette (closer to your example)
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


def _normalize_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(plan, dict):
        return {"title": " ", "lanes": [], "nodes": [], "edges": []}

    # ---------- lanes ----------
    lanes = plan.get("lanes") or []
    if lanes and isinstance(lanes, list) and isinstance(lanes[0], str):
        new_lanes: List[Dict[str, Any]] = []
        for i, name in enumerate(lanes):
            lid = _slug_lane_id(str(name), i)
            new_lanes.append({"id": lid, "name": str(name), "color": LANE_COLORS[i % len(LANE_COLORS)]})
        plan["lanes"] = new_lanes
        lanes = new_lanes

    if not lanes or not isinstance(lanes, list) or not isinstance(lanes[0], dict):
        plan["lanes"] = [{"id": "lane_default", "name": "Lane", "color": "#f5f5f5"}]
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

    # ---------- nodes ----------
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

    # ---------- edges ----------
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

        # prefer data_label variants
        if e.get("data_label") in (None, ""):
            for k in ("dataLabel", "datalabel", "data-label", "data", "data_type", "datatype"):
                v = e.get(k)
                if isinstance(v, str) and v.strip():
                    e["data_label"] = v.strip()
                    break
            else:
                e["data_label"] = ""

    # dedupe same (from,to) pairs
    merged: Dict[tuple, Dict[str, Any]] = {}
    for e in edges:
        if not isinstance(e, dict):
            continue
        key = (e.get("from"), e.get("to"))
        if key not in merged:
            merged[key] = dict(e)
    plan["edges"] = list(merged.values())
    return plan


# ==========================================================
# Geometry helpers
# ==========================================================
def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _dedupe_points(points: List[Point]) -> List[Point]:
    out: List[Point] = []
    for p in points:
        if not out or (abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6):
            out.append(p)
    return out


def _anchor_point_on_box(g: Dict[str, float], ax: float, ay: float) -> Point:
    return (g["x"] + ax * g["w"], g["y"] + ay * g["h"])


def _push_out_from_box(g: Dict[str, float], ax: float, ay: float, margin: float) -> Point:
    x, y = _anchor_point_on_box(g, ax, ay)
    if ax <= 0.01:
        x -= margin
    elif ax >= 0.99:
        x += margin
    if ay <= 0.01:
        y -= margin
    elif ay >= 0.99:
        y += margin
    return (x, y)


def _port_side(ax: float, ay: float) -> str:
    if ax <= 0.01:
        return "west"
    if ax >= 0.99:
        return "east"
    if ay <= 0.01:
        return "north"
    if ay >= 0.99:
        return "south"
    return "east"


def _anchors_from_geom(src_g: Dict[str, float], tgt_g: Dict[str, float]) -> Tuple[float, float, float, float]:
    sx = src_g["x"] + src_g["w"] / 2.0
    sy = src_g["y"] + src_g["h"] / 2.0
    tx = tgt_g["x"] + tgt_g["w"] / 2.0
    ty = tgt_g["y"] + tgt_g["h"] / 2.0
    dx = tx - sx
    dy = ty - sy
    if abs(dx) >= abs(dy):
        return (1.0, 0.5, 0.0, 0.5) if dx >= 0 else (0.0, 0.5, 1.0, 0.5)
    return (0.5, 1.0, 0.5, 0.0) if dy >= 0 else (0.5, 0.0, 0.5, 1.0)


def _rects_overlap(a: Dict[str, float], b: Dict[str, float]) -> bool:
    return not (
        a["x"] + a["w"] <= b["x"]
        or a["x"] >= b["x"] + b["w"]
        or a["y"] + a["h"] <= b["y"]
        or a["y"] >= b["y"] + b["h"]
    )


def _rect_center(r: Dict[str, float]) -> Tuple[float, float]:
    return (r["x"] + r["w"] / 2.0, r["y"] + r["h"] / 2.0)


def _dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ==========================================================
# Lane ordering
# ==========================================================
def _lane_order_three(lanes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    name_to_rank = {
        "people": 0,
        "person": 0,
        "roles": 0,
        "systems": 1,
        "system": 1,
        "partners": 2,
        "partner": 2,
        "external": 2,
    }
    ranked = []
    for ln in lanes:
        nm = (ln.get("name") or "").strip().lower()
        ranked.append((name_to_rank.get(nm, 99), ln))
    ranked.sort(key=lambda x: x[0])
    if any(r[0] != 99 for r in ranked):
        return [r[1] for r in ranked]
    return lanes


# ==========================================================
# Column alignment (min edge span)
# ==========================================================
def _assign_columns_min_edge_span(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    lane_ids: List[str],
) -> Dict[str, int]:
    node_by_id = {n["id"]: n for n in nodes if isinstance(n, dict) and n.get("id")}
    lane_of = {nid: node_by_id[nid].get("lane") for nid in node_by_id.keys()}

    out_to: DefaultDict[str, List[str]] = defaultdict(list)
    in_from: DefaultDict[str, List[str]] = defaultdict(list)
    for e in edges:
        if not isinstance(e, dict):
            continue
        a = (e.get("from") or "").strip()
        b = (e.get("to") or "").strip()
        if a in node_by_id and b in node_by_id and a != b:
            out_to[a].append(b)
            in_from[b].append(a)

    lane_nodes: Dict[str, List[str]] = {lid: [] for lid in lane_ids}
    for nid, ln in lane_of.items():
        if ln in lane_nodes:
            lane_nodes[ln].append(nid)

    spine_lane = lane_ids[1] if len(lane_ids) >= 3 else lane_ids[0]
    spine = lane_nodes.get(spine_lane, [])[:]

    def _key(nid: str) -> Tuple[str, str]:
        lbl = (node_by_id[nid].get("label") or "").strip().lower()
        return (lbl, nid)

    spine.sort(key=_key)

    col_of: Dict[str, int] = {}
    for i, nid in enumerate(spine):
        col_of[nid] = i

    def best_spine_col(nid: str) -> Optional[int]:
        candidates = []
        for nb in out_to.get(nid, []) + in_from.get(nid, []):
            if lane_of.get(nb) == spine_lane and nb in col_of:
                candidates.append(col_of[nb])
        if not candidates:
            return None
        c = Counter(candidates)
        most = c.most_common()
        top_freq = most[0][1]
        top_cols = sorted([k for (k, v) in most if v == top_freq])
        return top_cols[0]

    for lid in lane_ids:
        if lid == spine_lane:
            continue
        others = lane_nodes.get(lid, [])[:]
        others.sort(key=_key)
        fallback = 0
        for nid in others:
            sc = best_spine_col(nid)
            if sc is None:
                sc = fallback
                fallback += 1
            col_of[nid] = sc

    return col_of


# ==========================================================
# Enforce lane rule: max ONE lane boundary per edge
# ==========================================================
def _enforce_max_one_lane_boundary(
    lanes: List[Dict[str, Any]],
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    name_to_rank = {
        "people": 0,
        "person": 0,
        "roles": 0,
        "systems": 1,
        "system": 1,
        "partners": 2,
        "partner": 2,
        "external": 2,
    }

    lane_rank: Dict[str, int] = {}
    for i, ln in enumerate(lanes):
        lid = (ln.get("id") or "").strip()
        nm = (ln.get("name") or "").strip().lower()
        if lid:
            lane_rank[lid] = name_to_rank.get(nm, i)

    node_by_id = {n.get("id"): n for n in nodes if isinstance(n, dict) and n.get("id")}
    lane_of = {nid: (node_by_id[nid].get("lane") or "") for nid in node_by_id}

    systems_lane_ids = [lid for lid, r in lane_rank.items() if r == 1]
    systems_nodes = [nid for nid in node_by_id.keys() if lane_of.get(nid) in set(systems_lane_ids)]
    if not systems_nodes:
        return edges

    out_to: DefaultDict[str, List[str]] = defaultdict(list)
    in_from: DefaultDict[str, List[str]] = defaultdict(list)
    for e in edges:
        if not isinstance(e, dict):
            continue
        a = e.get("from")
        b = e.get("to")
        if a in node_by_id and b in node_by_id and a != b:
            out_to[a].append(b)
            in_from[b].append(a)

    def r_of(nid: str) -> Optional[int]:
        lid = lane_of.get(nid)
        if not lid:
            return None
        return lane_rank.get(lid)

    def pick_bridge(src: str, tgt: str) -> str:
        src_neighbors = set(out_to.get(src, []) + in_from.get(src, []))
        cand = [n for n in systems_nodes if n in src_neighbors]
        if cand:
            return sorted(cand)[0]

        tgt_neighbors = set(out_to.get(tgt, []) + in_from.get(tgt, []))
        cand = [n for n in systems_nodes if n in tgt_neighbors]
        if cand:
            return sorted(cand)[0]

        return sorted(systems_nodes)[0]

    rewritten: List[Dict[str, Any]] = []
    for e in edges:
        if not isinstance(e, dict):
            continue
        src = e.get("from")
        tgt = e.get("to")
        if src not in node_by_id or tgt not in node_by_id or src == tgt:
            rewritten.append(e)
            continue

        rs = r_of(src)
        rt = r_of(tgt)
        if rs is None or rt is None:
            rewritten.append(e)
            continue

        if abs(rs - rt) <= 1:
            rewritten.append(e)
            continue

        bridge = pick_bridge(src, tgt)
        dl = e.get("data_label", "") or ""
        lbl = e.get("label", "") or ""

        rewritten.append({"from": src, "to": bridge, "label": lbl, "data_label": dl})
        rewritten.append({"from": bridge, "to": tgt, "label": lbl, "data_label": dl})

    merged: Dict[tuple, Dict[str, Any]] = {}
    for e in rewritten:
        key = (e.get("from"), e.get("to"))
        if key not in merged:
            merged[key] = e
    return list(merged.values())


# ==========================================================
# Edge separation + validation
# ==========================================================
def _route_segments(points: List[Point]) -> List[Seg]:
    segs: List[Seg] = []
    if len(points) < 2:
        return segs
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        if abs(y1 - y2) < 1e-6:
            a, b = (x1, x2) if x1 <= x2 else (x2, x1)
            segs.append(("H", y1, a, b))
        elif abs(x1 - x2) < 1e-6:
            a, b = (y1, y2) if y1 <= y2 else (y2, y1)
            segs.append(("V", x1, a, b))
        else:
            segs.append(("X", 0.0, 0.0, 0.0))
    return segs


def _ranges_overlap(a1: float, a2: float, b1: float, b2: float, tol: float) -> bool:
    return not (a2 <= b1 + tol or b2 <= a1 + tol)


def _seg_overlaps(seg: Seg, occupied: List[Seg], tol: float) -> bool:
    kind, fixed, a, b = seg
    if kind not in ("H", "V"):
        return True
    for okind, ofixed, oa, ob in occupied:
        if okind != kind:
            continue
        if abs(ofixed - fixed) > tol:
            continue
        if _ranges_overlap(a, b, oa, ob, tol):
            return True
    return False


def _route_overlaps(points: List[Point], occupied: List[Seg], tol: float) -> bool:
    for seg in _route_segments(points):
        if _seg_overlaps(seg, occupied, tol=tol):
            return True
    return False


def _shift_route(points: List[Point], dx: float, dy: float) -> List[Point]:
    return _dedupe_points([(x + dx, y + dy) for (x, y) in points])


def _generate_offsets(step: float, tries: int) -> List[float]:
    out = [0.0]
    for i in range(1, tries + 1):
        out.append(step * i)
        out.append(-step * i)
    return out


def _prefer_shift_axis(points: List[Point]) -> str:
    v = 0.0
    h = 0.0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        if abs(x1 - x2) < 1e-6:
            v += abs(y2 - y1)
        elif abs(y1 - y2) < 1e-6:
            h += abs(x2 - x1)
    return "x" if v >= h else "y"


def _inflate_rect(r: Dict[str, float], pad: float) -> Dict[str, float]:
    return {"x": r["x"] - pad, "y": r["y"] - pad, "w": r["w"] + 2 * pad, "h": r["h"] + 2 * pad}


def _seg_hits_rect_h(x1: float, x2: float, y: float, r: Dict[str, float]) -> bool:
    lo, hi = (x1, x2) if x1 <= x2 else (x2, x1)
    if y < r["y"] or y > r["y"] + r["h"]:
        return False
    return not (hi <= r["x"] or lo >= r["x"] + r["w"])


def _seg_hits_rect_v(x: float, y1: float, y2: float, r: Dict[str, float]) -> bool:
    lo, hi = (y1, y2) if y1 <= y2 else (y2, y1)
    if x < r["x"] or x > r["x"] + r["w"]:
        return False
    return not (hi <= r["y"] or lo >= r["y"] + r["h"])


def _path_hits_rects(points: List[Point], rects: List[Dict[str, float]]) -> bool:
    if len(points) < 2:
        return False
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        if abs(x1 - x2) < 1e-6:
            for r in rects:
                if _seg_hits_rect_v(x1, y1, y2, r):
                    return True
        elif abs(y1 - y2) < 1e-6:
            for r in rects:
                if _seg_hits_rect_h(x1, x2, y1, r):
                    return True
        else:
            return True
    return False


def separate_routes_with_validation(
    edge_records: List[Dict[str, Any]],
    node_rects: List[Dict[str, float]],
    tolerance: float = 6.0,
    offset_step: float = 10.0,
    offset_tries: int = 10,
    keep_ends_fixed: bool = True,
    clamp_x: Optional[Tuple[float, float]] = None,
    clamp_y: Optional[Tuple[float, float]] = None,
) -> None:
    occupied: List[Seg] = []
    offsets = _generate_offsets(offset_step, offset_tries)

    def _apply_clamp(points: List[Point]) -> List[Point]:
        if not points:
            return points
        out: List[Point] = []
        for (x, y) in points:
            if clamp_x:
                x = _clamp(x, clamp_x[0], clamp_x[1])
            if clamp_y:
                y = _clamp(y, clamp_y[0], clamp_y[1])
            out.append((x, y))
        return _dedupe_points(out)

    for rec in edge_records:
        r: List[Point] = _dedupe_points(rec.get("route_pts") or [])
        if len(r) < 2:
            rec["route_pts"] = r
            continue

        axis = _prefer_shift_axis(r)
        best: Optional[List[Point]] = None

        for off in offsets:
            if off == 0.0:
                cand = r
            else:
                dx = off if axis == "x" else 0.0
                dy = 0.0 if axis == "x" else off
                cand = _shift_route(r, dx, dy)

                if keep_ends_fixed and len(cand) >= 2:
                    cand[0] = r[0]
                    cand[-1] = r[-1]
                    cand = _dedupe_points(cand)

            cand = _apply_clamp(cand)

            if _route_overlaps(cand, occupied, tol=tolerance):
                continue
            # IMPORTANT: avoid node collisions (stops edges going underneath unrelated nodes)
            if _path_hits_rects(cand, node_rects):
                continue

            best = cand
            break

        if best is None:
            best = _apply_clamp(r)

        rec["route_pts"] = best
        occupied.extend(_route_segments(best))


# ==========================================================
# Dogleg rule (avoid east->south immediately)
# ==========================================================
def _add_exit_dogleg_if_needed(points: List[Point], src_side: str, dogleg: float) -> List[Point]:
    if len(points) < 3:
        return points
    p0, p1 = points[0], points[1]
    vertical_immediate = abs(p0[0] - p1[0]) < 1e-6 and abs(p0[1] - p1[1]) > 1e-6
    if not vertical_immediate:
        return points
    if src_side not in ("east", "west"):
        return points
    dx = dogleg if src_side == "east" else -dogleg
    p1b = (p0[0] + dx, p0[1])
    p1c = (p0[0] + dx, p1[1])
    return _dedupe_points([p0, p1b, p1c] + points[2:])


def _add_entry_dogleg_if_needed(points: List[Point], tgt_side: str, dogleg: float) -> List[Point]:
    if len(points) < 3:
        return points
    p_last = points[-1]
    p_prev = points[-2]
    vertical_immediate = abs(p_prev[0] - p_last[0]) < 1e-6 and abs(p_prev[1] - p_last[1]) > 1e-6
    if not vertical_immediate:
        return points
    if tgt_side not in ("east", "west"):
        return points
    dx = dogleg if tgt_side == "west" else -dogleg
    p_mid1 = (p_last[0] + dx, p_prev[1])
    p_mid2 = (p_last[0] + dx, p_last[1])
    return _dedupe_points(points[:-2] + [p_mid1, p_mid2, p_last])


# ==========================================================
# Per-node port offset (prevent edges leaving same node at same position)
# ==========================================================
def _offset_seq_px(k: int, step_px: float) -> float:
    if k <= 0:
        return 0.0
    m = (k + 1) // 2
    sign = 1.0 if (k % 2 == 1) else -1.0
    return sign * (m * step_px)


def _apply_port_offset(
    g: Dict[str, float],
    side: str,
    base_ax: float,
    base_ay: float,
    offset_px: float,
) -> Tuple[float, float]:
    ax, ay = base_ax, base_ay
    MIN_A = 0.15
    MAX_A = 0.85

    if side in ("east", "west"):
        if g["h"] > 1e-6:
            ay = ay + (offset_px / g["h"])
            ay = _clamp(ay, MIN_A, MAX_A)
        ax = 1.0 if side == "east" else 0.0
    elif side in ("north", "south"):
        if g["w"] > 1e-6:
            ax = ax + (offset_px / g["w"])
            ax = _clamp(ax, MIN_A, MAX_A)
        ay = 0.0 if side == "north" else 1.0

    return ax, ay


# ==========================================================
# Label point along polyline
# ==========================================================
def _polyline_len(points: List[Point]) -> float:
    if len(points) < 2:
        return 0.0
    s = 0.0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        s += abs(x2 - x1) + abs(y2 - y1)
    return s


def _point_at_fraction(points: List[Point], t: float) -> Tuple[float, float, Tuple[float, float]]:
    """
    Return (x,y,normal) at ~fraction t along the polyline length.
    Normal is perpendicular to local segment:
      - if horizontal, normal points up (0,-1)
      - if vertical, normal points right (1,0)
    """
    t = _clamp(t, 0.10, 0.90)
    total = _polyline_len(points)
    if total <= 1e-6 or len(points) < 2:
        return points[0][0], points[0][1], (0.0, -1.0)

    target = total * t
    acc = 0.0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        seg = abs(x2 - x1) + abs(y2 - y1)
        if acc + seg >= target:
            mx = (x1 + x2) / 2.0
            my = (y1 + y2) / 2.0
            normal = (0.0, -1.0) if abs(y1 - y2) < 1e-6 else (1.0, 0.0)
            return mx, my, normal
        acc += seg

    x1, y1 = points[-2]
    x2, y2 = points[-1]
    normal = (0.0, -1.0) if abs(y1 - y2) < 1e-6 else (1.0, 0.0)
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0, normal


# ==========================================================
# Reserve horizontal "bus" segments
# ==========================================================
def _hseg(y: float, x1: float, x2: float) -> Seg:
    a, b = (x1, x2) if x1 <= x2 else (x2, x1)
    return ("H", float(y), float(a), float(b))


def _label_fraction_for_index(i: int) -> float:
    # keep labels close to mid-edge by default (less drifting)
    base = 0.50
    jig = [-0.06, 0.06, -0.12, 0.12, 0.0, 0.18, -0.18]
    return _clamp(base + jig[i % len(jig)], 0.18, 0.82)


def _pick_non_overlapping_bus_y(
    base_y: float,
    sx: float,
    ex: float,
    safe_top: float,
    safe_bot: float,
    node_rects_inflated: List[Dict[str, float]],
    occupied_bus_hsegs: List[Seg],
    step: float = 10.0,
    tries: int = 18,
    tol: float = 6.0,
) -> float:
    cand_offsets = _generate_offsets(step, tries)
    for off in cand_offsets:
        y = _clamp(base_y + off, safe_top, safe_bot)

        if _path_hits_rects([(sx, y), (ex, y)], node_rects_inflated):
            continue

        if _seg_overlaps(_hseg(y, sx, ex), occupied_bus_hsegs, tol=tol):
            continue

        return y

    return _clamp(base_y, safe_top, safe_bot)


# ==========================================================
# MAIN
# ==========================================================
def build_drawio_from_plan(plan: dict) -> str:
    plan = _normalize_plan(plan)

    title = _esc(plan.get("title") or "Process Flow")
    lanes = plan.get("lanes") or []
    nodes = plan.get("nodes") or []
    edges = plan.get("edges") or []

    # ----------------------------------------------------------
    # Keep only used lanes
    # ----------------------------------------------------------
    used_lane_ids = {n.get("lane") for n in nodes if isinstance(n, dict) and n.get("lane")}
    lanes = [ln for ln in lanes if isinstance(ln, dict) and ln.get("id") in used_lane_ids]

    MAX_LANES = 3
    if len(lanes) > MAX_LANES:
        allowed_lane_ids = {ln["id"] for ln in lanes[:MAX_LANES]}
        fallback_lane = lanes[0]["id"]
        lanes = lanes[:MAX_LANES]
        for n in nodes:
            if isinstance(n, dict) and n.get("lane") not in allowed_lane_ids:
                n["lane"] = fallback_lane

    if not lanes:
        lanes = [{"id": "lane_default", "name": "Lane", "color": "#E3F2FD"}]
        for n in nodes:
            if isinstance(n, dict):
                n["lane"] = "lane_default"

    lanes = _lane_order_three(lanes)

    lane_ids = [ln.get("id") for ln in lanes if ln.get("id")]
    lane_ids = [lid for lid in lane_ids if lid]

    for i, ln in enumerate(lanes):
        if not _is_hex_color(ln.get("color")):
            ln["color"] = LANE_COLORS[i % len(LANE_COLORS)]

    default_lane = lane_ids[0] if lane_ids else "lane_default"
    for n in nodes:
        if isinstance(n, dict) and n.get("lane") not in set(lane_ids):
            n["lane"] = default_lane

    # enforce one-lane-boundary rule
    edges = _enforce_max_one_lane_boundary(lanes=lanes, nodes=nodes, edges=edges)

    # ----------------------------------------------------------
    # Node map
    # ----------------------------------------------------------
    node_by_id: Dict[str, Dict[str, Any]] = {}
    for n in nodes:
        if isinstance(n, dict) and n.get("id"):
            node_by_id[n["id"]] = n

    # ----------------------------------------------------------
    # Shape inference
    # ----------------------------------------------------------
    def _node_shape(nid: str, n: Dict[str, Any]) -> str:
        label = (n.get("label") or "").strip().lower()

        lane_name = ""
        for ln in lanes:
            if ln.get("id") == n.get("lane"):
                lane_name = (ln.get("name") or "").strip().lower()
                break

        actor_words = {
            "supplier", "customer", "user", "employee", "bank", "vendor",
            "partner", "client", "manager", "admin", "staff", "finance team",
            "data subject", "processor", "controller", "external"
        }

        if any(w == label or w in label for w in actor_words):
            return "actor"

        if lane_name in {"external", "people", "person", "roles", "partners", "partner"}:
            return "actor"

        return "rounded"

    # ----------------------------------------------------------
    # Style helpers
    # ----------------------------------------------------------
    def _darken_hex(color: str, factor: float = 0.82) -> str:
        if not _is_hex_color(color):
            return "#a0a0a0"
        c = color.lstrip("#")
        r = max(0, min(255, int(int(c[0:2], 16) * factor)))
        g = max(0, min(255, int(int(c[2:4], 16) * factor)))
        b = max(0, min(255, int(int(c[4:6], 16) * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _lane_style(fill: str) -> str:
        stroke = _darken_hex(fill, 0.82)
        return (
            "swimlane;"
            "rounded=0;"
            "whiteSpace=wrap;"
            "html=1;"
            f"startSize={LANE_HEADER_H};"
            "horizontal=0;"
            "align=left;"
            "verticalAlign=top;"
            "fontStyle=1;"
            "fontSize=12;"
            f"fillColor={fill};"
            f"strokeColor={stroke};"
            "fontColor=#333333;"
            "collapsible=0;"
        )

    def _node_style(fill: str, shape_kind: str) -> str:
        stroke = _darken_hex(fill, 0.78)
        return (
            "rounded=1;"
            "whiteSpace=wrap;"
            "html=1;"
            "fontColor=#000000;"
            "align=center;"
            "verticalAlign=middle;"
            "fontStyle=1;"
            "fontSize=11;"
            f"fillColor={fill};"
            f"strokeColor={stroke};"
            + ("strokeWidth=2;" if shape_kind == "actor" else "strokeWidth=1.5;")
        )

    # ----------------------------------------------------------
    # Label helpers
    # ----------------------------------------------------------
    def _nounify_edge_label(label: str, data_label: str) -> str:
        dl = (data_label or "").strip()
        lb = (label or "").strip()

        if dl and len(dl) > 2:
            return dl

        low = lb.lower()
        verb_to_noun = {
            "submit": "Submission",
            "store": "Storage",
            "send": "Transfer",
            "sync": "Synchronization",
            "publish": "Publication",
            "track": "Tracking",
            "create": "Creation",
            "view": "Access",
            "update": "Update",
            "record": "Record",
            "run": "Execution",
            "export": "Export",
            "import": "Import",
            "migrate": "Migration",
            "reconcile": "Reconciliation",
            "approve": "Approval",
            "review": "Review",
            "validate": "Validation",
            "check": "Check",
        }

        if low in verb_to_noun:
            return verb_to_noun[low]

        if not lb:
            return ""

        return lb[:1].upper() + lb[1:]

    # ----------------------------------------------------------
    # Layout constants
    # ----------------------------------------------------------
    START_X = 40
    START_Y = 40
    TITLE_H = 55
    LANE_GAP = 30
    LANE_HEADER_H = 26

    NODE_H = 56
    PAD_X = 90
    PAD_Y = 18
    ROW_GAP = 34

    PORT_MARGIN = 14.0
    PORT_OFFSET_STEP_PX = 12.0
    PORT_OFFSET_TRIES = 8

    LANE_WIDTH = 1100.0
    SAFE_X_MIN = START_X + 20.0
    SAFE_X_MAX = START_X + LANE_WIDTH - 20.0

    # ----------------------------------------------------------
    # Node sizing
    # ----------------------------------------------------------
    lane_nodes: DefaultDict[str, List[str]] = defaultdict(list)
    lane_label_lens: DefaultDict[str, int] = defaultdict(int)

    for nid, n in node_by_id.items():
        lid = n.get("lane") or default_lane
        lane_nodes[lid].append(nid)
        lane_label_lens[lid] = max(lane_label_lens[lid], len((n.get("label") or "").strip()))

    NODE_W_BY_LANE: Dict[str, float] = {}
    for lid in lane_ids:
        max_len = lane_label_lens.get(lid, 10)
        NODE_W_BY_LANE[lid] = max(130.0, min(230.0, float(max_len * 7 + 36)))

    # ----------------------------------------------------------
    # Column assignment
    # ----------------------------------------------------------
    col_of = _assign_columns_min_edge_span(
        nodes=[{"id": n["id"], "lane": n.get("lane"), "label": n.get("label")} for n in node_by_id.values()],
        edges=edges,
        lane_ids=lane_ids,
    )

    def _node_sort_key(nid: str) -> Tuple[str, str]:
        lbl = (node_by_id[nid].get("label") or "").strip().lower()
        return (lbl, nid)

    # ----------------------------------------------------------
    # Better lane-wise placement
    # ----------------------------------------------------------
    lane_ordered_nodes: Dict[str, List[str]] = {}
    lane_cols_override: Dict[str, Dict[str, int]] = {}

    for lid in lane_ids:
        nids = lane_nodes.get(lid, [])[:]
        nids.sort(key=_node_sort_key)
        lane_ordered_nodes[lid] = nids

        unique_cols = sorted({int(col_of.get(nid, 0)) for nid in nids})

        if len(unique_cols) <= 1 and len(nids) >= 2:
            lane_cols_override[lid] = {}
            for i, nid in enumerate(nids):
                lane_cols_override[lid][nid] = i
        else:
            lane_cols_override[lid] = {nid: int(col_of.get(nid, 0)) for nid in nids}

    row_of: Dict[str, int] = {}
    max_rows_by_lane: DefaultDict[str, int] = defaultdict(int)

    for lid in lane_ids:
        nids = lane_ordered_nodes.get(lid, [])
        if not nids:
            continue

        cols_for_lane = lane_cols_override[lid]
        unique_cols = sorted(set(cols_for_lane.values()))

        if len(unique_cols) == len(nids):
            for nid in nids:
                row_of[nid] = 0
            max_rows_by_lane[lid] = 1
        else:
            buckets: DefaultDict[int, List[str]] = defaultdict(list)
            for nid in nids:
                buckets[cols_for_lane[nid]].append(nid)

            for c, cnids in buckets.items():
                cnids.sort(key=_node_sort_key)
                for r_idx, nid in enumerate(cnids):
                    row_of[nid] = r_idx
                    max_rows_by_lane[lid] = max(max_rows_by_lane[lid], r_idx + 1)

    def _lane_height(lid: str) -> float:
        rows = max(1, int(max_rows_by_lane.get(lid, 1)))
        content_h = rows * NODE_H + (rows - 1) * ROW_GAP
        return float(max(150, int(LANE_HEADER_H + PAD_Y * 2 + content_h + 24)))

    # ----------------------------------------------------------
    # Build cells
    # ----------------------------------------------------------
    cells: List[str] = []
    cid = 2

    def next_id() -> int:
        nonlocal cid
        x = cid
        cid += 1
        return x

    lane_cell_id_by_lane: Dict[str, int] = {}
    lane_top_y: Dict[str, float] = {}
    lane_bottom_y: Dict[str, float] = {}

    # title
    title_id = next_id()
    cells.append(
        f'<mxCell id="{title_id}" value="{title}" '
        f'style="rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;'
        f'fontStyle=1;fontSize=16;strokeWidth=2;fillColor=#1a1a2e;strokeColor=#16213e;fontColor=#ffffff;" '
        f'vertex="1" parent="1">'
        f'<mxGeometry x="{START_X}" y="{START_Y}" width="{LANE_WIDTH:.1f}" height="{TITLE_H}" as="geometry"/>'
        f"</mxCell>"
    )

    # lanes
    lane_y = START_Y + TITLE_H + 20
    for ln in lanes:
        lane_id = (ln.get("id") or "").strip() or "lane_default"
        lane_name = _esc(ln.get("name") or lane_id or "Lane")
        lane_color = (ln.get("color") or "#f5f5f5").strip()
        lane_h = _lane_height(lane_id)

        lid_cell = next_id()
        lane_cell_id_by_lane[lane_id] = lid_cell
        lane_top_y[lane_id] = float(lane_y)
        lane_bottom_y[lane_id] = float(lane_y + lane_h)

        cells.append(
            f'<mxCell id="{lid_cell}" value="{lane_name}" '
            f'style="{_lane_style(lane_color)}" vertex="1" parent="1">'
            f'<mxGeometry x="{START_X:.1f}" y="{lane_y:.1f}" width="{LANE_WIDTH:.1f}" height="{lane_h:.1f}" as="geometry"/>'
            f"</mxCell>"
        )
        lane_y += lane_h + LANE_GAP

    # ----------------------------------------------------------
    # Node geometries
    # ----------------------------------------------------------
    node_cell_id_by_node: Dict[str, int] = {}
    node_geom: Dict[str, Dict[str, float]] = {}
    node_layout: List[Dict[str, Any]] = []

    for lid in lane_ids:
        nids = lane_ordered_nodes.get(lid, [])
        if not nids:
            continue

        node_w = float(NODE_W_BY_LANE.get(lid, 170.0))
        cols_for_lane = lane_cols_override[lid]
        unique_cols = sorted(set(cols_for_lane.values()))

        left = START_X + PAD_X + node_w / 2.0
        right = START_X + LANE_WIDTH - PAD_X - node_w / 2.0

        if len(unique_cols) == 1:
            col_centers = {unique_cols[0]: (left + right) / 2.0}
        else:
            step = (right - left) / float(len(unique_cols) - 1)
            col_centers = {c: left + i * step for i, c in enumerate(unique_cols)}

        for nid in nids:
            n = node_by_id[nid]
            mx_node_id = next_id()
            node_cell_id_by_node[nid] = mx_node_id

            cidx = cols_for_lane[nid]
            r_idx = int(row_of.get(nid, 0))

            cx = col_centers.get(cidx, (left + right) / 2.0)
            abs_x = float(cx - node_w / 2.0)
            abs_y = float(lane_top_y[lid] + LANE_HEADER_H + PAD_Y + r_idx * (NODE_H + ROW_GAP))

            fill = (next((ln.get("color") for ln in lanes if ln.get("id") == lid), "#ffffff") or "#ffffff").strip()
            if not _is_hex_color(fill):
                fill = "#ffffff"

            shape_kind = _node_shape(nid, n)
            label = _esc(_short(n.get("label") or nid or "Step", 40))

            geom = {"x": abs_x, "y": abs_y, "w": float(node_w), "h": float(NODE_H), "lane_id": lid, "lane_color": fill}
            node_geom[nid] = geom

            rel_x = abs_x - START_X
            rel_y = abs_y - lane_top_y[lid]

            node_layout.append(
                {
                    "mx_id": mx_node_id,
                    "label": label,
                    "lane_id": lid,
                    "x": rel_x,
                    "y": rel_y,
                    "abs_x": abs_x,
                    "abs_y": abs_y,
                    "w": float(node_w),
                    "h": float(NODE_H),
                    "fill": fill,
                    "shape": shape_kind,
                    "parent": lane_cell_id_by_lane[lid],
                }
            )

    # ----------------------------------------------------------
    # Edge routing
    # ----------------------------------------------------------
    node_rects_inflated = [_inflate_rect(g, 34.0) for g in node_geom.values()]

    edge_style_base = (
        "edgeStyle=orthogonalEdgeStyle;"
        "rounded=1;"
        "orthogonalLoop=1;"
        "jettySize=auto;"
        "html=1;"
        "strokeColor=#000000;"
        "strokeWidth=2;"
        "startArrow=none;"
        "endArrow=classic;"
        "endFill=1;"
        "endSize=10;"
        "exitPerimeter=1;"
        "entryPerimeter=1;"
        "labelBackgroundColor=#ffffff;"
        "labelBorderColor=none;"
        "fontSize=9;"
        "align=center;"
        "verticalAlign=middle;"
        "spacing=2;"
    )

    occupied_bus_hsegs: List[Seg] = []
    edge_records: List[Dict[str, Any]] = []

    # side fanout counters to reduce corridor overlap
    right_side_fanout_counter: DefaultDict[str, int] = defaultdict(int)
    left_side_fanout_counter: DefaultDict[str, int] = defaultdict(int)

    # same-lane bus staggering to stop parallel edges using same y
    same_lane_bus_counter: DefaultDict[Tuple[str, str, str], int] = defaultdict(int)

    # separate vertical drops near same target area
    vertical_target_counter: DefaultDict[Tuple[str, str], int] = defaultdict(int)

    # NEW: separate repeated exits/entries on the same node side
    out_port_counter: DefaultDict[Tuple[str, str], int] = defaultdict(int)
    in_port_counter: DefaultDict[Tuple[str, str], int] = defaultdict(int)

    def _same_lane_bus_y_candidates(lane_id: str, base_y: float, step: float, tries: int) -> List[float]:
        offs = _generate_offsets(step, tries)
        return [base_y + o for o in offs]

    def _bus_y_ok(y: float, x1: float, x2: float) -> bool:
        for r in node_rects_inflated:
            if _seg_hits_rect_h(x1, x2, y, r):
                return False
        return True

    for e in edges:
        if not isinstance(e, dict):
            continue

        src_plan = (e.get("from") or "").strip()
        tgt_plan = (e.get("to") or "").strip()
        if not src_plan or not tgt_plan or src_plan == tgt_plan:
            continue

        src_cell = node_cell_id_by_node.get(src_plan)
        tgt_cell = node_cell_id_by_node.get(tgt_plan)
        if not src_cell or not tgt_cell:
            continue

        src_g = node_geom.get(src_plan)
        tgt_g = node_geom.get(tgt_plan)
        if not src_g or not tgt_g:
            continue

        # ------------------------------------------------------
        # Anchor side + per-node-side port offset
        # ------------------------------------------------------
        base_ex_x, base_ex_y, base_en_x, base_en_y = _anchors_from_geom(src_g, tgt_g)
        src_side = _port_side(base_ex_x, base_ex_y)
        tgt_side = _port_side(base_en_x, base_en_y)

        out_k = out_port_counter[(src_plan, src_side)]
        out_port_counter[(src_plan, src_side)] += 1

        in_k = in_port_counter[(tgt_plan, tgt_side)]
        in_port_counter[(tgt_plan, tgt_side)] += 1

        out_off_px = _offset_seq_px(min(out_k, PORT_OFFSET_TRIES), PORT_OFFSET_STEP_PX)
        in_off_px = _offset_seq_px(min(in_k, PORT_OFFSET_TRIES), PORT_OFFSET_STEP_PX)

        ex_x, ex_y = _apply_port_offset(src_g, src_side, base_ex_x, base_ex_y, out_off_px)
        en_x, en_y = _apply_port_offset(tgt_g, tgt_side, base_en_x, base_en_y, in_off_px)

        # fanout offsets for crowded left/right side corridors
        src_fan_px = 0.0
        tgt_fan_px = 0.0

        if src_side == "east":
            src_fan_px = 18.0 * right_side_fanout_counter[src_plan]
            right_side_fanout_counter[src_plan] += 1
        elif src_side == "west":
            src_fan_px = 18.0 * left_side_fanout_counter[src_plan]
            left_side_fanout_counter[src_plan] += 1

        if tgt_side == "east":
            tgt_fan_px = 18.0 * right_side_fanout_counter[tgt_plan]
            right_side_fanout_counter[tgt_plan] += 1
        elif tgt_side == "west":
            tgt_fan_px = 18.0 * left_side_fanout_counter[tgt_plan]
            left_side_fanout_counter[tgt_plan] += 1

        anchor_style = (
            f"exitX={ex_x:.2f};exitY={ex_y:.2f};exitDx=0;exitDy=0;"
            f"entryX={en_x:.2f};entryY={en_y:.2f};entryDx=0;entryDy=0;"
        )
        port_constraints = f"sourcePortConstraint={src_side};targetPortConstraint={tgt_side};"

        start = _push_out_from_box(src_g, ex_x, ex_y, PORT_MARGIN)
        end = _push_out_from_box(tgt_g, en_x, en_y, PORT_MARGIN)

        # apply fanout to start/end
        if src_side == "east":
            start = (start[0] + src_fan_px, start[1])
        elif src_side == "west":
            start = (start[0] - src_fan_px, start[1])

        if tgt_side == "east":
            end = (end[0] + tgt_fan_px, end[1])
        elif tgt_side == "west":
            end = (end[0] - tgt_fan_px, end[1])

        sx, sy = start
        tx, ty = end

        src_lane = str(src_g.get("lane_id") or default_lane)
        tgt_lane = str(tgt_g.get("lane_id") or default_lane)

        if src_lane == tgt_lane:
            top = lane_top_y[src_lane]
            bot = lane_bottom_y[src_lane]

            safe_top = top + LANE_HEADER_H + 6
            safe_bot = bot - 6

            lane_dir = f"{src_side}->{tgt_side}"
            same_lane_key = (src_lane, tgt_plan, lane_dir)
            same_lane_idx = same_lane_bus_counter[same_lane_key]
            same_lane_bus_counter[same_lane_key] += 1

            # forbidden middle band: first row of nodes
            node_row_top = top + LANE_HEADER_H + PAD_Y - 8
            node_row_bot = top + LANE_HEADER_H + PAD_Y + NODE_H + 12

            # prefer top corridor first
            top_base = safe_top + (same_lane_idx * 18.0)

            # if top corridor is occupied, use a lower corridor under first row
            bottom_base = node_row_bot + 18.0 + (same_lane_idx * 18.0)

            chosen_bus_y = None

            def _same_lane_y_ok(cand_y: float) -> bool:
                if node_row_top <= cand_y <= node_row_bot:
                    return False
                if not _bus_y_ok(cand_y, sx, tx):
                    return False
                if _seg_overlaps(_hseg(cand_y, sx, tx), occupied_bus_hsegs, tol=6.0):
                    return False
                return True

            # try upper corridor
            for cand in _same_lane_bus_y_candidates(src_lane, top_base, 12.0, 18):
                cand = _clamp(cand, safe_top, safe_bot)
                if _same_lane_y_ok(cand):
                    chosen_bus_y = cand
                    break

            # try lower corridor
            if chosen_bus_y is None:
                for cand in _same_lane_bus_y_candidates(src_lane, bottom_base, 12.0, 18):
                    cand = _clamp(cand, safe_top, safe_bot)
                    if _same_lane_y_ok(cand):
                        chosen_bus_y = cand
                        break

            # final fallback scan
            if chosen_bus_y is None:
                for cand in range(int(safe_top), int(safe_bot) + 1, 12):
                    cand_y = float(cand)
                    if _same_lane_y_ok(cand_y):
                        chosen_bus_y = cand_y
                        break

            # absolute fallback
            if chosen_bus_y is None:
                chosen_bus_y = safe_top

            bus_y = chosen_bus_y
        else:
            if lane_top_y[src_lane] < lane_top_y[tgt_lane]:
                gap_top = lane_bottom_y[src_lane] + 6
                gap_bot = lane_top_y[tgt_lane] - 6
            else:
                gap_top = lane_bottom_y[tgt_lane] + 6
                gap_bot = lane_top_y[src_lane] - 6

            if gap_bot <= gap_top:
                bus_y = (sy + ty) / 2.0
            else:
                bus_y = _pick_non_overlapping_bus_y(
                    base_y=(gap_top + gap_bot) / 2.0,
                    sx=sx,
                    ex=tx,
                    safe_top=gap_top,
                    safe_bot=gap_bot,
                    node_rects_inflated=node_rects_inflated,
                    occupied_bus_hsegs=occupied_bus_hsegs,
                    step=12.0,
                    tries=18,
                    tol=6.0,
                )

        occupied_bus_hsegs.append(_hseg(bus_y, sx, tx))

        # ------------------------------------------------------
        # Separate vertical target corridors, but keep short
        # direct vertical edges clean to avoid ugly hooks.
        # ------------------------------------------------------
        route_pts: List[Point]

        if tgt_side in ("north", "south"):
            nearly_same_x = abs(start[0] - end[0]) < 28.0
            adjacent_lane_vertical = abs(start[1] - end[1]) < 260.0

            if nearly_same_x and adjacent_lane_vertical:
                route_pts = _dedupe_points([
                    start,
                    end,
                ])
            else:
                side_key = "right" if end[0] >= (START_X + LANE_WIDTH / 2.0) else "left"
                v_key = (tgt_plan, side_key)
                v_idx = vertical_target_counter[v_key]
                vertical_target_counter[v_key] += 1

                shift = 20.0 * v_idx
                vx = end[0] + shift if side_key == "right" else end[0] - shift
                vx = _clamp(vx, SAFE_X_MIN, SAFE_X_MAX)

                route_pts = _dedupe_points([
                    start,
                    (sx, bus_y),
                    (vx, bus_y),
                    (vx, end[1]),
                    end,
                ])
        else:
            route_pts = _dedupe_points([
                start,
                (sx, bus_y),
                (tx, bus_y),
                end,
            ])

        edge_records.append(
            {
                "edge": e,
                "src_plan": src_plan,
                "src_cell": src_cell,
                "tgt_cell": tgt_cell,
                "style": edge_style_base + port_constraints + anchor_style,
                "route_pts": route_pts,
            }
        )

    separate_routes_with_validation(
        edge_records=edge_records,
        node_rects=node_rects_inflated,
        tolerance=6.0,
        offset_step=10.0,
        offset_tries=12,
        keep_ends_fixed=True,
        clamp_x=(SAFE_X_MIN, SAFE_X_MAX),
        clamp_y=None,
    )

    # ----------------------------------------------------------
    # Emit edges first
    # ----------------------------------------------------------
    for rec in edge_records:
        src_cell = rec["src_cell"]
        tgt_cell = rec["tgt_cell"]
        route_pts = rec["route_pts"]

        interior = route_pts[1:-1]
        points_xml = ""
        if interior:
            pts = "".join([f'<mxPoint x="{x:.1f}" y="{y:.1f}"/>' for (x, y) in interior])
            points_xml = f'<Array as="points">{pts}</Array>'

        eid = next_id()
        raw_edge_label = (rec["edge"].get("label") or "").strip()
        raw_data_label = (rec["edge"].get("data_label") or "").strip()
        visible_label = _esc(_short(_nounify_edge_label(raw_edge_label, raw_data_label), 48))

        cells.append(
            f'<mxCell id="{eid}" value="{visible_label}" style="{rec["style"]}" '
            f'edge="1" parent="1" source="{src_cell}" target="{tgt_cell}">'
            f'<mxGeometry relative="1" as="geometry">{points_xml}</mxGeometry>'
            f"</mxCell>"
        )

    # ----------------------------------------------------------
    # Emit nodes last
    # ----------------------------------------------------------
    for info in node_layout:
        node_style = _node_style(info["fill"], info["shape"])
        cells.append(
            f'<mxCell id="{info["mx_id"]}" value="{info["label"]}" style="{node_style}" '
            f'vertex="1" parent="{info["parent"]}">'
            f'<mxGeometry x="{info["x"]:.1f}" y="{info["y"]:.1f}" width="{info["w"]:.1f}" height="{info["h"]:.1f}" as="geometry"/>'
            f"</mxCell>"
        )

    cells_xml = "\n".join(cells)

    page_h = lane_y + 40
    page_w = START_X + LANE_WIDTH + 40

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{title}" agent="ProcessFlow Export" version="21.0.0" type="device">
 <diagram name="Process Flow" id="process-flow-diagram">
   <mxGraphModel dx="{int(page_w)}" dy="{int(page_h)}" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{int(page_w)}" pageHeight="{int(page_h)}" math="0" shadow="0">
     <root>
       <mxCell id="0"/>
       <mxCell id="1" parent="0"/>
{cells_xml}
     </root>
   </mxGraphModel>
 </diagram>
</mxfile>'''