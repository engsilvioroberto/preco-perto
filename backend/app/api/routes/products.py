
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse
from typing import List

router = APIRouter()

@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Buscar produtos por nome (autocomplete)"""
    search_term = f"%{q.lower()}%"
    
    result = await db.execute(
        select(Product)
        .where(
            or_(
                Product.name.ilike(search_term),
                Product.normalized_name.ilike(search_term)
            )
        )
        .limit(limit)
    )
    
    products = result.scalars().all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    """Obter produto por ID"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    return product
