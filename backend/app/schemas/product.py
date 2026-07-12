from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    normalized_name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None
    brand: Optional[str] = None


class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
