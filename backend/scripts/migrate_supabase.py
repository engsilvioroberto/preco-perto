"""Migrate schema to Supabase (create tables only, no drop)."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.database import Base

# Import all models
from app.models.user import User
from app.models.market import Market
from app.models.product import Product
from app.models.price import Price
from app.models.receipt import Receipt
from app.models.receipt_item import ReceiptItem
from app.models.offer_flyer import OfferFlyer
from app.models.offer_flyer_item import OfferFlyerItem

DATABASE_URL = (
    "postgresql+asyncpg://postgres.acrgptiaqsioezqlbisg:u4fBah5WVf6Muhwb"
    "@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
)

async def migrate():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        print("Creating tables in Supabase...")
        await conn.run_sync(Base.metadata.create_all)
        print("Done!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())