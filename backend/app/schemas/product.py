from datetime import datetime
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    normalized_name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[Decimal] = None
    brand: Optional[str] = None
    barcode: Optional[str] = None
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductSearchResponse(BaseModel):
    products: List[ProductResponse]
    total: int
