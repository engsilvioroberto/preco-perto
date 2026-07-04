"""
Distance calculation and cost-benefit analysis service.
Uses Haversine formula for geographic distance and calculates
transport costs for walking, car, and bus.
"""

import math
from typing import Optional

# Earth radius in kilometers
EARTH_RADIUS_KM = 6371.0

# Transport constants (Ribeirão Preto context)
WALKING_SPEED_KMH = 5.0
CAR_SPEED_KMH = 30.0
CAR_COST_PER_KM = 0.75  # R$/km (gasolina + manutenção)
BUS_FARE = 4.40  # Tarifa fixa Ribeirão Preto


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance between two points using the Haversine formula.

    Args:
        lat1: Latitude of point 1 (degrees)
        lng1: Longitude of point 1 (degrees)
        lat2: Latitude of point 2 (degrees)
        lng2: Longitude of point 2 (degrees)

    Returns:
        Distance in kilometers.
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def calculate_cost_benefit(
    distance_km: float,
    price_diff: float,
    time_value_per_hour: Optional[float] = None,
) -> dict:
    """
    Calculate cost-benefit of traveling to save on a product price.

    Args:
        distance_km: One-way distance in km.
        price_diff: Price difference (savings) in R$ for the product.
        time_value_per_hour: Optional value of time in R$/hour (default: None, not included).

    Returns:
        dict with keys:
        - transport_cost_walking: R$ cost walking (always 0)
        - transport_cost_car: R$ cost by car
        - transport_cost_bus: R$ cost by bus (round trip)
        - time_walking_min: minutes walking (round trip)
        - time_car_min: minutes by car (round trip)
        - time_bus_min: minutes by bus (round trip, estimate)
        - worth_it_walking: bool - savings > cost walking
        - worth_it_car: bool - savings > cost car
        - worth_it_bus: bool - savings > cost bus
        - savings: net savings for each transport mode
    """
    # Round trip
    round_trip_km = distance_km * 2

    # Costs
    transport_cost_walking = 0.0
    transport_cost_car = round(round_trip_km * CAR_COST_PER_KM, 2)
    transport_cost_bus = BUS_FARE * 2  # Round trip fare

    # Time (round trip) in minutes
    time_walking_min = round((round_trip_km / WALKING_SPEED_KMH) * 60, 1)
    time_car_min = round((round_trip_km / CAR_SPEED_KMH) * 60, 1)
    # Bus: assume average 20 km/h including stops
    time_bus_min = round((round_trip_km / 20.0) * 60, 1)

    # Net savings per transport mode
    net_walking = round(price_diff - transport_cost_walking, 2)
    net_car = round(price_diff - transport_cost_car, 2)
    net_bus = round(price_diff - transport_cost_bus, 2)

    return {
        "transport_cost_walking": transport_cost_walking,
        "transport_cost_car": transport_cost_car,
        "transport_cost_bus": transport_cost_bus,
        "time_walking_min": time_walking_min,
        "time_car_min": time_car_min,
        "time_bus_min": time_bus_min,
        "worth_it_walking": net_walking > 0,
        "worth_it_car": net_car > 0,
        "worth_it_bus": net_bus > 0,
        "savings": {
            "walking": net_walking,
            "car": net_car,
            "bus": net_bus,
        },
    }
