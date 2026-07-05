#!/usr/bin/env python3
"""
Script para criar e popular banco SQLite local com dados de exemplo.
Usado para desenvolvimento e testes antes de migrar para Supabase.
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'backend' / 'precoperto.db'

def create_tables(conn):
    """Criar todas as tabelas no SQLite"""
    cursor = conn.cursor()
    
    # Tabela users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela markets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS markets (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            neighborhood TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            opening_hours TEXT,
            categories TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela products
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            normalized_name TEXT NOT NULL,
            category TEXT,
            unit TEXT,
            quantity REAL,
            brand TEXT,
            image_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela prices
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            market_id TEXT NOT NULL,
            price REAL NOT NULL,
            original_price REAL,
            is_promotion INTEGER DEFAULT 0,
            promotion_ends_at TEXT,
            source TEXT NOT NULL,
            source_id TEXT,
            captured_at TEXT NOT NULL,
            expires_at TEXT,
            created_by TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (market_id) REFERENCES markets(id)
        )
    """)
    
    # Tabela receipts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            market_id TEXT,
            image_url TEXT NOT NULL,
            ocr_text TEXT,
            cnpj_extracted TEXT,
            total_value REAL,
            receipt_date TEXT,
            status TEXT DEFAULT 'pending',
            user_latitude REAL,
            user_longitude REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Tabela receipt_items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipt_items (
            id TEXT PRIMARY KEY,
            receipt_id TEXT NOT NULL,
            product_id TEXT,
            description TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            confidence REAL,
            is_confirmed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (receipt_id) REFERENCES receipts(id)
        )
    """)
    
    # Índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_normalized_name ON products(normalized_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_product_id ON prices(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_market_id ON prices(market_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_captured_at ON prices(captured_at)")
    
    conn.commit()
    print("✅ Tabelas criadas")

def seed_data(conn):
    """Popular com dados de exemplo"""
    cursor = conn.cursor()
    
    # Mercados reais de Ribeirão Preto
    markets = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Carrefour Ribeirão',
            'address': 'Av. Presidente Vargas, 2001',
            'neighborhood': 'Centro',
            'latitude': -21.1767,
            'longitude': -47.8208,
            'opening_hours': '{"monday": {"open": "08:00", "close": "22:00"}, "tuesday": {"open": "08:00", "close": "22:00"}}',
            'categories': '["supermercado", "atacado"]'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Extra Hiper Ribeirão',
            'address': 'Av. Wladimir Meirelles Ferreira, 2500',
            'neighborhood': 'Jardim Botânico',
            'latitude': -21.1900,
            'longitude': -47.8100,
            'opening_hours': '{"monday": {"open": "07:00", "close": "23:00"}}',
            'categories': '["supermercado"]'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Dalben Supermercados',
            'address': 'Rua General Osório, 1500',
            'neighborhood': 'Campos Elíseos',
            'latitude': -21.1850,
            'longitude': -47.8250,
            'opening_hours': '{"monday": {"open": "08:00", "close": "22:00"}}',
            'categories': '["supermercado"]'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Savegnago Supermercados',
            'address': 'Av. Costabile Romano, 1000',
            'neighborhood': 'Quintino Facci I',
            'latitude': -21.2000,
            'longitude': -47.8300,
            'opening_hours': '{"monday": {"open": "08:00", "close": "22:00"}}',
            'categories': '["supermercado"]'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Paulistão Supermercados',
            'address': 'Av. Presidente Vargas, 3500',
            'neighborhood': 'Ipiranga',
            'latitude': -21.1800,
            'longitude': -47.8150,
            'opening_hours': '{"monday": {"open": "07:00", "close": "22:00"}}',
            'categories': '["supermercado"]'
        }
    ]
    
    print(f"Inserindo {len(markets)} mercados...")
    for market in markets:
        cursor.execute("""
            INSERT OR REPLACE INTO markets 
            (id, name, address, neighborhood, latitude, longitude, opening_hours, categories)
            VALUES (:id, :name, :address, :neighborhood, :latitude, :longitude, :opening_hours, :categories)
        """, market)
    
    # Produtos comuns
    products = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Leite Integral Piracanjuba 1L',
            'normalized_name': 'leite integral piracanjuba 1l',
            'category': 'laticínios',
            'unit': 'L',
            'quantity': 1.0,
            'brand': 'Piracanjuba'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Leite Desnatado Piracanjuba 1L',
            'normalized_name': 'leite desnatado piracanjuba 1l',
            'category': 'laticínios',
            'unit': 'L',
            'quantity': 1.0,
            'brand': 'Piracanjuba'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Arroz Branco Tio João 5kg',
            'normalized_name': 'arroz branco tio joao 5kg',
            'category': 'grãos',
            'unit': 'kg',
            'quantity': 5.0,
            'brand': 'Tio João'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Feijão Preto Camil 1kg',
            'normalized_name': 'feijao preto camil 1kg',
            'category': 'grãos',
            'unit': 'kg',
            'quantity': 1.0,
            'brand': 'Camil'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Açúcar Cristal União 1kg',
            'normalized_name': 'acucar cristal uniao 1kg',
            'category': 'adoçantes',
            'unit': 'kg',
            'quantity': 1.0,
            'brand': 'União'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Óleo de Soja Liza 900ml',
            'normalized_name': 'oleo soja liza 900ml',
            'category': 'óleos',
            'unit': 'ml',
            'quantity': 900.0,
            'brand': 'Liza'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Café Melitta Tradicional 500g',
            'normalized_name': 'cafe melitta tradicional 500g',
            'category': 'bebidas',
            'unit': 'g',
            'quantity': 500.0,
            'brand': 'Melitta'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Sabão em Pó Omo 1.6kg',
            'normalized_name': 'sabao po omo 1.6kg',
            'category': 'limpeza',
            'unit': 'kg',
            'quantity': 1.6,
            'brand': 'Omo'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Shampoo Pantene Restauração 400ml',
            'normalized_name': 'shampoo pantene restauracao 400ml',
            'category': 'higiene',
            'unit': 'ml',
            'quantity': 400.0,
            'brand': 'Pantene'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Papel Higiênico Personal Vip 30m 12 Rolos',
            'normalized_name': 'papel higienico personal vip 30m 12 rolos',
            'category': 'higiene',
            'unit': 'un',
            'quantity': 12.0,
            'brand': 'Personal'
        }
    ]
    
    print(f"Inserindo {len(products)} produtos...")
    for product in products:
        cursor.execute("""
            INSERT OR REPLACE INTO products 
            (id, name, normalized_name, category, unit, quantity, brand)
            VALUES (:id, :name, :normalized_name, :category, :unit, :quantity, :brand)
        """, product)
    
    # Preços para cada produto em cada mercado
    prices_data = [
        # Leite Integral
        ('Leite Integral Piracanjuba 1L', 'Carrefour Ribeirão', 4.99, 5.49, True),
        ('Leite Integral Piracanjuba 1L', 'Extra Hiper Ribeirão', 5.29, None, False),
        ('Leite Integral Piracanjuba 1L', 'Dalben Supermercados', 5.49, None, False),
        ('Leite Integral Piracanjuba 1L', 'Savegnago Supermercados', 5.99, None, False),
        ('Leite Integral Piracanjuba 1L', 'Paulistão Supermercados', 6.49, None, False),
        
        # Arroz
        ('Arroz Branco Tio João 5kg', 'Carrefour Ribeirão', 22.90, 25.90, True),
        ('Arroz Branco Tio João 5kg', 'Extra Hiper Ribeirão', 24.50, None, False),
        ('Arroz Branco Tio João 5kg', 'Dalben Supermercados', 25.90, None, False),
        ('Arroz Branco Tio João 5kg', 'Savegnago Supermercados', 26.90, None, False),
        ('Arroz Branco Tio João 5kg', 'Paulistão Supermercados', 27.90, None, False),
        
        # Feijão
        ('Feijão Preto Camil 1kg', 'Carrefour Ribeirão', 7.99, 8.99, True),
        ('Feijão Preto Camil 1kg', 'Extra Hiper Ribeirão', 8.49, None, False),
        ('Feijão Preto Camil 1kg', 'Dalben Supermercados', 8.99, None, False),
        ('Feijão Preto Camil 1kg', 'Savegnago Supermercados', 9.49, None, False),
        ('Feijão Preto Camil 1kg', 'Paulistão Supermercados', 9.99, None, False),
        
        # Açúcar
        ('Açúcar Cristal União 1kg', 'Carrefour Ribeirão', 4.49, None, False),
        ('Açúcar Cristal União 1kg', 'Extra Hiper Ribeirão', 4.79, None, False),
        ('Açúcar Cristal União 1kg', 'Dalben Supermercados', 4.99, None, False),
        ('Açúcar Cristal União 1kg', 'Savegnago Supermercados', 5.29, None, False),
        ('Açúcar Cristal União 1kg', 'Paulistão Supermercados', 5.49, None, False),
        
        # Óleo
        ('Óleo de Soja Liza 900ml', 'Carrefour Ribeirão', 6.99, 7.99, True),
        ('Óleo de Soja Liza 900ml', 'Extra Hiper Ribeirão', 7.29, None, False),
        ('Óleo de Soja Liza 900ml', 'Dalben Supermercados', 7.49, None, False),
        ('Óleo de Soja Liza 900ml', 'Savegnago Supermercados', 7.99, None, False),
        ('Óleo de Soja Liza 900ml', 'Paulistão Supermercados', 8.29, None, False),
    ]
    
    print(f"Inserindo {len(prices_data)} preços...")
    captured_at = datetime.now().isoformat()
    
    for product_name, market_name, price, original_price, is_promotion in prices_data:
        # Buscar IDs
        cursor.execute("SELECT id FROM products WHERE name = ?", (product_name,))
        product_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM markets WHERE name = ?", (market_name,))
        market_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO prices 
            (id, product_id, market_id, price, original_price, is_promotion, source, captured_at)
            VALUES (?, ?, ?, ?, ?, ?, 'seed', ?)
        """, (
            str(uuid.uuid4()),
            product_id,
            market_id,
            price,
            original_price,
            1 if is_promotion else 0,
            captured_at
        ))
    
    conn.commit()
    print(f"✅ {len(markets)} mercados, {len(products)} produtos, {len(prices_data)} preços inseridos")

def main():
    print("🚀 Criando banco SQLite local...")
    
    # Remover banco antigo se existir
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("Banco antigo removido")
    
    # Criar conexão
    conn = sqlite3.connect(DB_PATH)
    
    try:
        create_tables(conn)
        seed_data(conn)
        print("\n🎉 Banco SQLite criado com sucesso!")
        print(f"📍 Localização: {DB_PATH}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
