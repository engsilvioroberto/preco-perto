from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class OfferFlyerItemOut(BaseModel):
    id: UUID
    product_id: Optional[UUID] = None
    product_name: Optional[str] = None
    description: str
    price: float
    original_price: Optional[float] = None
    confidence: Optional[float] = None
    is_confirmed: bool = False


class OfferFlyerUploadResponse(BaseModel):
    offer_flyer_id: UUID
    status: str
    items: List[OfferFlyerItemOut] = []
    total_items: int = 0


class OfferFlyerDetailResponse(BaseModel):
    id: UUID
    status: str
    market_id: UUID
    market_name: Optional[str] = None
    valid_from: date
    valid_until: date
    items: List[OfferFlyerItemOut] = []
    total_items: int = 0
    confirmed_items: int = 0
    pending_review: int = 0


class OfferFlyerItemConfirm(BaseModel):
    item_id: UUID
    product_id: UUID
    is_confirmed: bool = True


class OfferFlyerConfirmIn(BaseModel):
    items: List[OfferFlyerItemConfirm]


class OfferFlyerConfirmResponse(BaseModel):
    offer_flyer_id: UUID
    status: str
    confirmed_items: int
    prices_added: int
    message: str
