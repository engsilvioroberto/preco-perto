from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MarketBase(BaseModel):
    name: str
    address: str
    neighborhood: Optional[str] = None
    latitude: float
    longitude: float


class MarketResponse(MarketBase):
    id: str
    opening_hours: Optional[Dict[str, Any]] = None
    categories: Optional[List[str]] = None
    distance_km: Optional[float] = None
    
    class Config:
        from_attributes = True
