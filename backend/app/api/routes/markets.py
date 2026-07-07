
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.core.database import get_db
from app.models.market import Market
from app.schemas.market import MarketResponse
from typing import List
import math

router = APIRouter()

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km"""
    R = 6371  # Earth radius in km
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

@router.get("/nearby", response_model=List[MarketResponse])
async def get_nearby_markets(
    lat: float = Query(...),
    lng: float = Query(...),
    radius: float = Query(10, ge=0.1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Listar mercados próximos"""
    result = await db.execute(select(Market))
    markets = result.scalars().all()
    
    # Filter by distance and sort
    markets_with_distance = []
    for market in markets:
        distance = haversine_distance(lat, lng, market.latitude, market.longitude)
        if distance <= radius:
            market_dict = {
                "id": str(market.id),
                "name": market.name,
                "address": market.address,
                "neighborhood": market.neighborhood,
                "latitude": market.latitude,
                "longitude": market.longitude,
                "distance_km": round(distance, 2),
                "opening_hours": market.opening_hours,
                "categories": market.categories
            }
            markets_with_distance.append(market_dict)
    
    # Sort by distance
    markets_with_distance.sort(key=lambda x: x["distance_km"])
    return markets_with_distance

@router.get("/by-cnpj", response_model=MarketResponse)
async def get_market_by_cnpj(cnpj: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Buscar mercado pelo CNPJ extraído de uma nota fiscal escaneada"""
    digits_only = re.sub(r'\D', '', cnpj)
    result = await db.execute(select(Market))
    markets = result.scalars().all()

    for market in markets:
        if market.cnpj and re.sub(r'\D', '', market.cnpj) == digits_only:
            return market

    raise HTTPException(status_code=404, detail="Mercado não encontrado para este CNPJ")

@router.get("/{market_id}", response_model=MarketResponse)
async def get_market(market_id: str, db: AsyncSession = Depends(get_db)):
    """Obter mercado por ID"""
    result = await db.execute(select(Market).where(Market.id == market_id))
    market = result.scalar_one_or_none()
    
    if not market:
        raise HTTPException(status_code=404, detail="Mercado não encontrado")
    
    return market
