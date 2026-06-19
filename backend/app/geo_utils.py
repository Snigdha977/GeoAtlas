from math import radians, sin, cos, sqrt, atan2
from typing import Dict

EARTH_RADIUS_KM = 6371.0


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate latitude and longitude values.

    Args:
        latitude: Latitude in degrees.
        longitude: Longitude in degrees.

    Returns:
        True if coordinates are valid, False otherwise.
    """
    return (
        -90.0 <= latitude <= 90.0
        and -180.0 <= longitude <= 180.0
    )


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate the great-circle distance between two coordinates.

    Args:
        lat1: Latitude of first point.
        lon1: Longitude of first point.
        lat2: Latitude of second point.
        lon2: Longitude of second point.

    Returns:
        Distance in kilometers.
    """
    if not (
        validate_coordinates(lat1, lon1)
        and validate_coordinates(lat2, lon2)
    ):
        raise ValueError("Invalid coordinates provided.")

    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(
        radians,
        [lat1, lon1, lat2, lon2]
    )

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(EARTH_RADIUS_KM * c, 2)


def get_bounding_box(
    latitude: float,
    longitude: float,
    radius_km: float = 10.0
) -> Dict[str, float]:
    """
    Compute an approximate bounding box around a coordinate.

    Args:
        latitude: Center latitude.
        longitude: Center longitude.
        radius_km: Radius in kilometers.

    Returns:
        Dictionary containing min/max latitude and longitude.
    """
    if not validate_coordinates(latitude, longitude):
        raise ValueError("Invalid coordinates provided.")

    delta_lat = radius_km / 111.0
    delta_lon = radius_km / (
        111.0 * cos(radians(latitude))
    )

    return {
        "min_lat": latitude - delta_lat,
        "max_lat": latitude + delta_lat,
        "min_lon": longitude - delta_lon,
        "max_lon": longitude + delta_lon,
    }


def format_coordinates(
    latitude: float,
    longitude: float
) -> str:
    """
    Format coordinates to six decimal places.

    Args:
        latitude: Latitude value.
        longitude: Longitude value.

    Returns:
        Formatted coordinate string.
    """
    if not validate_coordinates(latitude, longitude):
        raise ValueError("Invalid coordinates provided.")

    return f"{latitude:.6f}, {longitude:.6f}"


def coordinates_to_geojson(
    latitude: float,
    longitude: float
) -> Dict:
    """
    Convert coordinates to GeoJSON Point format.

    Args:
        latitude: Latitude value.
        longitude: Longitude value.

    Returns:
        GeoJSON Point dictionary.
    """
    if not validate_coordinates(latitude, longitude):
        raise ValueError("Invalid coordinates provided.")

    return {
        "type": "Point",
        "coordinates": [longitude, latitude],
    }


def midpoint_coordinates(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> Dict[str, float]:
    """
    Calculate the midpoint between two coordinates.

    Args:
        lat1: Latitude of first point.
        lon1: Longitude of first point.
        lat2: Latitude of second point.
        lon2: Longitude of second point.

    Returns:
        Dictionary containing midpoint latitude and longitude.
    """
    if not (
        validate_coordinates(lat1, lon1)
        and validate_coordinates(lat2, lon2)
    ):
        raise ValueError("Invalid coordinates provided.")

    return {
        "latitude": round((lat1 + lat2) / 2, 6),
        "longitude": round((lon1 + lon2) / 2, 6),
    }


def is_within_radius(
    center_lat: float,
    center_lon: float,
    point_lat: float,
    point_lon: float,
    radius_km: float
) -> bool:
    """
    Determine whether a point lies within a given radius.

    Args:
        center_lat: Center latitude.
        center_lon: Center longitude.
        point_lat: Target latitude.
        point_lon: Target longitude.
        radius_km: Radius in kilometers.

    Returns:
        True if point lies within radius, False otherwise.
    """
    distance = haversine_distance(
        center_lat,
        center_lon,
        point_lat,
        point_lon,
    )

    return distance <= radius_km
