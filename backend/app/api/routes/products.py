from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.product import Product
from app.schemas.schemas import Product

router = APIRouter()

@router.get("/search", response_model=List[Product])
def search_products(q: str, limit: int = 10, db: Session = Depends(get_db)):
    """Search products by name (fuzzy match)"""
    from app.services.search_service import search_products as fuzzy_search
    results = fuzzy_search(db, q, limit=limit)
    return [product for product, score in results]

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
