#!/usr/bin/env python3
"""
Extract line and area geometries from a DXF file and output separate GeoJSON files for each entity.

Supported entities:
- Lines: LINE, LWPOLYLINE, POLYLINE, SPLINE (approximated)
- Areas: POLYGON, HATCH, CIRCLE, ELLIPSE, ARC (converted to closed paths)

Usage examples:
  python extract_dxf_coords.py --input "../5号线轴线＋保护区红线2000(2023.8.31）.dxf" --output-dir output \
      --src-crs EPSG:4547  # example: CGCS2000/GK zone (replace with the correct EPSG)

Notes:
- If you are not sure of the source CRS of the DXF (it is often in projected meters),
  omit --src-crs to export raw XY coordinates.
- To filter layers or entity types, use --layers and/or --types.
- Each line/area will be output as a separate GeoJSON file.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

try:
    import ezdxf  # type: ignore
except Exception as exc:  # pragma: no cover - dependency import error display
    raise SystemExit(
        "Missing dependency: ezdxf. Install with: pip install ezdxf"
    ) from exc

try:
    from pyproj import Transformer  # type: ignore
except Exception:
    Transformer = None  # lazy optional dependency


Coordinate = Tuple[float, float]


def _to_xy_tuple(point) -> Coordinate:
    # ezdxf uses Vector-like objects with x, y, z attributes
    return float(point[0]), float(point[1])


def _transform_points(
    points: Sequence[Coordinate], src_crs: Optional[str], dst_crs: str
) -> List[Coordinate]:
    if src_crs is None:
        return list(points)
    if Transformer is None:
        raise SystemExit(
            "pyproj is required for CRS transformation. Install with: pip install pyproj"
        )
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    xs, ys = zip(*points) if points else ([], [])
    if not xs:
        return []
    tx, ty = transformer.transform(xs, ys)
    return list(zip(map(float, tx), map(float, ty)))


def _approximate_spline(entity) -> List[Coordinate]:
    # Try multiple ezdxf APIs depending on version
    try:
        pts = entity.approximate(segments=100)  # ezdxf >= 0.16
    except Exception:
        try:
            pts = entity.flattening(distance=1.0)  # type: ignore[attr-defined]
        except Exception:
            try:
                pts = entity.control_points
            except Exception:
                pts = []
    return [_to_xy_tuple(p) for p in pts]


def _approximate_arc(entity) -> List[Coordinate]:
    """Convert ARC to a series of points"""
    try:
        center = _to_xy_tuple(entity.dxf.center)
        radius = float(entity.dxf.radius)
        start_angle = float(entity.dxf.start_angle)
        end_angle = float(entity.dxf.end_angle)
        
        # Normalize angles
        if end_angle < start_angle:
            end_angle += 360
        
        # Create points along the arc
        num_points = max(8, int((end_angle - start_angle) / 5))  # At least 8 points
        points = []
        for i in range(num_points + 1):
            angle = start_angle + (end_angle - start_angle) * i / num_points
            angle_rad = math.radians(angle)
            x = center[0] + radius * math.cos(angle_rad)
            y = center[1] + radius * math.sin(angle_rad)
            points.append((x, y))
        return points
    except Exception:
        return []


def _approximate_circle(entity) -> List[Coordinate]:
    """Convert CIRCLE to a series of points"""
    try:
        center = _to_xy_tuple(entity.dxf.center)
        radius = float(entity.dxf.radius)
        
        # Create 32 points around the circle
        num_points = 32
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        # Close the circle
        points.append(points[0])
        return points
    except Exception:
        return []


def _approximate_ellipse(entity) -> List[Coordinate]:
    """Convert ELLIPSE to a series of points"""
    try:
        center = _to_xy_tuple(entity.dxf.center)
        major_axis = _to_xy_tuple(entity.dxf.major_axis)
        ratio = float(entity.dxf.ratio)
        
        # Calculate minor axis
        major_length = math.sqrt(major_axis[0]**2 + major_axis[1]**2)
        minor_length = major_length * ratio
        
        # Create points around the ellipse
        num_points = 32
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            # Parametric equation of ellipse
            x = center[0] + major_length * math.cos(angle)
            y = center[1] + minor_length * math.sin(angle)
            points.append((x, y))
        # Close the ellipse
        points.append(points[0])
        return points
    except Exception:
        return []


def _collect_line_coords(entity) -> Optional[List[Coordinate]]:
    """Extract coordinates from line-type entities"""
    etype = entity.dxftype()
    if etype == "LINE":
        start = _to_xy_tuple(entity.dxf.start)
        end = _to_xy_tuple(entity.dxf.end)
        return [start, end]
    elif etype == "LWPOLYLINE":
        return [
            (float(x), float(y))
            for x, y, *_ in entity.get_points()  # handles bulge but we ignore it here
        ]
    elif etype == "POLYLINE":
        try:
            pts = [v.dxf.location for v in entity.vertices]
        except Exception:
            pts = []
        return [_to_xy_tuple(p) for p in pts]
    elif etype == "SPLINE":
        return _approximate_spline(entity)
    return None


def _collect_area_coords(entity) -> Optional[List[Coordinate]]:
    """Extract coordinates from area-type entities"""
    etype = entity.dxftype()
    
    if etype == "CIRCLE":
        return _approximate_circle(entity)
    elif etype == "ELLIPSE":
        return _approximate_ellipse(entity)
    elif etype == "ARC":
        return _approximate_arc(entity)
    elif etype == "HATCH":
        try:
            # Extract boundary paths from HATCH
            paths = []
            for path in entity.paths:
                if hasattr(path, 'vertices'):
                    path_points = [_to_xy_tuple(v.location) for v in path.vertices]
                    if path_points:
                        paths.append(path_points)
            # Return the first path for now (could be enhanced to handle multiple paths)
            return paths[0] if paths else None
        except Exception:
            return None
    elif etype == "LWPOLYLINE":
        # Check if it's closed (area)
        try:
            if entity.closed:
                return [
                    (float(x), float(y))
                    for x, y, *_ in entity.get_points()
                ]
        except Exception:
            pass
    elif etype == "POLYLINE":
        # Check if it's closed (area)
        try:
            if entity.closed:
                pts = [v.dxf.location for v in entity.vertices]
                return [_to_xy_tuple(p) for p in pts]
        except Exception:
            pass
    
    return None


def _get_entity_properties(entity) -> Dict:
    """Extract common properties from entity"""
    props = {
        "type": entity.dxftype(),
        "layer": getattr(entity.dxf, "layer", "0"),
    }
    
    # Try to get color information
    try:
        color = entity.dxf.color
        if color != 256:  # 256 is "BYLAYER"
            props["color"] = color
    except Exception:
        pass
    
    # Try to get lineweight
    try:
        lineweight = entity.dxf.lineweight
        if lineweight != -1:  # -1 is "BYLAYER"
            props["lineweight"] = lineweight
    except Exception:
        pass
    
    # Try to get linetype
    try:
        linetype = entity.dxf.linetype
        if linetype != "BYLAYER":
            props["linetype"] = linetype
    except Exception:
        pass
    
    return props


def _generate_filename(entity, index: int, output_dir: Path) -> Path:
    """Generate filename for individual entity"""
    etype = entity.dxftype()
    layer = getattr(entity.dxf, "layer", "0")
    
    # Clean layer name for filename
    safe_layer = "".join(c for c in layer if c.isalnum() or c in "_-").rstrip("_")
    if not safe_layer:
        safe_layer = "layer"
    
    # Generate filename
    filename = f"{safe_layer}_{etype}_{index:04d}.geojson"
    return output_dir / filename


def extract_geometries_from_dxf(
    input_path: Path,
    output_dir: Path,
    *,
    allow_types: Optional[Iterable[str]] = None,
    allow_layers: Optional[Iterable[str]] = None,
    src_crs: Optional[str] = None,
    dst_crs: str = "EPSG:4326",
) -> Dict:
    doc = ezdxf.readfile(str(input_path))
    msp = doc.modelspace()

    types = None if allow_types is None else {t.upper() for t in allow_types}
    layers = None if allow_layers is None else set(allow_layers)

    lines_features: List[Dict] = []
    areas_features: List[Dict] = []
    individual_files: List[str] = []
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    entity_index = 0
    for entity in msp:
        etype = entity.dxftype()
        if types is not None and etype.upper() not in types:
            continue
        if layers is not None:
            try:
                if entity.dxf.layer not in layers:
                    continue
            except Exception:
                pass

        # Try to extract as line first
        line_coords = _collect_line_coords(entity)
        if line_coords and len(line_coords) >= 2:
            transformed = _transform_points(line_coords, src_crs, dst_crs)
            
            # Create individual GeoJSON file for this line
            individual_file = _generate_filename(entity, entity_index, output_dir)
            
            feature = {
                "type": "Feature",
                "properties": _get_entity_properties(entity),
                "geometry": {
                    "type": "LineString",
                    "coordinates": transformed,
                },
            }
            
            # Write individual file
            individual_file.write_text(json.dumps(feature, ensure_ascii=False, indent=2))
            # store relative path for web viewer compatibility
            try:
                individual_files.append(str(individual_file.relative_to(output_dir)))
            except Exception:
                individual_files.append(individual_file.name)
            
            # Also collect for summary
            lines_features.append(feature)
            entity_index += 1
            continue

        # Try to extract as area
        area_coords = _collect_area_coords(entity)
        if area_coords and len(area_coords) >= 3:
            transformed = _transform_points(area_coords, src_crs, dst_crs)
            
            # Create individual GeoJSON file for this area
            individual_file = _generate_filename(entity, entity_index, output_dir)
            
            feature = {
                "type": "Feature",
                "properties": _get_entity_properties(entity),
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [transformed],  # GeoJSON Polygon format
                },
            }
            
            # Write individual file
            individual_file.write_text(json.dumps(feature, ensure_ascii=False, indent=2))
            # store relative path for web viewer compatibility
            try:
                individual_files.append(str(individual_file.relative_to(output_dir)))
            except Exception:
                individual_files.append(individual_file.name)
            
            # Also collect for summary
            areas_features.append(feature)
            entity_index += 1

    # Create summary file
    summary = {
        "type": "FeatureCollection",
        "properties": {
            "summary": {
                "total_features": len(lines_features) + len(areas_features),
                "lines": len(lines_features),
                "areas": len(areas_features),
                "layers": list(set(
                    f["properties"]["layer"] 
                    for f in lines_features + areas_features
                )),
                "individual_files": individual_files
            }
        },
        "features": lines_features + areas_features
    }
    
    # Write summary file
    summary_file = output_dir / "summary.geojson"
    summary_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Extract line and area geometries from a DXF file and output separate GeoJSON files for each entity."
        )
    )
    p.add_argument("--input", required=True, help="Path to the DXF file")
    p.add_argument(
        "--output-dir", required=True, help="Directory to write individual GeoJSON files"
    )
    p.add_argument(
        "--types",
        default="LINE,LWPOLYLINE,POLYLINE,SPLINE,CIRCLE,ELLIPSE,ARC,HATCH",
        help="Comma-separated entity types to include",
    )
    p.add_argument(
        "--layers",
        default=None,
        help="Comma-separated layer names to include; omit for all layers",
    )
    p.add_argument(
        "--src-crs",
        default=None,
        help=(
            "Source CRS like 'EPSG:4547'. If omitted, raw DXF XY are exported."
        ),
    )
    p.add_argument(
        "--dst-crs",
        default="EPSG:4326",
        help="Destination CRS (default WGS84/EPSG:4326)",
    )
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    output_dir = Path(args.output_dir).expanduser().resolve()
    
    allow_layers = (
        None if args.layers in (None, "") else [s for s in args.layers.split(",") if s]
    )
    allow_types = [s for s in args.types.split(",") if s]

    summary = extract_geometries_from_dxf(
        input_path,
        output_dir,
        allow_types=allow_types,
        allow_layers=allow_layers,
        src_crs=args.src_crs,
        dst_crs=args.dst_crs,
    )

    print(f"\n✅ Extraction completed!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Summary: {summary['properties']['summary']['total_features']} total features")
    print(f"  - Lines: {summary['properties']['summary']['lines']}")
    print(f"  - Areas: {summary['properties']['summary']['areas']}")
    print(f"  - Layers: {', '.join(summary['properties']['summary']['layers'])}")
    print(f"📄 Summary file: {output_dir / 'summary.geojson'}")
    print(f"🔗 Individual files: {len(summary['properties']['summary']['individual_files'])}")


if __name__ == "__main__":
    main()


