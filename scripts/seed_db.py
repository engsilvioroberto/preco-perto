import sys
import os

# Adiciona o diretório backend ao path para importar os modelos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.models.base import SessionLocal, Product, Market, Price
from datetime import datetime

def seed_data():
    db = SessionLocal()
    
    # 1. Criar Mercados
    markets = [
        Market(name="Supermercado Silva", address="Rua Ribeirão, 100", latitude=-21.17, longitude=-47.81),
        Market(name="Atacado do Povo", address="Av. Saudade, 500", latitude=-21.18, longitude=-47.80)
    ]
    db.add_all(markets)
    db.commit()
    
    # 2. Criar Produtos
    products = [
        Product(name="Leite Integral Parmalat", brand="Parmalat", barcode="7891234567890"),
        Product(name="Arroz Tio João 5kg", brand="Tio João", barcode="7891234567891"),
        Product(name="Feijão Carioca Kicaldo", brand="Kicaldo", barcode="7891234567892"),
        Product(name="Coca-Cola 2L", brand="Coca-Cola", barcode="7891234567893")
    ]
    db.add_all(products)
    db.commit()
    
    # 3. Criar Preços
    prices = [
        Price(product_id=1, market_id=1, price=5.49),
        Price(product_id=1, market_id=2, price=5.29),
        Price(product_id=2, market_id=1, price=24.90),
        Price(product_id=3, market_id=2, price=7.50)
    ]
    db.add_all(prices)
    db.commit()
    
    db.close()
    print("Dados inseridos com sucesso!")

if __name__ == "__main__":
    seed_data()
