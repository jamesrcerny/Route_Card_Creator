"""Pure KML parsing and route-card data computation for RouteCardTool.

Reads WinTAK-style KML files (Placemarks with a <name> and a <Point><coordinates>)
and turns the ordered list of points into route-card rows: an 8-digit MGRS grid,
plus the flow/distance/direction to the next point in the route.
"""
import math
import re
import xml.etree.ElementTree as ET
from datetime import date

import mgrs
from geopy.distance import geodesic
from pygeomag import GeoMag, decimal_year_from_date

_MGRS = mgrs.MGRS()
_GEOMAG = GeoMag()
_DECIMAL_YEAR = decimal_year_from_date(date.today())
_KML_NS = "{http://www.opengis.net/kml/2.2}"

# (pattern, checkpoint display label, flow short label). None display/flow means
# "derive from the captured group" (used for CP n / CP A style checkpoints).
_ROLE_PATTERNS = [
    (re.compile(r"^A?IP$", re.IGNORECASE), "Insert (IP)", "IP"),
    (re.compile(r"^A?ORP$", re.IGNORECASE), "ORP", "ORP"),
    (re.compile(r"^A?EX$", re.IGNORECASE), "Extract (Ex)", "Ex"),
    (re.compile(r"^CP\s*([A-Za-z0-9]+)$", re.IGNORECASE), None, None),
]


def classify_point(name):
    """Returns (checkpoint_display_label, flow_short_label) for a placemark name."""
    name = name.strip()
    for pattern, display, flow in _ROLE_PATTERNS:
        match = pattern.match(name)
        if match:
            if display is None:
                suffix = match.group(1).upper()
                return suffix, suffix
            return display, flow
    return name, name


def parse_kml_points(path):
    """Returns an ordered list of {"name", "lat", "lon"} for every Point placemark in path."""
    tree = ET.parse(path)
    root = tree.getroot()
    points = []
    for placemark in root.iter(f"{_KML_NS}Placemark"):
        name_el = placemark.find(f"{_KML_NS}name")
        coords_el = placemark.find(f"{_KML_NS}Point/{_KML_NS}coordinates")
        if name_el is None or coords_el is None or not coords_el.text:
            continue
        lon_str, lat_str, *_ = coords_el.text.strip().split(",")
        points.append({
            "name": (name_el.text or "").strip(),
            "lat": float(lat_str),
            "lon": float(lon_str),
        })
    return points


def true_bearing_deg(lat1, lon1, lat2, lon2):
    """Forward true compass bearing in degrees (0-360) from point 1 to point 2."""
    lat1r, lat2r = math.radians(lat1), math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlon) * math.cos(lat2r)
    y = math.cos(lat1r) * math.sin(lat2r) - math.sin(lat1r) * math.cos(lat2r) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def magnetic_declination(lat, lon):
    """Magnetic declination in degrees (East positive) at a point, using the current WMM."""
    return _GEOMAG.calculate(glat=lat, glon=lon, alt=0, time=_DECIMAL_YEAR).d


def magnetic_bearing_deg(lat1, lon1, lat2, lon2):
    """Forward magnetic compass bearing in degrees (0-360) from point 1 to point 2."""
    true_bearing = true_bearing_deg(lat1, lon1, lat2, lon2)
    declination = magnetic_declination(lat1, lon1)
    return (true_bearing - declination) % 360


def to_mgrs(lat, lon):
    """8-digit MGRS grid reference (4-digit easting + 4-digit northing, 10m precision)."""
    return _MGRS.toMGRS(lat, lon, MGRSPrecision=4)


def build_route(path):
    """Parses a KML file into route-card rows, in document order.

    Each row covers one checkpoint: its label, its MGRS grid, and the flow/distance
    (meters)/direction (magnetic degrees) of the leg leading to the *next* checkpoint
    (blank on the last row).
    """
    points = parse_kml_points(path)
    if not points:
        raise ValueError(f"No placemarks with point coordinates found in {path}")

    rows = []
    for i, point in enumerate(points):
        display, flow_short = classify_point(point["name"])
        grid = to_mgrs(point["lat"], point["lon"])
        if i + 1 < len(points):
            nxt = points[i + 1]
            _, next_flow_short = classify_point(nxt["name"])
            distance_m = round(geodesic(
                (point["lat"], point["lon"]), (nxt["lat"], nxt["lon"])).meters)
            direction_deg = round(magnetic_bearing_deg(
                point["lat"], point["lon"], nxt["lat"], nxt["lon"]))
            flow = f"{flow_short}-{next_flow_short}"
        else:
            flow, distance_m, direction_deg = "", "", ""
        rows.append({
            "checkpoint": display,
            "grid": grid,
            "flow": flow,
            "distance": distance_m,
            "direction": direction_deg,
        })
    return rows
