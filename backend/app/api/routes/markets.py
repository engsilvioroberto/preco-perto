
import re
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.market import Market
from app.models.user import User
from app.schemas.market import MarketCreate, MarketResponse
from app.services.geocoding import geocode_address
from app.services.utils.distance import calculate_distance

router = APIRouter()

@router.get("", response_model=List[MarketResponse])
async def list_markets(db: AsyncSession = Depends(get_db)):
    """Listar todos os mercados"""
    result = await db.execute(select(Market).order_by(Market.name))
    markets = result.scalars().all()
    return [{
        "id": str(m.id),
        "name": m.name,
        "address": m.address,
        "neighborhood": m.neighborhood,
        "latitude": m.latitude,
        "longitude": m.longitude,
        "city": m.city,
        "state": m.state,
        "zipcode": m.zipcode,
        "opening_hours": m.opening_hours,
        "categories": m.categories,
        "phone": m.phone,
    } for m in markets]


@router.get("/nearby")
async def get_nearby_markets(
    lat: float = Query(...),
    lng: float = Query(...),
    radius: float = Query(10, ge=0.1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Listar mercados próximos"""
    result = await db.execute(select(Market))
    markets = result.scalars().all()

    markets_with_distance = []
    for market in markets:
        distance = calculate_distance(lat, lng, market.latitude, market.longitude)
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
    return {"markets": markets_with_distance, "total": len(markets_with_distance)}


@router.post("", response_model=MarketResponse, status_code=status.HTTP_201_CREATED)
async def create_market(
    market_data: MarketCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Cadastrar novo mercado (admin only). Faz geocoding automático se lat/lng não fornecidos."""
    lat = market_data.latitude
    lng = market_data.longitude

    if lat is None or lng is None:
        full_address = f"{market_data.address}, {market_data.neighborhood}, {market_data.city}, {market_data.state}"
        geo_result = geocode_address(full_address)
        if geo_result:
            lat = geo_result["lat"]
            lng = geo_result["lng"]
        else:
            raise HTTPException(
                status_code=400,
                detail="Não foi possível determinar coordenadas do endereço. Forneça latitude/longitude manualmente.",
            )

    now = datetime.utcnow()
    market = Market(
        id=uuid.uuid4(),
        name=market_data.name,
        cnpj=market_data.cnpj,
        address=market_data.address,
        neighborhood=market_data.neighborhood,
        city=market_data.city,
        state=market_data.state,
        zipcode=market_data.zipcode,
        latitude=lat,
        longitude=lng,
        opening_hours=market_data.opening_hours,
        categories=market_data.categories,
        phone=market_data.phone,
        created_by=admin.id,
        created_at=now,
        updated_at=now,
    )
    db.add(market)
    await db.commit()
    await db.refresh(market)
    return market


@router.get("/by-cnpj", response_model=MarketResponse)
async def get_market_by_cnpj(cnpj: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Buscar mercado pelo CNPJ extraído de uma nota fiscal escaneada"""
    digits_only = re.sub(r'\D', '', cnpj)
    result = await db.execute(select(Market))
    markets = result.scalars().all()

    for market in markets:
        if market.cnpj and re.sub(r'\D', '', market.cnpj) == digits_only:
            return {
                "id": str(market.id),
                "name": market.name,
                "cnpj": market.cnpj,
                "address": market.address,
                "neighborhood": market.neighborhood,
                "latitude": market.latitude,
                "longitude": market.longitude,
                "city": market.city,
                "state": market.state,
                "zipcode": market.zipcode,
                "opening_hours": market.opening_hours,
                "categories": market.categories,
            }

    raise HTTPException(status_code=404, detail="Mercado não encontrado para este CNPJ")

@router.get("/{market_id}", response_model=MarketResponse)
async def get_market(market_id: str, db: AsyncSession = Depends(get_db)):
    """Obter mercado por ID"""
    result = await db.execute(select(Market).where(Market.id == market_id))
    market = result.scalar_one_or_none()
    
    if not market:
        raise HTTPException(status_code=404, detail="Mercado não encontrado")
    
    return market
