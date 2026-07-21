"""Freehand track ROI geometry closed to the frame with endpoint tangents.

The operator stroke remains intact. Its endpoint derivative rays extend to the
frame boundary, producing two closed partitions; the smaller partition is the
technical tracking region.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

Point = tuple[float, float]
SCHEMA_VERSION = "track-roi-stroke.v1"
SCOPE = "review_assistance_only"
_EPSILON = 1e-7


@dataclass(frozen=True)
class TrackRoi:
    revision: int
    reference_source_sha256: str
    reference_timestamp_sec: float
    reference_frame_size_px: tuple[int, int]
    stroke_points_normalized: tuple[Point, ...]
    start_extension_normalized: Point
    end_extension_normalized: Point
    tracking_region_normalized: tuple[Point, ...]
    scope: str = SCOPE

    def validate(self) -> None:
        width, height = self.reference_frame_size_px
        if self.revision < 1 or width <= 0 or height <= 0:
            raise ValueError("ROI revision and reference frame dimensions must be positive")
        if self.scope != SCOPE or not self.reference_source_sha256.strip():
            raise ValueError("ROI must have review-assistance scope and source checksum")
        derived = derive_track_region(self.stroke_points_normalized)
        if _distance_sq(derived.start_extension[0], self.start_extension_normalized) > _EPSILON**2:
            raise ValueError("ROI start tangent extension does not match the saved stroke")
        if _distance_sq(derived.end_extension[0], self.end_extension_normalized) > _EPSILON**2:
            raise ValueError("ROI end tangent extension does not match the saved stroke")
        if not _points_equal(derived.tracking_region, self.tracking_region_normalized):
            raise ValueError("ROI tracking region does not match the saved stroke")

    @classmethod
    def create(
        cls,
        *,
        revision: int,
        reference_source_sha256: str,
        reference_timestamp_sec: float,
        reference_frame_size_px: tuple[int, int],
        stroke_points_normalized: tuple[Point, ...],
    ) -> TrackRoi:
        region = derive_track_region(stroke_points_normalized)
        return cls(
            revision=revision,
            reference_source_sha256=reference_source_sha256,
            reference_timestamp_sec=reference_timestamp_sec,
            reference_frame_size_px=reference_frame_size_px,
            stroke_points_normalized=stroke_points_normalized,
            start_extension_normalized=region.start_extension[0],
            end_extension_normalized=region.end_extension[0],
            tracking_region_normalized=region.tracking_region,
        )

    def to_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "schema_version": SCHEMA_VERSION,
            "scope": self.scope,
            "revision": self.revision,
            "reference": {
                "source_sha256": self.reference_source_sha256,
                "timestamp_sec": self.reference_timestamp_sec,
                "frame_size_px": list(self.reference_frame_size_px),
            },
            "stroke_points_normalized": [list(point) for point in self.stroke_points_normalized],
            "start_extension_normalized": list(self.start_extension_normalized),
            "end_extension_normalized": list(self.end_extension_normalized),
            "tracking_region_normalized": [list(point) for point in self.tracking_region_normalized],
            "snapshot_sha256": self.snapshot_hash(),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> TrackRoi:
        if raw.get("schema_version") != SCHEMA_VERSION or raw.get("scope") != SCOPE:
            raise ValueError("Unsupported track ROI schema; redraw this ROI as a freehand stroke")
        reference = raw.get("reference")
        if not isinstance(reference, dict):
            raise ValueError("ROI reference must be an object")
        roi = cls(
            revision=int(raw["revision"]),
            reference_source_sha256=str(reference["source_sha256"]),
            reference_timestamp_sec=float(reference["timestamp_sec"]),
            reference_frame_size_px=tuple(int(value) for value in reference["frame_size_px"]),  # type: ignore[arg-type]
            stroke_points_normalized=tuple(_read_point(value) for value in raw["stroke_points_normalized"]),  # type: ignore[arg-type]
            start_extension_normalized=_read_point(raw["start_extension_normalized"]),
            end_extension_normalized=_read_point(raw["end_extension_normalized"]),
            tracking_region_normalized=tuple(_read_point(value) for value in raw["tracking_region_normalized"]),  # type: ignore[arg-type]
            scope=str(raw["scope"]),
        )
        roi.validate()
        return roi

    def snapshot_hash(self) -> str:
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class DerivedTrackRegion:
    start_extension: tuple[Point, ...]
    end_extension: tuple[Point, ...]
    tracking_region: tuple[Point, ...]


def derive_track_region(points: tuple[Point, ...]) -> DerivedTrackRegion:
    """Close a simple freehand stroke using its outward endpoint derivatives."""
    stroke = _compact(points)
    if len(stroke) < 2:
        raise ValueError("Draw a stroke with at least two distinct points")
    if any(not _inside(point) for point in stroke):
        raise ValueError("Keep the freehand stroke inside the video frame")
    if _self_intersects(stroke):
        raise ValueError("Freehand stroke must not cross itself; redraw it")
    start = stroke[0]
    end = stroke[-1]
    start_boundary = _ray_to_boundary(start, _outward_tangent(stroke, at_start=True))
    end_boundary = _ray_to_boundary(end, _outward_tangent(stroke, at_start=False))
    barrier = (start_boundary, *stroke, end_boundary)
    if _polyline_intersects_boundary(stroke):
        raise ValueError("Stroke may touch the frame only at its endpoints; redraw it")
    forward_boundary = _boundary_path(end_boundary, start_boundary, clockwise=True)
    reverse_boundary = _boundary_path(end_boundary, start_boundary, clockwise=False)
    first = _compact((*barrier, *forward_boundary))
    second = _compact((*barrier, *reverse_boundary))
    first_area, second_area = abs(_polygon_area(first)), abs(_polygon_area(second))
    if first_area <= _EPSILON or second_area <= _EPSILON:
        raise ValueError("Stroke does not create two non-empty connected frame regions")
    return DerivedTrackRegion((start_boundary,), (end_boundary,), first if first_area <= second_area else second)


def normalized_to_pixel(point: Point, width: int, height: int) -> Point:
    return point[0] * width, point[1] * height


def detection_footpoint(bbox_xyxy_px: tuple[float, float, float, float]) -> Point:
    x1, y1, x2, y2 = bbox_xyxy_px
    if x2 < x1 or y2 < y1:
        raise ValueError("Detection bounding box coordinates are invalid")
    return (x1 + x2) / 2.0, y2


def point_in_polygon(point: Point, polygon: tuple[Point, ...], *, epsilon: float = _EPSILON) -> bool:
    inside = False
    for index, current in enumerate(polygon):
        previous = polygon[index - 1]
        if _point_on_segment(point, previous, current, epsilon):
            return True
        if (current[1] > point[1]) != (previous[1] > point[1]):
            crossing = (previous[0] - current[0]) * (point[1] - current[1]) / (previous[1] - current[1]) + current[0]
            if point[0] <= crossing:
                inside = not inside
    return inside


def roi_contains_detection(roi: TrackRoi, bbox_xyxy_px: tuple[float, float, float, float], width: int, height: int) -> bool:
    polygon = tuple(normalized_to_pixel(point, width, height) for point in roi.tracking_region_normalized)
    return point_in_polygon(detection_footpoint(bbox_xyxy_px), polygon)


def read_roi(path: Path) -> TrackRoi:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid track ROI: {path}")
    return TrackRoi.from_dict(raw)


def write_roi(roi: TrackRoi, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(roi.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return path


def _outward_tangent(points: tuple[Point, ...], *, at_start: bool) -> Point:
    count = min(5, len(points) - 1)
    if at_start:
        vector = (points[0][0] - points[count][0], points[0][1] - points[count][1])
    else:
        vector = (points[-1][0] - points[-1 - count][0], points[-1][1] - points[-1 - count][1])
    length = math.hypot(*vector)
    if length <= _EPSILON:
        raise ValueError("Endpoint tangent is undefined; redraw the stroke")
    return vector[0] / length, vector[1] / length


def _ray_to_boundary(point: Point, direction: Point) -> Point:
    candidates: list[tuple[float, Point]] = []
    for axis, value in ((0, 0.0), (0, 1.0), (1, 0.0), (1, 1.0)):
        component = direction[axis]
        if abs(component) <= _EPSILON:
            continue
        t = (value - point[axis]) / component
        other = point[1 - axis] + t * direction[1 - axis]
        if t >= -_EPSILON and -_EPSILON <= other <= 1.0 + _EPSILON:
            coordinate = (value, min(1.0, max(0.0, other))) if axis == 0 else (min(1.0, max(0.0, other)), value)
            candidates.append((max(0.0, t), coordinate))
    if not candidates:
        raise ValueError("Endpoint tangent cannot reach the frame boundary")
    return min(candidates, key=lambda item: item[0])[1]


def _boundary_path(start: Point, end: Point, *, clockwise: bool) -> tuple[Point, ...]:
    corners = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    start_t, end_t = _perimeter_coordinate(start), _perimeter_coordinate(end)
    if not clockwise:
        start_t, end_t = 4.0 - start_t, 4.0 - end_t
        corners = tuple(reversed(corners))
    if end_t < start_t:
        end_t += 4.0
    result: list[Point] = []
    for corner in corners:
        corner_t = _perimeter_coordinate(corner)
        if not clockwise:
            corner_t = 4.0 - corner_t
        while corner_t < start_t:
            corner_t += 4.0
        if start_t + _EPSILON < corner_t < end_t - _EPSILON:
            result.append(corner)
    return tuple(result)


def _perimeter_coordinate(point: Point) -> float:
    x, y = point
    if abs(y) <= _EPSILON:
        return x
    if abs(x - 1.0) <= _EPSILON:
        return 1.0 + y
    if abs(y - 1.0) <= _EPSILON:
        return 3.0 - x
    return 4.0 - y


def _compact(points: tuple[Point, ...]) -> tuple[Point, ...]:
    result: list[Point] = []
    for point in points:
        if not result or _distance_sq(point, result[-1]) > _EPSILON**2:
            result.append(point)
    return tuple(result)


def _self_intersects(points: tuple[Point, ...]) -> bool:
    for index in range(len(points) - 1):
        for other in range(index + 2, len(points) - 1):
            if _segments_intersect(points[index], points[index + 1], points[other], points[other + 1]):
                return True
    return False


def _polyline_intersects_boundary(points: tuple[Point, ...]) -> bool:
    return any(_on_boundary(point) for point in points[1:-1])


def _segments_intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    return (
        _cross(_subtract(b, a), _subtract(c, a)) * _cross(_subtract(b, a), _subtract(d, a)) < -_EPSILON
        and _cross(_subtract(d, c), _subtract(a, c)) * _cross(_subtract(d, c), _subtract(b, c)) < -_EPSILON
    )


def _polygon_area(points: tuple[Point, ...]) -> float:
    return sum(points[index - 1][0] * point[1] - point[0] * points[index - 1][1] for index, point in enumerate(points)) / 2.0


def _point_on_segment(point: Point, first: Point, second: Point, epsilon: float) -> bool:
    return (
        abs(_cross(_subtract(second, first), _subtract(point, first))) <= epsilon
        and min(first[0], second[0]) - epsilon <= point[0] <= max(first[0], second[0]) + epsilon
        and min(first[1], second[1]) - epsilon <= point[1] <= max(first[1], second[1]) + epsilon
    )


def _inside(point: Point) -> bool:
    return all(math.isfinite(value) and -_EPSILON <= value <= 1.0 + _EPSILON for value in point)


def _on_boundary(point: Point) -> bool:
    return (
        abs(point[0]) <= _EPSILON or abs(point[0] - 1) <= _EPSILON or abs(point[1]) <= _EPSILON or abs(point[1] - 1) <= _EPSILON
    )


def _read_point(raw: object) -> Point:
    if not isinstance(raw, list | tuple) or len(raw) != 2:
        raise ValueError("ROI point must contain two coordinates")
    return float(raw[0]), float(raw[1])


def _points_equal(first: tuple[Point, ...], second: tuple[Point, ...]) -> bool:
    return len(first) == len(second) and all(_distance_sq(a, b) <= _EPSILON**2 for a, b in zip(first, second))


def _distance_sq(first: Point, second: Point) -> float:
    return (first[0] - second[0]) ** 2 + (first[1] - second[1]) ** 2


def _subtract(first: Point, second: Point) -> Point:
    return first[0] - second[0], first[1] - second[1]


def _cross(first: Point, second: Point) -> float:
    return first[0] * second[1] - first[1] * second[0]
