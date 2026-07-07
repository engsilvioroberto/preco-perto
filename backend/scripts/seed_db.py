import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import Base, AsyncSessionLocal
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

# Import all models to register them
from app.models.user import User
from app.models.market import Market
from app.models.product import Product
from app.models.price import Price
from app.models.receipt import Receipt
from app.models.offer_flyer import OfferFlyer
from app.models.offer_flyer_item import OfferFlyerItem
from app.core.security import get_password_hash
from app.services.product_normalization import normalize_product

async def seed_data():
    engine = create_async_engine(settings.DATABASE_URL)
    
    # 1. Create tables
    async with engine.begin() as conn:
        print("Creating database tables...")
        await conn.run_sync(Base.metadata.drop_all) # Clear if exists
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")

    async with AsyncSessionLocal() as session:
        async with session.begin():
            # 2. Create users
            print("Creating users...")
            admin = User(
                id=uuid.uuid4(),
                email="admin@precoperto.com",
                name="Admin PreçoPerto",
                password_hash=get_password_hash("admin123"),
                is_admin=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            user = User(
                id=uuid.uuid4(),
                email="joao@gmail.com",
                name="João Silva",
                password_hash=get_password_hash("joao123"),
                is_admin=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add_all([admin, user])
            
            # 3. Create markets
            print("Creating markets...")
            markets = [
                Market(
                    id=uuid.uuid4(),
                    name='Carrefour Ribeirão',
                    cnpj='45.543.915/0001-81',
                    address='Av. Presidente Vargas, 2001',
                    neighborhood='Centro',
                    city='Ribeirão Preto',
                    state='SP',
                    zipcode='14015-510',
                    latitude=-21.1767,
                    longitude=-47.8208,
                    categories=['supermercado', 'atacado'],
                    phone='(16) 3977-1000',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                Market(
                    id=uuid.uuid4(),
                    name='Extra Hiper Ribeirão',
                    cnpj='33.014.556/0001-96',
                    address='Av. Wladimir Meirelles Ferreira, 2500',
                    neighborhood='Jardim Botânico',
                    city='Ribeirão Preto',
                    state='SP',
                    zipcode='14024-100',
                    latitude=-21.1900,
                    longitude=-47.8100,
                    categories=['supermercado'],
                    phone='(16) 3603-2000',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                Market(
                    id=uuid.uuid4(),
                    name='Dalben Supermercados',
                    cnpj='07.545.678/0001-90',
                    address='Rua General Osório, 1500',
                    neighborhood='Campos Elíseos',
                    city='Ribeirão Preto',
                    state='SP',
                    zipcode='14085-010',
                    latitude=-21.1850,
                    longitude=-47.8250,
                    categories=['supermercado'],
                    phone='(16) 3610-3000',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                Market(
                    id=uuid.uuid4(),
                    name='Savegnago Supermercados',
                    cnpj='51.890.123/0001-45',
                    address='Av. Costabile Romano, 1000',
                    neighborhood='Quintino Facci I',
                    city='Ribeirão Preto',
                    state='SP',
                    zipcode='14070-100',
                    latitude=-21.2000,
                    longitude=-47.8300,
                    categories=['supermercado'],
                    phone='(16) 3916-4000',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                Market(
                    id=uuid.uuid4(),
                    name='Paulistão Supermercados',
                    cnpj='52.345.678/0001-12',
                    address='Av. Presidente Vargas, 3500',
                    neighborhood='Ipiranga',
                    city='Ribeirão Preto',
                    state='SP',
                    zipcode='14015-510',
                    latitude=-21.1800,
                    longitude=-47.8150,
                    categories=['supermercado'],
                    phone='(16) 3620-5000',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            ]
            session.add_all(markets)

            # 4. Create products
            print("Creating products...")
            products_data = [
                ('Leite Integral Piracanjuba 1L', 'laticínios', 'L', 1.0, 'Piracanjuba'),
                ('Leite Desnatado Piracanjuba 1L', 'laticínios', 'L', 1.0, 'Piracanjuba'),
                ('Arroz Branco Tio João 5kg', 'grãos', 'kg', 5.0, 'Tio João'),
                ('Feijão Preto Camil 1kg', 'grãos', 'kg', 1.0, 'Camil'),
                ('Açúcar Cristal União 1kg', 'adoçantes', 'kg', 1.0, 'União'),
                ('Óleo de Soja Liza 900ml', 'óleos', 'ml', 900.0, 'Liza'),
                ('Café Torrado Melitta Tradicional 500g', 'bebidas', 'g', 500.0, 'Melitta'),
                ('Sabão em Pó Omo 1.6kg', 'limpeza', 'kg', 1.6, 'Omo'),
                ('Shampoo Pantene 400ml', 'higiene', 'ml', 400.0, 'Pantene'),
                ('Papel Higiênico Personal 12 Rolos', 'higiene', 'un', 12.0, 'Personal'),
            ]
            
            products = []
            for name, category, unit, qty, brand in products_data:
                normalized = normalize_product(name)
                p = Product(
                    id=uuid.uuid4(),
                    name=name,
                    normalized_name=normalized,
                    category=category,
                    unit=unit,
                    quantity=qty,
                    brand=brand,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                products.append(p)
            session.add_all(products)
            
            # Flush to get objects registered
            await session.flush()
            
            # Map products and markets for price seeding
            market_map = {m.name: m for m in markets}
            product_map = {p.name: p for p in products}
            
            # 5. Create prices
            print("Creating prices...")
            prices_data = [
                ('Leite Integral Piracanjuba 1L', 'Carrefour Ribeirão', 4.99, 5.49, True),
                ('Leite Integral Piracanjuba 1L', 'Extra Hiper Ribeirão', 5.29, None, False),
                ('Leite Integral Piracanjuba 1L', 'Dalben Supermercados', 5.49, None, False),
                ('Leite Integral Piracanjuba 1L', 'Savegnago Supermercados', 5.99, None, False),
                ('Leite Integral Piracanjuba 1L', 'Paulistão Supermercados', 6.49, None, False),
                
                ('Arroz Branco Tio João 5kg', 'Carrefour Ribeirão', 22.90, 25.90, True),
                ('Arroz Branco Tio João 5kg', 'Extra Hiper Ribeirão', 24.50, None, False),
                ('Arroz Branco Tio João 5kg', 'Dalben Supermercados', 25.90, None, False),
                ('Arroz Branco Tio João 5kg', 'Savegnago Supermercados', 26.90, None, False),
                ('Arroz Branco Tio João 5kg', 'Paulistão Supermercados', 27.90, None, False),
                
                ('Feijão Preto Camil 1kg', 'Carrefour Ribeirão', 7.99, 8.99, True),
                ('Feijão Preto Camil 1kg', 'Extra Hiper Ribeirão', 8.49, None, False),
                ('Feijão Preto Camil 1kg', 'Dalben Supermercados', 8.99, None, False),
                ('Feijão Preto Camil 1kg', 'Savegnago Supermercados', 9.49, None, False),
                ('Feijão Preto Camil 1kg', 'Paulistão Supermercados', 9.99, None, False),
            ]
            
            for prod_name, mkt_name, price_val, orig_price, is_promo in prices_data:
                p = product_map.get(prod_name)
                m = market_map.get(mkt_name)
                if p and m:
                    pr = Price(
                        id=uuid.uuid4(),
                        product_id=p.id,
                        market_id=m.id,
                        price=price_val,
                        original_price=orig_price,
                        is_promotion=is_promo,
                        source="manual",
                        captured_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=7),
                        created_by=admin.id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(pr)
                    
    print("Database setup and seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_data())
