
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, products, markets, prices, receipts

app = FastAPI(
    title="PreçoPerto API",
    version="1.0.0",
    description="API para comparação de preços colaborativa"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(markets.router, prefix="/api/v1/markets", tags=["markets"])
app.include_router(prices.router, prefix="/api/v1/prices", tags=["prices"])
app.include_router(receipts.router, prefix="/api/v1/receipts", tags=["receipts"])

@app.get("/")
async def root():
    return {"message": "PreçoPerto API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}
