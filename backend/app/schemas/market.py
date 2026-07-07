
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class MarketBase(BaseModel):
    name: str
    address: str
    neighborhood: Optional[str] = None
    latitude: float
    longitude: float


class MarketCreate(BaseModel):
    name: str
    cnpj: Optional[str] = None
    address: str
    neighborhood: Optional[str] = None
    city: str = "Ribeirão Preto"
    state: str = "SP"
    zipcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_hours: Optional[Dict[str, Any]] = None
    categories: Optional[List[str]] = None
    phone: Optional[str] = None


class MarketResponse(MarketBase):
    id: UUID
    cnpj: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    opening_hours: Optional[Dict[str, Any]] = None
    categories: Optional[List[str]] = None
    distance_km: Optional[float] = None

    class Config:
        from_attributes = True
