from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductInfo(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None


class MarketPrice(BaseModel):
    market_id: str
    market_name: str
    market_address: str
    market_neighborhood: Optional[str] = None
    market_latitude: float
    market_longitude: float
    price: float
    original_price: Optional[float] = None
    is_promotion: bool
    promotion_ends_at: Optional[str] = None
    distance_km: float
    captured_at: str
    source: str
    cost_benefit: Optional[Dict[str, Any]] = None


class PriceComparisonResponse(BaseModel):
    product: ProductInfo
    prices: List[MarketPrice]
    cheapest_price: float
    most_expensive_price: float
    average_price: float
    total_markets: int
