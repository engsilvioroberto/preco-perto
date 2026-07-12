import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def calculate_cost_benefit(distance_km: float, price_difference: float) -> dict:
    """
    Calculate cost-benefit of traveling to a market
    
    Args:
        distance_km: Distance to market in kilometers
        price_difference: Price difference (how much more expensive is the alternative)
    
    Returns:
        Dictionary with cost-benefit analysis
    """
    # Cost estimates
    GASOLINE_COST_PER_KM = 0.75  # R$ per km
    BUS_FARE = 4.40  # R$ fixed fare in Ribeirão Preto
    WALKING_SPEED_KMH = 5.0  # km/h
    CAR_SPEED_KMH = 30.0  # km/h average in city
    
    # Calculate costs
    transport_cost_car = round(distance_km * GASOLINE_COST_PER_KM * 2, 2)  # Round trip
    transport_cost_bus = BUS_FARE * 2  # Round trip
    transport_cost_walking = 0.0
    
    # Calculate time
    time_walking_min = (distance_km / WALKING_SPEED_KMH) * 60
    time_car_min = (distance_km / CAR_SPEED_KMH) * 60
    
    # Determine if it's worth it
    worth_it_walking = price_difference > transport_cost_walking and time_walking_min < 30
    worth_it_car = price_difference > transport_cost_car
    worth_it_bus = price_difference > transport_cost_bus
    
    return {
        "transport_cost_walking": transport_cost_walking,
        "transport_cost_car": transport_cost_car,
        "transport_cost_bus": transport_cost_bus,
        "time_walking_min": round(time_walking_min, 1),
        "time_car_min": round(time_car_min, 1),
        "worth_it_walking": worth_it_walking,
        "worth_it_car": worth_it_car,
        "worth_it_bus": worth_it_bus
    }
