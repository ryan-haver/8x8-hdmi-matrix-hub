#!/usr/bin/env python3
"""Simplify the traced device icons in ``web/assets/icons/svg`` (UI-22).

The bundled icons were produced by ``scripts/convert-icons-to-svg.js``, which
pre-processed PNG sprites of unknown licence with Jimp and auto-traced them
with potrace. The traces carry three decimals on a 1024-unit grid and a lot of
tracing noise, so a single icon weighed up to 376 KB - far above the "< 5 KB per
icon" target in docs/REMEDIATION_PLAN.md ("Device icons (UI-22)"). Simplifying
the raw traces in place is not an option: potrace outlines carry so much
high-frequency noise that Ramer-Douglas-Peucker needs a tolerance of 150+ units
(15% of the icon) to reach the budget, which destroys the drawing.

So each icon is re-traced at the resolution it is actually displayed at:

    1. parse the path into absolute cubic segments and flatten the curves,
    2. decimate the polylines to the raster grid (kills the tracing noise),
    3. rasterise the result with the non-zero winding rule,
    4. close 1 px gaps and drop connected components below the speckle floor,
    5. trace the pixel-boundary contours (outer loops and holes),
    6. simplify each contour with Ramer-Douglas-Peucker and re-fit it as
       Catmull-Rom cubics (straight lines at sharp corners), and
    7. emit integer coordinates as one compact relative path.

The pipeline only depends on the standard library, so the icons can be rebuilt
without installing anything.

Usage::

    python scripts/optimize_device_icons.py            # rewrite the icons
    python scripts/optimize_device_icons.py --check    # report only, write nothing
    python scripts/optimize_device_icons.py --render out.png television
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = REPO_ROOT / "web" / "assets" / "icons" / "svg"

# docs/REMEDIATION_PLAN.md: "Target < 5 KB per icon". tests/ enforces 5120
# bytes; the default budget keeps a margin below that cap.
BUDGET_BYTES = 5000

# Raster grid the icons are re-traced on. The UI draws these at 22-48 px, so
# 192 px per side keeps every feature the app can resolve while dropping the
# sub-pixel tracing noise.
MASK_SIZE = 192

# Flattening tolerance of the source curves, in viewBox units.
FLATTEN_TOLERANCE = 0.5

# Traces smaller than this (square viewBox units) are speckle, not drawing.
MIN_SUBPATH_AREA = 24.0

# Contour simplification tolerance search range, in viewBox units.
MIN_TOLERANCE = 1.0
MAX_TOLERANCE = 24.0

# Connected components below this many mask pixels are speckle.
MIN_COMPONENT_PIXELS = 16

# A vertex whose turn exceeds this many degrees is kept as a corner and the
# neighbouring segments stay straight lines.
CORNER_ANGLE_DEG = 55.0

SVG_TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}">'
    '<path fill="currentColor" d="{d}"/></svg>\n'
)

TOKEN_RE = re.compile(r"[MmZzLlHhVvCcSsQqTtAa]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
VIEWBOX_RE = re.compile(r'viewBox="([^"]+)"')
PATH_D_RE = re.compile(r'\sd="([^"]+)"')

# What this tool emits. Re-tracing an already re-traced icon is lossy (every
# pass drops another sub-pixel line), so such files are left alone unless the
# caller asks for --force.
OPTIMIZED_RE = re.compile(
    r'\A<svg xmlns="http://www\.w3\.org/2000/svg" viewBox="[^"]+">'
    r'<path fill="currentColor" d="[^"]+"/></svg>\n\Z'
)

Point = tuple[float, float]
Mask = list[bytearray]


# ---------------------------------------------------------------------------
# Path parsing
# ---------------------------------------------------------------------------


def _tokenize(d: str) -> list[str]:
    return TOKEN_RE.findall(d)


def parse_path(d: str) -> list[list[tuple[str, list[Point]]]]:
    """Parse a path ``d`` into subpaths of absolute segments.

    Each subpath is a list of ``("C", [p0, c1, c2, p1])`` and ``("L", [p0, p1])``
    tuples, closed by ``("Z", [])``.
    """
    tokens = _tokenize(d)
    subpaths: list[list[tuple[str, list[Point]]]] = []
    current: list[tuple[str, list[Point]]] = []

    pos: Point = (0.0, 0.0)
    start: Point = (0.0, 0.0)
    last_cubic_ctrl: Point | None = None
    last_quad_ctrl: Point | None = None
    command = ""
    index = 0

    def numbers(count: int) -> list[float]:
        nonlocal index
        if index + count > len(tokens):
            raise ValueError(f"path data ended early near token {index}")
        values = [float(tokens[index + offset]) for offset in range(count)]
        index += count
        return values

    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            index += 1
            if command in "Zz":
                if current:
                    current.append(("Z", []))
                    subpaths.append(current)
                    current = []
                pos = start
                last_cubic_ctrl = None
                last_quad_ctrl = None
                continue
        elif not command:
            raise ValueError("path data must start with a command")
        elif command == "M":
            command = "L"
        elif command == "m":
            command = "l"

        relative = command.islower()
        upper = command.upper()

        if upper == "M":
            x, y = numbers(2)
            if relative:
                x, y = pos[0] + x, pos[1] + y
            if current:
                subpaths.append(current)
            pos = start = (x, y)
            current = []
            last_cubic_ctrl = last_quad_ctrl = None
        elif upper == "L":
            x, y = numbers(2)
            if relative:
                x, y = pos[0] + x, pos[1] + y
            current.append(("L", [pos, (x, y)]))
            pos = (x, y)
            last_cubic_ctrl = last_quad_ctrl = None
        elif upper == "H":
            (x,) = numbers(1)
            if relative:
                x += pos[0]
            current.append(("L", [pos, (x, pos[1])]))
            pos = (x, pos[1])
            last_cubic_ctrl = last_quad_ctrl = None
        elif upper == "V":
            (y,) = numbers(1)
            if relative:
                y += pos[1]
            current.append(("L", [pos, (pos[0], y)]))
            pos = (pos[0], y)
            last_cubic_ctrl = last_quad_ctrl = None
        elif upper in ("C", "S"):
            if upper == "C":
                x1, y1, x2, y2, x, y = numbers(6)
                if relative:
                    x1, y1 = pos[0] + x1, pos[1] + y1
                    x2, y2 = pos[0] + x2, pos[1] + y2
                    x, y = pos[0] + x, pos[1] + y
            else:
                x2, y2, x, y = numbers(4)
                if relative:
                    x2, y2 = pos[0] + x2, pos[1] + y2
                    x, y = pos[0] + x, pos[1] + y
                if last_cubic_ctrl is None:
                    x1, y1 = pos
                else:
                    x1 = 2 * pos[0] - last_cubic_ctrl[0]
                    y1 = 2 * pos[1] - last_cubic_ctrl[1]
            current.append(("C", [pos, (x1, y1), (x2, y2), (x, y)]))
            pos = (x, y)
            last_cubic_ctrl = (x2, y2)
            last_quad_ctrl = None
        elif upper in ("Q", "T"):
            if upper == "Q":
                qx, qy, x, y = numbers(4)
                if relative:
                    qx, qy = pos[0] + qx, pos[1] + qy
                    x, y = pos[0] + x, pos[1] + y
            else:
                x, y = numbers(2)
                if relative:
                    x, y = pos[0] + x, pos[1] + y
                if last_quad_ctrl is None:
                    qx, qy = pos
                else:
                    qx = 2 * pos[0] - last_quad_ctrl[0]
                    qy = 2 * pos[1] - last_quad_ctrl[1]
            c1 = (pos[0] + 2 / 3 * (qx - pos[0]), pos[1] + 2 / 3 * (qy - pos[1]))
            c2 = (x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y))
            current.append(("C", [pos, c1, c2, (x, y)]))
            pos = (x, y)
            last_quad_ctrl = (qx, qy)
            last_cubic_ctrl = None
        elif upper == "A":
            rx, ry, rotation, large_arc, sweep, x, y = numbers(7)
            if relative:
                x, y = pos[0] + x, pos[1] + y
            current.extend(arc_to_cubics(pos, rx, ry, rotation, bool(large_arc), bool(sweep), (x, y)))
            pos = (x, y)
            last_cubic_ctrl = last_quad_ctrl = None
        else:  # pragma: no cover - TOKEN_RE cannot produce anything else
            raise ValueError(f"unsupported path command {command!r}")

    if current:
        subpaths.append(current)
    return subpaths


def arc_to_cubics(
    start: Point,
    rx: float,
    ry: float,
    rotation_deg: float,
    large_arc: bool,
    sweep: bool,
    end: Point,
) -> list[tuple[str, list[Point]]]:
    """Convert an SVG elliptical arc into cubic Béziers (SVG 1.1 appendix F.6)."""
    if start == end or (rx == 0 and ry == 0):
        return []
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(rotation_deg)
    cos_phi, sin_phi = math.cos(phi), math.sin(phi)

    dx, dy = (start[0] - end[0]) / 2, (start[1] - end[1]) / 2
    x1p = cos_phi * dx + sin_phi * dy
    y1p = -sin_phi * dx + cos_phi * dy

    # Scale the radii up when they are too small to span the endpoints.
    scale = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if scale > 1:
        factor = math.sqrt(scale)
        rx *= factor
        ry *= factor

    denominator = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    numerator = max(0.0, rx * rx * ry * ry - denominator)
    coefficient = math.sqrt(numerator / denominator) if denominator else 0.0
    if large_arc == sweep:
        coefficient = -coefficient
    cxp = coefficient * rx * y1p / ry
    cyp = -coefficient * ry * x1p / rx
    cx = cos_phi * cxp - sin_phi * cyp + (start[0] + end[0]) / 2
    cy = sin_phi * cxp + cos_phi * cyp + (start[1] + end[1]) / 2

    def angle(ux: float, uy: float, vx: float, vy: float) -> float:
        length = math.hypot(ux, uy) * math.hypot(vx, vy)
        if length == 0:
            return 0.0
        value = max(-1.0, min(1.0, (ux * vx + uy * vy) / length))
        result = math.acos(value)
        return -result if ux * vy - uy * vx < 0 else result

    theta1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    theta2 = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    delta = theta2 - theta1
    if not sweep and delta > 0:
        delta -= 2 * math.pi
    elif sweep and delta < 0:
        delta += 2 * math.pi

    def on_ellipse(theta: float) -> Point:
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        return (cos_phi * rx * cos_t - sin_phi * ry * sin_t + cx, sin_phi * rx * cos_t + cos_phi * ry * sin_t + cy)

    def derivative(theta: float) -> Point:
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        return (-rx * sin_t, ry * cos_t)

    segments: list[tuple[str, list[Point]]] = []
    steps = max(1, int(math.ceil(abs(delta) / (math.pi / 2))))
    step_angle = delta / steps
    alpha = 4 / 3 * math.tan(step_angle / 4)
    point = start
    for index in range(steps):
        theta = theta1 + index * step_angle
        next_point = on_ellipse(theta + step_angle)
        tangent = derivative(theta)
        next_tangent = derivative(theta + step_angle)
        c1 = (point[0] + alpha * (cos_phi * tangent[0] - sin_phi * tangent[1]),
              point[1] + alpha * (sin_phi * tangent[0] + cos_phi * tangent[1]))
        c2 = (next_point[0] - alpha * (cos_phi * next_tangent[0] - sin_phi * next_tangent[1]),
              next_point[1] - alpha * (sin_phi * next_tangent[0] + cos_phi * next_tangent[1]))
        segments.append(("C", [point, c1, c2, next_point]))
        point = next_point
    return segments


# ---------------------------------------------------------------------------
# Flattening and decimation
# ---------------------------------------------------------------------------


def flatten_cubic(p0: Point, p1: Point, p2: Point, p3: Point, tolerance: float, out: list[Point]) -> None:
    """Append a polyline approximation of a cubic to ``out``."""
    ux = 3 * p1[0] - 2 * p0[0] - p3[0]
    uy = 3 * p1[1] - 2 * p0[1] - p3[1]
    vx = 3 * p2[0] - 2 * p0[0] - p3[0]
    vy = 3 * p2[1] - 2 * p0[1] - p3[1]
    if max(ux * ux, vx * vx) + max(uy * uy, vy * vy) <= 16 * tolerance * tolerance:
        out.append(p3)
        return

    def mid(a: Point, b: Point) -> Point:
        return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)

    p01, p12, p23 = mid(p0, p1), mid(p1, p2), mid(p2, p3)
    p012, p123 = mid(p01, p12), mid(p12, p23)
    p0123 = mid(p012, p123)
    flatten_cubic(p0, p01, p012, p0123, tolerance, out)
    flatten_cubic(p0123, p123, p23, p3, tolerance, out)


def flatten_subpath(segments: list[tuple[str, list[Point]]], tolerance: float) -> list[Point]:
    points: list[Point] = []
    for kind, values in segments:
        if kind == "C":
            flatten_cubic(values[0], values[1], values[2], values[3], tolerance, points)
        elif kind == "L":
            points.append(values[1])
    return points


def dedupe(points: list[Point], epsilon: float = 0.5) -> list[Point]:
    """Drop consecutive duplicate points and the closing duplicate of a loop."""
    cleaned: list[Point] = []
    for point in points:
        if cleaned and abs(point[0] - cleaned[-1][0]) <= epsilon and abs(point[1] - cleaned[-1][1]) <= epsilon:
            continue
        cleaned.append(point)
    while (
        len(cleaned) > 1
        and abs(cleaned[0][0] - cleaned[-1][0]) <= epsilon
        and abs(cleaned[0][1] - cleaned[-1][1]) <= epsilon
    ):
        cleaned.pop()
    return cleaned


def decimate(points: list[Point], step: float) -> list[Point]:
    """Keep a point only when it is ``step`` away from the last kept one.

    This is what removes the tracing noise: potrace emits thousands of
    sub-pixel steps per contour, all of which land on the same mask pixel.
    """
    if len(points) < 3 or step <= 0:
        return list(points)
    kept = [points[0]]
    last_x, last_y = points[0]
    for x, y in points[1:]:
        if math.hypot(x - last_x, y - last_y) >= step:
            kept.append((x, y))
            last_x, last_y = x, y
    return kept


def signed_area(points: list[Point]) -> float:
    """Shoelace area; negative for outer contours in this y-down space."""
    total = 0.0
    for index in range(len(points)):
        x0, y0 = points[index]
        x1, y1 = points[(index + 1) % len(points)]
        total += x0 * y1 - x1 * y0
    return total / 2


def polygon_area(points: list[Point]) -> float:
    return abs(signed_area(points))


# ---------------------------------------------------------------------------
# Rasterising the source drawing
# ---------------------------------------------------------------------------


def source_loops(d: str) -> list[list[Point]]:
    """Flatten a source path into decimated loops, dropping speckle."""
    step = 1024.0 / MASK_SIZE
    loops: list[list[Point]] = []
    for segments in parse_path(d):
        points = dedupe(flatten_subpath(segments, FLATTEN_TOLERANCE))
        if len(points) < 3 or polygon_area(points) < MIN_SUBPATH_AREA:
            continue
        points = decimate(points, step)
        if len(points) >= 3:
            loops.append(points)
    return loops


def rasterize(loops: list[list[Point]], size: int = MASK_SIZE, view_box: float = 1024.0) -> Mask:
    """Scanline-fill the loops with the non-zero winding rule."""
    scale = size / view_box
    winding = [[0] * size for _ in range(size)]
    for loop in loops:
        points = [(x * scale, y * scale) for x, y in loop]
        count = len(points)
        for index in range(count):
            x0, y0 = points[index]
            x1, y1 = points[(index + 1) % count]
            if y0 == y1:
                continue
            direction = 1 if y0 < y1 else -1
            top, bottom = (y0, y1) if direction > 0 else (y1, y0)
            first = max(0, int(math.ceil(top - 0.5)))
            last = min(size - 1, int(math.floor(bottom - 0.5)))
            slope = (x1 - x0) / (y1 - y0)
            for row in range(first, last + 1):
                x = x0 + (row + 0.5 - y0) * slope
                # A crossing at x affects every pixel centre (column + 0.5) to
                # its right, so the first affected column is ceil(x - 0.5).
                column = math.ceil(x - 0.5)
                if 0 <= column < size:
                    winding[row][column] += direction

    mask: Mask = [bytearray(size) for _ in range(size)]
    for row in range(size):
        line = winding[row]
        filled = mask[row]
        accumulator = 0
        for column in range(size):
            accumulator += line[column]
            if accumulator:
                filled[column] = 1
    return mask


def close_gaps(mask: Mask, size: int = MASK_SIZE) -> Mask:
    """Dilate then erode with a 3x3 kernel, so 1 px breaks in a trace heal."""
    dilated: Mask = [bytearray(size) for _ in range(size)]
    for y in range(size):
        above = mask[y - 1] if y else None
        line = mask[y]
        below = mask[y + 1] if y + 1 < size else None
        out = dilated[y]
        for x in range(size):
            hit = line[x]
            if not hit:
                hit = (
                    (line[x - 1] if x else 0)
                    or (line[x + 1] if x + 1 < size else 0)
                    or (above[x] if above is not None else 0)
                    or (below[x] if below is not None else 0)
                )
            out[x] = 1 if hit else 0

    eroded: Mask = [bytearray(size) for _ in range(size)]
    for y in range(size):
        above = dilated[y - 1] if y else None
        line = dilated[y]
        below = dilated[y + 1] if y + 1 < size else None
        out = eroded[y]
        for x in range(size):
            out[x] = 1 if line[x] and (above is not None and above[x]) and (below is not None and below[x]) else 0
    return eroded


def drop_speckle(mask: Mask, min_pixels: int = MIN_COMPONENT_PIXELS, size: int = MASK_SIZE) -> Mask:
    """Remove connected components smaller than ``min_pixels``."""
    seen = [bytearray(size) for _ in range(size)]
    keep = [bytearray(size) for _ in range(size)]
    for y in range(size):
        for x in range(size):
            if not mask[y][x] or seen[y][x]:
                continue
            component: list[tuple[int, int]] = []
            queue = deque([(y, x)])
            seen[y][x] = 1
            while queue:
                cy, cx = queue.popleft()
                component.append((cy, cx))
                for ny in range(max(0, cy - 1), min(size, cy + 2)):
                    row = mask[ny]
                    seen_row = seen[ny]
                    for nx in range(max(0, cx - 1), min(size, cx + 2)):
                        if row[nx] and not seen_row[nx]:
                            seen_row[nx] = 1
                            queue.append((ny, nx))
            if len(component) >= min_pixels:
                for cy, cx in component:
                    keep[cy][cx] = 1
    return keep


# ---------------------------------------------------------------------------
# Contour extraction
# ---------------------------------------------------------------------------


def trace_contours(mask: Mask, size: int = MASK_SIZE) -> list[list[Point]]:
    """Trace every pixel-boundary loop of ``mask`` as a closed polygon.

    Contours run so that outer loops have negative and holes positive area,
    which is the non-zero convention the traced sources already use.
    """
    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for y in range(size):
        line = mask[y]
        above = mask[y - 1] if y else None
        below = mask[y + 1] if y + 1 < size else None
        for x in range(size):
            if not line[x]:
                continue
            left = line[x - 1] if x else 0
            right = line[x + 1] if x + 1 < size else 0
            up = above[x] if above is not None else 0
            down = below[x] if below is not None else 0
            if not up:
                edges.append(((x + 1, y), (x, y)))
            if not right:
                edges.append(((x + 1, y + 1), (x + 1, y)))
            if not down:
                edges.append(((x, y + 1), (x + 1, y + 1)))
            if not left:
                edges.append(((x, y), (x, y + 1)))

    outgoing: dict[tuple[int, int], list[int]] = {}
    for index, (start, _end) in enumerate(edges):
        outgoing.setdefault(start, []).append(index)

    used = bytearray(len(edges))
    contours: list[list[Point]] = []
    for index in range(len(edges)):
        if used[index]:
            continue
        used[index] = 1
        origin = edges[index][0]
        contour: list[Point] = [origin]
        current = index
        while True:
            end = edges[current][1]
            contour.append(end)
            if end == origin:
                break
            following = None
            for candidate in outgoing.get(end, ()):
                if not used[candidate]:
                    following = candidate
                    break
            if following is None:
                break
            used[following] = 1
            current = following
        if len(contour) > 4:
            contours.append([(float(x), float(y)) for x, y in contour[:-1]])
    return contours


# ---------------------------------------------------------------------------
# Simplification and serialisation
# ---------------------------------------------------------------------------


def _perpendicular_distance(point: Point, start: Point, end: Point) -> float:
    dx, dy = end[0] - start[0], end[1] - start[1]
    if dx == 0 and dy == 0:
        return math.hypot(point[0] - start[0], point[1] - start[1])
    return abs(dy * point[0] - dx * point[1] + end[0] * start[1] - end[1] * start[0]) / math.hypot(dx, dy)


def _rdp(points: list[Point], tolerance: float) -> list[Point]:
    """Ramer-Douglas-Peucker on an open chain."""
    if len(points) < 3:
        return list(points)
    keep = bytearray(len(points))
    keep[0] = keep[-1] = 1
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        if last <= first + 1:
            continue
        worst_index = -1
        worst = tolerance
        for index in range(first + 1, last):
            distance = _perpendicular_distance(points[index], points[first], points[last])
            if distance > worst:
                worst = distance
                worst_index = index
        if worst_index != -1:
            keep[worst_index] = 1
            stack.append((first, worst_index))
            stack.append((worst_index, last))
    return [point for point, flag in zip(points, keep) if flag]


def simplify_loop(points: list[Point], tolerance: float) -> list[Point]:
    """Simplify a closed polygon, keeping two anchors so the loop stays closed."""
    if len(points) <= 4:
        return list(points)

    # Anchor candidates are the extreme points on each axis; they are far
    # enough apart to split the loop into two chains RDP can handle.
    candidates = {
        min(range(len(points)), key=lambda i: (points[i][0], points[i][1])),
        max(range(len(points)), key=lambda i: (points[i][0], points[i][1])),
        min(range(len(points)), key=lambda i: (points[i][1], points[i][0])),
        max(range(len(points)), key=lambda i: (points[i][1], points[i][0])),
    }
    first, second = max(
        ((a, b) for a in candidates for b in candidates if a != b),
        key=lambda pair: math.dist(points[pair[0]], points[pair[1]]),
    )
    if second < first:
        first, second = second, first

    head = points[first : second + 1]
    tail = points[second:] + points[: first + 1]
    simplified = _rdp(head, tolerance)[:-1] + _rdp(tail, tolerance)[:-1]
    return dedupe(simplified, epsilon=0.5) or list(points)


def _is_corner(points: list[Point], index: int) -> bool:
    count = len(points)
    if count < 3:
        return False
    previous = points[index - 1]
    current = points[index]
    following = points[(index + 1) % count]
    ax, ay = current[0] - previous[0], current[1] - previous[1]
    bx, by = following[0] - current[0], following[1] - current[1]
    if (ax == 0 and ay == 0) or (bx == 0 and by == 0):
        return True
    cos_angle = (ax * bx + ay * by) / (math.hypot(ax, ay) * math.hypot(bx, by))
    cos_angle = max(-1.0, min(1.0, cos_angle))
    return math.degrees(math.acos(cos_angle)) > CORNER_ANGLE_DEG


def _number(value: float) -> str:
    """Round to an integer viewBox unit (the 1024 grid the icons are traced on)."""
    return str(int(round(value)))


def build_path_data(loops: list[list[Point]]) -> str:
    """Serialise simplified loops as one compact relative path.

    Repeated ``l``/``c`` segments drop their command letter (SVG implicit
    repetition); every continued run starts with a space, otherwise adjacent
    positive integers would run together into a single bogus number.
    """
    out: list[str] = []
    previous = ""
    for points in loops:
        if len(points) < 3:
            continue
        cursor = (float(round(points[0][0])), float(round(points[0][1])))
        out.append(f"M{_number(cursor[0])} {_number(cursor[1])}")
        previous = "M"

        count = len(points)
        for index in range(count):
            following = points[(index + 1) % count]
            if _is_corner(points, index) or _is_corner(points, (index + 1) % count):
                # Straight edge, so a rectangle stays a rectangle.
                target = (float(round(following[0])), float(round(following[1])))
                body = f"{_number(target[0] - cursor[0])} {_number(target[1] - cursor[1])}"
                out.append(f" {body}" if previous == "l" else f"l{body}")
                cursor = target
                previous = "l"
                continue

            # Catmull-Rom through the points, written as a cubic Bézier.
            before = points[index - 1]
            after = points[(index + 2) % count]
            c1 = (cursor[0] + (following[0] - before[0]) / 6, cursor[1] + (following[1] - before[1]) / 6)
            c2 = (following[0] - (after[0] - cursor[0]) / 6, following[1] - (after[1] - cursor[1]) / 6)
            c1 = (float(round(c1[0])), float(round(c1[1])))
            c2 = (float(round(c2[0])), float(round(c2[1])))
            end = (float(round(following[0])), float(round(following[1])))
            body = (
                f"{_number(c1[0] - cursor[0])} {_number(c1[1] - cursor[1])} "
                f"{_number(c2[0] - cursor[0])} {_number(c2[1] - cursor[1])} "
                f"{_number(end[0] - cursor[0])} {_number(end[1] - cursor[1])}"
            )
            out.append(f" {body}" if previous == "c" else f"c{body}")
            cursor = end
            previous = "c"
        out.append("z")
        previous = "z"
    return "".join(out)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def load_svg(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    view_box_match = VIEWBOX_RE.search(text)
    path_match = PATH_D_RE.search(text)
    if not view_box_match or not path_match:
        raise ValueError(f"{path.name}: expected an <svg viewBox=...> with a <path d=...>")
    return view_box_match.group(1), path_match.group(1)


def retrace(d: str, tolerance: float, scale: float = 1024.0 / MASK_SIZE) -> list[list[Point]]:
    """Re-trace a source path at mask resolution and simplify the contours."""
    mask = rasterize(source_loops(d), view_box=scale * MASK_SIZE)
    mask = close_gaps(mask)
    mask = drop_speckle(mask)
    loops: list[list[Point]] = []
    for contour in trace_contours(mask):
        points = [(x * scale, y * scale) for x, y in contour]
        simplified = simplify_loop(points, tolerance)
        if len(simplified) >= 3 and polygon_area(simplified) > 1.0:
            loops.append(simplified)
    return loops


def optimize_file(path: Path, budget: int = BUDGET_BYTES) -> dict:
    """Pick the smallest tolerance that fits ``budget`` and return the result."""
    view_box, d = load_svg(path)
    scale = 1024.0 / MASK_SIZE
    view_size = float(max((float(value) for value in view_box.split()[2:]), default=1024.0))
    if view_size != 1024.0:
        scale = view_size / MASK_SIZE

    def measure(tolerance: float) -> tuple[str, int, int]:
        loops = retrace(d, tolerance, scale)
        data = build_path_data(loops)
        size = len(SVG_TEMPLATE.format(view_box=view_box, d=data).encode("utf-8"))
        return data, size, sum(len(loop) for loop in loops)

    data, size, points = measure(MAX_TOLERANCE)
    tolerance = MAX_TOLERANCE
    if size <= budget:
        # Smallest tolerance that still fits, so detailed icons keep detail.
        low, high = MIN_TOLERANCE, MAX_TOLERANCE
        for _ in range(12):
            middle = (low + high) / 2
            candidate, candidate_size, candidate_points = measure(middle)
            if candidate_size <= budget:
                high = middle
                data, size, points = candidate, candidate_size, candidate_points
            else:
                low = middle
            if high - low < 0.05:
                break
        tolerance = high

    svg = SVG_TEMPLATE.format(view_box=view_box, d=data)
    return {
        "name": path.name,
        "before": path.stat().st_size,
        "after": len(svg.encode("utf-8")),
        "tolerance": round(tolerance, 2),
        "points": points,
        "svg": svg,
        "path": data,
    }


def render_compare(result: dict, source_d: str, output: Path, size: int = 256) -> None:
    """Write a side-by-side PNG of the source drawing and the re-traced path."""
    try:
        from PIL import Image
    except ImportError:
        print("Pillow is not installed; skipping render", file=sys.stderr)
        return

    def pixels(d: str) -> bytes:
        rows = rasterize(source_loops(d), size)
        return bytes(255 if value else 0 for row in rows for value in row)

    comparison = Image.new("L", (size * 2, size), 0)
    comparison.paste(Image.frombytes("L", (size, size), pixels(source_d)), (0, 0))
    comparison.paste(Image.frombytes("L", (size, size), pixels(result["path"])), (size, 0))
    comparison.save(output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Re-trace the device icons under the 5 KB per-icon budget (UI-22).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--check", action="store_true", help="only report, never write")
    parser.add_argument("--force", action="store_true", help="also re-trace icons this tool already wrote")
    parser.add_argument("--budget", type=int, default=BUDGET_BYTES, help="per-icon byte budget")
    parser.add_argument("--render", type=Path, help="write a source/re-traced PNG for this icon")
    args = parser.parse_args(argv)

    icons = sorted(ICON_DIR.glob("*.svg"))
    if not icons:
        print(f"no icons found in {ICON_DIR}", file=sys.stderr)
        return 1

    rows = []
    over_budget = []
    for icon in icons:
        text = icon.read_text(encoding="utf-8")
        size = icon.stat().st_size
        if not args.force and OPTIMIZED_RE.match(text):
            # Already re-traced. Another pass would drop yet another
            # sub-pixel line, so leave the drawing alone.
            print(f"{icon.name:<28} {size:>7} bytes  already optimised")
            if size >= 5120:
                over_budget.append(icon.name)
            rows.append({"before": size, "after": size})
            continue

        result = optimize_file(icon, budget=args.budget)
        rows.append(result)
        if result["after"] >= 5120:
            over_budget.append(result["name"])
        status = "unchanged"
        if not args.check and result["after"] != result["before"]:
            icon.write_text(result["svg"], encoding="utf-8")
            status = "rewritten"
        print(
            f"{result['name']:<28} {result['before']:>7} -> {result['after']:>5} bytes  "
            f"tol={result['tolerance']:>5}  points={result['points']:<4} {status}"
        )
        if args.render and icon.stem == args.render.stem:
            _view_box, source_d = load_svg(icon)
            render_compare(result, source_d, args.render)

    total_before = sum(row["before"] for row in rows)
    total_after = sum(row["after"] for row in rows)
    saved = 100 * (1 - total_after / total_before) if total_before else 0.0
    print("-" * 96)
    print(f"{len(rows)} icons: {total_before:,} -> {total_after:,} bytes ({saved:.1f}% smaller), budget {args.budget} bytes")

    # scripts/convert-icons-to-svg.js also wrote a copy of every path into
    # _icon-paths.json (2.9 MB). Nothing reads it, so it is regenerated from the
    # icons instead of being left stale: same shape, current data.
    paths = {icon.stem: load_svg(icon)[1] for icon in icons}
    index_file = ICON_DIR / "_icon-paths.json"
    payload = json.dumps(paths, indent=2) + "\n"
    if args.check:
        print(f"{index_file.name}: {len(payload.encode('utf-8')):,} bytes (would be rewritten)")
    else:
        was = index_file.stat().st_size if index_file.is_file() else 0
        index_file.write_text(payload, encoding="utf-8")
        print(f"{index_file.name}: {was:,} -> {index_file.stat().st_size:,} bytes")

    if over_budget:
        print(f"OVER BUDGET (>= 5120 bytes): {', '.join(over_budget)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
