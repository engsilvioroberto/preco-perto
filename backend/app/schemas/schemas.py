from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    brand: Optional[str] = None
    barcode: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True

class MarketBase(BaseModel):
    name: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class MarketCreate(MarketBase):
    pass

class Market(MarketBase):
    id: int
    class Config:
        from_attributes = True

class PriceBase(BaseModel):
    product_id: int
    market_id: int
    price: float

class PriceCreate(PriceBase):
    pass

class Price(PriceBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True
