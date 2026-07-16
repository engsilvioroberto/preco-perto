"""Seed Supabase with demo data (markets, products, prices)."""
import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.models.user import User
from app.models.market import Market
from app.models.product import Product
from app.models.price import Price
from app.core.security import hash_password
from app.services.product_normalization import normalize_product

DATABASE_URL = (
    "postgresql+asyncpg://postgres.acrgptiaqsioezqlbisg:u4fBah5WVf6Muhwb"
    "@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
)

async def seed():
    engine = create_async_engine(DATABASE_URL, connect_args={"statement_cache_size": 0})
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        async with session.begin():
            # Users
            print("Creating users...")
            admin = User(
                id=uuid.uuid4(), email="admin@precoperto.com", name="Admin PreçoPerto",
                password_hash=hash_password("admin123"), is_admin=True,
                created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
            )
            user = User(
                id=uuid.uuid4(), email="joao@gmail.com", name="João Silva",
                password_hash=hash_password("joao123"), is_admin=False,
                created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
            )
            session.add_all([admin, user])

            # Markets
            print("Creating markets...")
            markets = [
                Market(id=uuid.uuid4(), name="Carrefour Ribeirão",
                    cnpj="45.543.915/0001-81", address="Av. Presidente Vargas, 2001",
                    neighborhood="Centro", city="Ribeirão Preto", state="SP",
                    zipcode="14015-510", latitude=-21.1767, longitude=-47.8208,
                    categories=["supermercado", "atacado"], phone="(16) 3977-1000",
                    created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
                Market(id=uuid.uuid4(), name="Extra Hiper Ribeirão",
                    cnpj="33.014.556/0001-96", address="Av. Wladimir Meirelles Ferreira, 2500",
                    neighborhood="Jardim Botânico", city="Ribeirão Preto", state="SP",
                    zipcode="14024-100", latitude=-21.1900, longitude=-47.8100,
                    categories=["supermercado"], phone="(16) 3603-2000",
                    created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
                Market(id=uuid.uuid4(), name="Dalben Supermercados",
                    cnpj="07.545.678/0001-90", address="Rua General Osório, 1500",
                    neighborhood="Campos Elíseos", city="Ribeirão Preto", state="SP",
                    zipcode="14085-010", latitude=-21.1850, longitude=-47.8250,
                    categories=["supermercado"], phone="(16) 3610-3000",
                    created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
                Market(id=uuid.uuid4(), name="Savegnago Supermercados",
                    cnpj="51.890.123/0001-45", address="Av. Costabile Romano, 1000",
                    neighborhood="Quintino Facci I", city="Ribeirão Preto", state="SP",
                    zipcode="14070-100", latitude=-21.2000, longitude=-47.8300,
                    categories=["supermercado"], phone="(16) 3916-4000",
                    created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
                Market(id=uuid.uuid4(), name="Paulistão Supermercados",
                    cnpj="52.345.678/0001-12", address="Av. Presidente Vargas, 3500",
                    neighborhood="Ipiranga", city="Ribeirão Preto", state="SP",
                    zipcode="14015-510", latitude=-21.1800, longitude=-47.8150,
                    categories=["supermercado"], phone="(16) 3620-5000",
                    created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            ]
            session.add_all(markets)

            # Products
            print("Creating products...")
            products_data = [
                ("Leite Integral Piracanjuba 1L", "laticínios", "L", 1.0, "Piracanjuba"),
                ("Arroz Branco Tio João 5kg", "grãos", "kg", 5.0, "Tio João"),
                ("Feijão Preto Camil 1kg", "grãos", "kg", 1.0, "Camil"),
                ("Açúcar Cristal União 1kg", "adoçantes", "kg", 1.0, "União"),
                ("Óleo de Soja Liza 900ml", "óleos", "ml", 900.0, "Liza"),
                ("Café Torrado Melitta 500g", "bebidas", "g", 500.0, "Melitta"),
                ("Sabão em Pó Omo 1.6kg", "limpeza", "kg", 1.6, "Omo"),
                ("Shampoo Pantene 400ml", "higiene", "ml", 400.0, "Pantene"),
                ("Papel Higiênico Personal 12un", "higiene", "un", 12.0, "Personal"),
                ("Cebola Kg", "hortifruti", "kg", 1.0, None),
            ]
            products = []
            for name, category, unit, qty, brand in products_data:
                p = Product(id=uuid.uuid4(), name=name,
                    normalized_name=normalize_product(name), category=category,
                    unit=unit, quantity=qty, brand=brand,
                    created_at=datetime.utcnow(), updated_at=datetime.utcnow())
                products.append(p)
            session.add_all(products)
            await session.flush()

            product_map = {p.name: p for p in products}
            market_map = {m.name: m for m in markets}

            # Prices
            print("Creating prices...")
            now = datetime.utcnow()
            prices_data = [
                ("Leite Integral Piracanjuba 1L", "Carrefour Ribeirão", 4.99, 5.49, True),
                ("Leite Integral Piracanjuba 1L", "Extra Hiper Ribeirão", 5.29, None, False),
                ("Leite Integral Piracanjuba 1L", "Dalben Supermercados", 5.49, None, False),
                ("Leite Integral Piracanjuba 1L", "Savegnago Supermercados", 5.99, None, False),
                ("Leite Integral Piracanjuba 1L", "Paulistão Supermercados", 6.49, None, False),
                ("Arroz Branco Tio João 5kg", "Carrefour Ribeirão", 22.90, 25.90, True),
                ("Arroz Branco Tio João 5kg", "Extra Hiper Ribeirão", 24.50, None, False),
                ("Arroz Branco Tio João 5kg", "Dalben Supermercados", 25.90, None, False),
                ("Feijão Preto Camil 1kg", "Carrefour Ribeirão", 7.99, 8.99, True),
                ("Feijão Preto Camil 1kg", "Paulistão Supermercados", 9.99, None, False),
                ("Açúcar Cristal União 1kg", "Savegnago Supermercados", 3.49, None, False),
                ("Óleo de Soja Liza 900ml", "Carrefour Ribeirão", 5.79, 6.29, True),
                ("Café Torrado Melitta 500g", "Dalben Supermercados", 12.90, None, False),
                ("Sabão em Pó Omo 1.6kg", "Extra Hiper Ribeirão", 18.90, 21.90, True),
                ("Shampoo Pantene 400ml", "Paulistão Supermercados", 14.90, None, False),
            ]
            for prod_name, mkt_name, price_val, orig_price, is_promo in prices_data:
                p = product_map.get(prod_name)
                m = market_map.get(mkt_name)
                if p and m:
                    session.add(Price(
                        id=uuid.uuid4(), product_id=p.id, market_id=m.id,
                        price=price_val, original_price=orig_price,
                        is_promotion=is_promo, source="manual",
                        captured_at=now, created_by=admin.id,
                        created_at=now, updated_at=now,
                    ))

    print("Seed completo!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())