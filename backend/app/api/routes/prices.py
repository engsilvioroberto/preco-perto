
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from app.core.database import get_db
from app.models.price import Price
from app.models.product import Product
from app.models.market import Market
from app.schemas.price import PriceComparisonResponse, MarketPrice
from app.services.utils.distance import calculate_distance, calculate_cost_benefit
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/product/{product_id}", response_model=PriceComparisonResponse)
async def get_prices_by_product(
    product_id: str,
    lat: float = Query(...),
    lng: float = Query(...),
    radius: float = Query(10, ge=0.1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Buscar preços de um produto com comparação"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    now = datetime.utcnow()
    ninety_days_ago = now - timedelta(days=90)
    thirty_days_ago = now - timedelta(days=30)

    result = await db.execute(
        select(Price, Market)
        .join(Market, Price.market_id == Market.id)
        .where(
            and_(
                Price.product_id == product_id,
                Price.captured_at >= ninety_days_ago,
            )
        )
        .order_by(desc(Price.captured_at))
    )

    prices_with_markets = result.all()

    market_prices = []
    for price, market in prices_with_markets:
        distance = calculate_distance(lat, lng, market.latitude, market.longitude)
        if distance > radius:
            continue

        is_stale = price.captured_at < thirty_days_ago

        market_prices.append({
            "market_id": str(market.id),
            "market_name": market.name,
            "market_address": market.address,
            "market_neighborhood": market.neighborhood,
            "market_latitude": market.latitude,
            "market_longitude": market.longitude,
            "price": float(price.price),
            "original_price": float(price.original_price) if price.original_price else None,
            "is_promotion": price.is_promotion,
            "promotion_ends_at": price.promotion_ends_at.isoformat() if price.promotion_ends_at else None,
            "distance_km": round(distance, 2),
            "captured_at": price.captured_at.isoformat(),
            "source": price.source,
            "is_stale": is_stale,
        })

    market_prices.sort(key=lambda x: (x["is_stale"], x["price"]))

    if len(market_prices) >= 2:
        most_expensive_price = market_prices[-1]["price"]
        most_expensive_market = market_prices[-1]["market_name"]

        for mp in market_prices:
            savings = round(most_expensive_price - mp["price"], 2)
            cost_benefit = calculate_cost_benefit(mp["distance_km"], savings)
            cost_benefit["savings_vs_most_expensive"] = savings
            cost_benefit["most_expensive_price"] = most_expensive_price
            cost_benefit["most_expensive_market"] = most_expensive_market
            mp["cost_benefit"] = cost_benefit

    prices_list = [mp["price"] for mp in market_prices]
    avg_price = sum(prices_list) / len(prices_list) if prices_list else 0

    return {
        "product": {
            "id": str(product.id),
            "name": product.name,
            "category": product.category,
            "unit": product.unit,
            "quantity": float(product.quantity) if product.quantity else None,
        },
        "prices": market_prices,
        "cheapest_price": min(prices_list) if prices_list else 0,
        "most_expensive_price": max(prices_list) if prices_list else 0,
        "average_price": round(avg_price, 2),
        "total_markets": len(market_prices),
    }

@router.get("/market/{market_id}")
async def get_prices_by_market(
    market_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Buscar preços por mercado"""
    # Get market
    result = await db.execute(select(Market).where(Market.id == market_id))
    market = result.scalar_one_or_none()
    if not market:
        raise HTTPException(status_code=404, detail="Mercado não encontrado")
    
    # Get prices
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(Price, Product)
        .join(Product, Price.product_id == Product.id)
        .where(
            and_(
                Price.market_id == market_id,
                Price.captured_at >= thirty_days_ago
            )
        )
        .order_by(desc(Price.captured_at))
        .limit(limit)
    )
    
    prices_with_products = result.all()
    
    prices = []
    for price, product in prices_with_products:
        prices.append({
            "product_id": str(product.id),
            "product_name": product.name,
            "product_category": product.category,
            "price": float(price.price),
            "original_price": float(price.original_price) if price.original_price else None,
            "is_promotion": price.is_promotion,
            "captured_at": price.captured_at.isoformat(),
            "source": price.source
        })
    
    return {
        "market": {
            "id": str(market.id),
            "name": market.name,
            "address": market.address
        },
        "prices": prices,
        "total": len(prices)
    }
