from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.base import SessionLocal
from app.models.product import Product as ProductModel
from app.models.market import Market as MarketModel
from app.models.price import Price as PriceModel
from app.schemas import schemas
from typing import List

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# ─── API Routes ───────────────────────────────────────────────
from app.api.routes.products import router as products_router
from app.api.routes.markets import router as markets_router
from app.api.routes.prices import router as prices_router
from app.api.routes.auth import router as auth_router
from app.api.routes.receipts import router as receipts_router

app = FastAPI(title="PreçoPerto API")

# ─── Database Dependency ──────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─── API v1 Endpoints ─────────────────────────────────────────
app.include_router(products_router, prefix="/api/v1/products", tags=["Products"])
app.include_router(markets_router, prefix="/api/v1/markets", tags=["Markets"])
app.include_router(prices_router, prefix="/api/v1/prices", tags=["Prices"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(receipts_router, prefix="/api/v1/receipts", tags=["Receipts"])

# ─── Legacy / Direct Routes ───────────────────────────────────
@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ProductModel).offset(skip).limit(limit).all()

@app.post("/markets/", response_model=schemas.Market)
def create_market(market: schemas.MarketCreate, db: Session = Depends(get_db)):
    db_market = MarketModel(**market.model_dump())
    db.add(db_market)
    db.commit()
    db.refresh(db_market)
    return db_market

@app.get("/markets/", response_model=List[schemas.Market])
def read_markets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(MarketModel).offset(skip).limit(limit).all()

@app.post("/prices/", response_model=schemas.Price)
def create_price(price: schemas.PriceCreate, db: Session = Depends(get_db)):
    db_price = PriceModel(**price.model_dump())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

@app.get("/prices/", response_model=List[schemas.Price])
def read_prices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(PriceModel).offset(skip).limit(limit).all()

# ─── Frontend Static Serving ──────────────────────────────────
frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")

# Mount at /preco-perto/ (for GitHub Pages compatibility / cached browsers)
if os.path.exists(frontend_dist):
    app.mount("/preco-perto", StaticFiles(directory=frontend_dist, html=True), name="frontend_ghpages")

# Mount assets directly (for base=/ builds)
assets_dir = os.path.join(frontend_dist, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Serve root SPA — catch all remaining paths for the frontend SPA
# This must come AFTER all API routes to avoid hijacking them
@app.get("/")
def serve_home():
    return FileResponse(os.path.join(frontend_dist, "index.html"))

@app.get("/{path:path}")
def serve_static(path: str):
    """Serve static files for the SPA. Only SPA-fallback for non-file paths."""
    file_path = os.path.join(frontend_dist, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    # SPA fallback only for paths that look like routes (no file extension)
    # Don't return index.html for .js/.css/.json requests — return 404 instead
    if '.' not in path.split('/')[-1]:
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    return HTTPException(status_code=404, detail="Not found")
