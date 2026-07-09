"""Seed sample data for PreçoPerto local testing."""
from app.models.base import Base
from app.core.database import engine
from app.models.product import Product
from app.models.market import Market
from app.models.price import Price
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from datetime import datetime

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Seed products
products_data = [
    {'name': 'Arroz Tio João 5kg', 'brand': 'Tio João', 'barcode': '7891000012345'},
    {'name': 'Feijão Carioca Camil 1kg', 'brand': 'Camil', 'barcode': '7891000023456'},
    {'name': 'Leite Integral Italac 1L', 'brand': 'Italac', 'barcode': '7891000034567'},
    {'name': 'Óleo de Soja Liza 900ml', 'brand': 'Liza', 'barcode': '7891000045678'},
    {'name': 'Café Pilão 500g', 'brand': 'Pilão', 'barcode': '7891000056789'},
    {'name': 'Açúcar União 5kg', 'brand': 'União', 'barcode': '7891000067890'},
    {'name': 'Coca-Cola 2L', 'brand': 'Coca-Cola', 'barcode': '7891000078901'},
    {'name': 'Pão de Forma Pullman 400g', 'brand': 'Pullman', 'barcode': '7891000089012'},
    {'name': 'Margarina Qualy 500g', 'brand': 'Qualy', 'barcode': '7891000090123'},
    {'name': 'Detergente Ypê 500ml', 'brand': 'Ypê', 'barcode': '7891000101234'},
]

products = {}
for p in products_data:
    prod = Product(**p)
    db.add(prod)
    db.flush()
    products[p['name']] = prod

# Seed markets
markets_data = [
    {'name': 'Supermercado BH', 'address': 'Rua XV de Novembro, 150', 'latitude': -19.9280, 'longitude': -43.9390},
    {'name': 'Extra Hiper', 'address': 'Av. Amazonas, 3500', 'latitude': -19.9300, 'longitude': -43.9350},
    {'name': 'Carrefour Bairro', 'address': 'Rua da Bahia, 800', 'latitude': -19.9320, 'longitude': -43.9420},
    {'name': 'Araxá Supermercados', 'address': 'Rua Rio de Janeiro, 1200', 'latitude': -19.9260, 'longitude': -43.9370},
]

markets = {}
for m in markets_data:
    market = Market(**m)
    db.add(market)
    db.flush()
    markets[m['name']] = market

# Seed prices
prices_data = [
    ('Arroz Tio João 5kg', 'Supermercado BH', 28.90),
    ('Arroz Tio João 5kg', 'Extra Hiper', 26.50),
    ('Arroz Tio João 5kg', 'Carrefour Bairro', 29.90),
    ('Feijão Carioca Camil 1kg', 'Supermercado BH', 8.90),
    ('Feijão Carioca Camil 1kg', 'Extra Hiper', 7.50),
    ('Feijão Carioca Camil 1kg', 'Araxá Supermercados', 8.45),
    ('Leite Integral Italac 1L', 'Supermercado BH', 5.49),
    ('Leite Integral Italac 1L', 'Extra Hiper', 4.99),
    ('Leite Integral Italac 1L', 'Carrefour Bairro', 5.29),
    ('Óleo de Soja Liza 900ml', 'Extra Hiper', 6.99),
    ('Óleo de Soja Liza 900ml', 'Supermercado BH', 7.49),
    ('Óleo de Soja Liza 900ml', 'Araxá Supermercados', 6.79),
    ('Café Pilão 500g', 'Supermercado BH', 18.90),
    ('Café Pilão 500g', 'Carrefour Bairro', 17.50),
    ('Café Pilão 500g', 'Extra Hiper', 16.90),
    ('Coca-Cola 2L', 'Extra Hiper', 8.99),
    ('Coca-Cola 2L', 'Supermercado BH', 9.49),
    ('Coca-Cola 2L', 'Araxá Supermercados', 8.79),
    ('Detergente Ypê 500ml', 'Supermercado BH', 2.89),
    ('Detergente Ypê 500ml', 'Extra Hiper', 2.49),
]

for prod_name, market_name, value in prices_data:
    price = Price(
        product_id=products[prod_name].id,
        market_id=markets[market_name].id,
        price=value,
    )
    db.add(price)

db.commit()
db.close()
print('✅ Seed concluído!')
print(f'   Produtos: {len(products_data)}')
print(f'   Mercados: {len(markets_data)}')
print(f'   Preços: {len(prices_data)}')
