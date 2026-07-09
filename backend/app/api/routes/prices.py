from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.price import Price
from app.models.product import Product
from app.models.market import Market
from pydantic import BaseModel
from typing import Optional, Any, Dict

class MarketPriceItem(BaseModel):
    market_id: int
    market_name: str
    market_address: Optional[str] = None
    market_latitude: float
    market_longitude: float
    price: float
    distance_km: float
    timestamp: Optional[str] = None
    
    class Config:
        from_attributes = True

class PriceComparisonResponse(BaseModel):
    product: Dict[str, Any]
    prices: List[MarketPriceItem]
    cheapest_price: float
    most_expensive_price: float
    average_price: float
    total_markets: int

router = APIRouter()

@router.get("/product/{product_id}", response_model=PriceComparisonResponse)
def get_prices_by_product(
    product_id: int,
    lat: float,
    lng: float,
    radius: float = 10.0,
    db: Session = Depends(get_db)
):
    """Get prices for a product with nearby markets"""
    from app.services.utils.distance import haversine_distance
    
    # Get product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get all prices for this product
    prices = db.query(Price, Market).join(Market).filter(
        Price.product_id == product_id
    ).all()
    
    # Calculate distances and filter by radius
    market_prices = []
    for price, market in prices:
        distance = haversine_distance(lat, lng, market.latitude, market.longitude)
        if distance <= radius:
            market_prices.append(MarketPriceItem(
                market_id=market.id,
                market_name=market.name,
                market_address=market.address,
                market_latitude=market.latitude,
                market_longitude=market.longitude,
                price=price.price,
                distance_km=round(distance, 2),
                timestamp=price.timestamp.isoformat() if price.timestamp else None
            ))
    
    # Sort by price
    market_prices.sort(key=lambda x: x.price)
    
    # Calculate stats
    prices_list = [mp.price for mp in market_prices]
    cheapest = min(prices_list) if prices_list else 0
    most_expensive = max(prices_list) if prices_list else 0
    average = sum(prices_list) / len(prices_list) if prices_list else 0
    
    return PriceComparisonResponse(
        product={
            "id": product.id,
            "name": product.name,
            "brand": product.brand
        },
        prices=market_prices,
        cheapest_price=cheapest,
        most_expensive_price=most_expensive,
        average_price=round(average, 2),
        total_markets=len(market_prices)
    )

@router.get("/market/{market_id}")
def get_prices_by_market(
    market_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all prices for a market"""
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    
    prices = db.query(Price, Product).join(Product).filter(
        Price.market_id == market_id
    ).limit(limit).all()
    
    prices_list = []
    for price, product in prices:
        prices_list.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_brand": product.brand,
            "price": price.price,
            "timestamp": price.timestamp.isoformat() if price.timestamp else None
        })
    
    return {
        "market": {
            "id": market.id,
            "name": market.name,
            "address": market.address
        },
        "prices": prices_list,
        "total": len(prices_list)
    }
