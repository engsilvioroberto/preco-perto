from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import auth, products, markets, prices, receipts, admin
from app.core.rate_limit import RateLimiter

app = FastAPI(
    title="PreçoPerto API",
    version="1.0.0",
    description="API para comparação de preços colaborativa"
)

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://precoperto.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_origin_regex=r"https://.*\.github\.io",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(RateLimiter())

# Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(markets.router, prefix="/api/v1/markets", tags=["markets"])
app.include_router(prices.router, prefix="/api/v1/prices", tags=["prices"])
app.include_router(receipts.router, prefix="/api/v1/receipts", tags=["receipts"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "PreçoPerto API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}
