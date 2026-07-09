from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.market import Market as MarketModel
from app.schemas.schemas import Market as MarketSchema

router = APIRouter()

@router.get("/nearby", response_model=List[MarketSchema])
def get_nearby_markets(
    lat: float,
    lng: float,
    radius: float = 10.0,
    db: Session = Depends(get_db)
):
    """Get markets near a location"""
    from app.services.utils.distance import haversine_distance
    
    markets = db.query(MarketModel).all()
    
    # Filter by distance
    nearby = []
    for market in markets:
        if market.latitude is None or market.longitude is None:
            continue
        distance = haversine_distance(lat, lng, market.latitude, market.longitude)
        if distance <= radius:
            nearby.append(market)
    
    return nearby

@router.get("/{market_id}", response_model=MarketSchema)
def get_market(market_id: int, db: Session = Depends(get_db)):
    """Get market by ID"""
    market = db.query(MarketModel).filter(MarketModel.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market
