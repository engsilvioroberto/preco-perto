
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class PriceBase(BaseModel):
    product_id: UUID
    market_id: UUID
    price: Decimal
    original_price: Optional[Decimal] = None
    is_promotion: bool = False
    promotion_ends_at: Optional[date] = None
    source: str
    source_id: Optional[UUID] = None
    captured_at: datetime
    expires_at: Optional[datetime] = None


class PriceCreate(PriceBase):
    pass


class PriceResponse(PriceBase):
    id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


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
    is_stale: bool = False
    cost_benefit: Optional[Dict[str, Any]] = None


class ProductInfo(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None


class PriceComparisonResponse(BaseModel):
    product: ProductInfo
    prices: List[MarketPrice]
    cheapest_price: float
    most_expensive_price: float
    average_price: float
    total_markets: int
