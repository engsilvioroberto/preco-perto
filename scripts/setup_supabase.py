#!/usr/bin/env python3
"""
Script para criar tabelas no Supabase e popular dados iniciais.
"""

import os
import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_tables():
    """Criar todas as tabelas no Supabase"""
    
    # Converter URL async para sync
    db_url = settings.DATABASE_URL.replace('+asyncpg', '')
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("Criando tabelas...")
        
        # Tabela users
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        
        # Tabela markets
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS markets (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                address TEXT NOT NULL,
                neighborhood VARCHAR(255),
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                opening_hours JSONB,
                categories TEXT[],
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        
        # Tabela products
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                normalized_name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                unit VARCHAR(50),
                quantity DECIMAL(10, 3),
                brand VARCHAR(255),
                image_url TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        
        # Tabela prices
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS prices (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                market_id UUID NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
                price DECIMAL(10, 2) NOT NULL,
                original_price DECIMAL(10, 2),
                is_promotion BOOLEAN DEFAULT FALSE,
                promotion_ends_at DATE,
                source VARCHAR(50) NOT NULL,
                source_id UUID,
                captured_at TIMESTAMP WITH TIME ZONE NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE,
                created_by UUID REFERENCES users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        
        # Tabela receipts
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS receipts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                market_id UUID REFERENCES markets(id),
                image_url TEXT NOT NULL,
                ocr_text TEXT,
                cnpj_extracted VARCHAR(18),
                total_value DECIMAL(10, 2),
                receipt_date TIMESTAMP WITH TIME ZONE,
                status VARCHAR(50) DEFAULT 'pending',
                user_latitude DECIMAL(10, 8),
                user_longitude DECIMAL(11, 8),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        
        # Tabela receipt_items
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS receipt_items (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                receipt_id UUID NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
                product_id UUID REFERENCES products(id),
                description TEXT NOT NULL,
                quantity DECIMAL(10, 3) NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                confidence DECIMAL(5, 2),
                is_confirmed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        
        # Criar índices
        print("Criando índices...")
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_products_normalized_name ON products(normalized_name)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_prices_product_id ON prices(product_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_prices_market_id ON prices(market_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_prices_captured_at ON prices(captured_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_receipts_user_id ON receipts(user_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_receipt_items_receipt_id ON receipt_items(receipt_id)"))
        
        conn.commit()
        print("✅ Tabelas criadas com sucesso!")

def seed_data():
    """Popular dados iniciais"""
    
    db_url = settings.DATABASE_URL.replace('+asyncpg', '')
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("\nPopulando dados iniciais...")
        
        # Mercados de Ribeirão Preto
        markets = [
            ('Carrefour Ribeirão', 'Av. Presidente Vargas, 2001', 'Centro', -21.1767, -47.8208),
            ('Extra Hiper', 'Av. Wladimir Meirelles Ferreira, 2500', 'Jardim Botânico', -21.1900, -47.8100),
            ('Dalben Supermercados', 'Rua General Osório, 1500', 'Campos Elíseos', -21.1850, -47.8250),
            ('Savegnago Supermercados', 'Av. Costabile Romano, 1000', 'Quintino Facci I', -21.2000, -47.8300),
            ('Paulistão Supermercados', 'Av. Presidente Vargas, 3500', 'Ipiranga', -21.1800, -47.8150),
        ]
        
        print(f"Inserindo {len(markets)} mercados...")
        for name, address, neighborhood, lat, lng in markets:
            conn.execute(text("""
                INSERT INTO markets (name, address, neighborhood, latitude, longitude)
                VALUES (:name, :address, :neighborhood, :lat, :lng)
                ON CONFLICT DO NOTHING
            """), {
                'name': name,
                'address': address,
                'neighborhood': neighborhood,
                'lat': lat,
                'lng': lng
            })
        
        # Produtos comuns
        products = [
            ('Leite Integral Piracanjuba 1L', 'leite integral piracanjuba 1l', 'laticínios', 'L', 1.0, 'Piracanjuba'),
            ('Leite Desnatado Piracanjuba 1L', 'leite desnatado piracanjuba 1l', 'laticínios', 'L', 1.0, 'Piracanjuba'),
            ('Arroz Branco Tio João 5kg', 'arroz branco tio joao 5kg', 'grãos', 'kg', 5.0, 'Tio João'),
            ('Feijão Preto Camil 1kg', 'feijao preto camil 1kg', 'grãos', 'kg', 1.0, 'Camil'),
            ('Açúcar Cristal União 1kg', 'acucar cristal uniao 1kg', 'adoçantes', 'kg', 1.0, 'União'),
            ('Óleo de Soja Liza 900ml', 'oleo soja liza 900ml', 'óleos', 'ml', 900.0, 'Liza'),
            ('Café Melitta Tradicional 500g', 'cafe melitta tradicional 500g', 'bebidas', 'g', 500.0, 'Melitta'),
            ('Sabão em Pó Omo 1.6kg', 'sabao po omo 1.6kg', 'limpeza', 'kg', 1.6, 'Omo'),
            ('Shampoo Pantene 400ml', 'shampoo pantene 400ml', 'higiene', 'ml', 400.0, 'Pantene'),
            ('Papel Higiênico Personal 12 Rolos', 'papel higienico personal 12 rolos', 'higiene', 'un', 12.0, 'Personal'),
        ]
        
        print(f"Inserindo {len(products)} produtos...")
        for name, normalized, category, unit, quantity, brand in products:
            conn.execute(text("""
                INSERT INTO products (name, normalized_name, category, unit, quantity, brand)
                VALUES (:name, :normalized, :category, :unit, :quantity, :brand)
                ON CONFLICT DO NOTHING
            """), {
                'name': name,
                'normalized': normalized,
                'category': category,
                'unit': unit,
                'quantity': quantity,
                'brand': brand
            })
        
        conn.commit()
        print("✅ Dados iniciais inseridos!")
        
        # Buscar IDs para criar preços
        print("\nCriando preços de exemplo...")
        
        # Buscar IDs dos mercados
        markets_result = conn.execute(text("SELECT id, name FROM markets")).fetchall()
        market_ids = {name: id for id, name in markets_result}
        
        # Buscar IDs dos produtos
        products_result = conn.execute(text("SELECT id, name FROM products")).fetchall()
        product_ids = {name: id for id, name in products_result}
        
        # Criar preços para cada produto em cada mercado
        prices_data = [
            ('Leite Integral Piracanjuba 1L', 'Carrefour Ribeirão', 4.99, 5.49, True),
            ('Leite Integral Piracanjuba 1L', 'Extra Hiper', 5.29, None, False),
            ('Leite Integral Piracanjuba 1L', 'Dalben Supermercados', 5.49, None, False),
            ('Leite Integral Piracanjuba 1L', 'Savegnago Supermercados', 5.99, None, False),
            ('Leite Integral Piracanjuba 1L', 'Paulistão Supermercados', 6.49, None, False),
            
            ('Arroz Branco Tio João 5kg', 'Carrefour Ribeirão', 22.90, 25.90, True),
            ('Arroz Branco Tio João 5kg', 'Extra Hiper', 24.50, None, False),
            ('Arroz Branco Tio João 5kg', 'Dalben Supermercados', 25.90, None, False),
            ('Arroz Branco Tio João 5kg', 'Savegnago Supermercados', 26.90, None, False),
            ('Arroz Branco Tio João 5kg', 'Paulistão Supermercados', 27.90, None, False),
            
            ('Feijão Preto Camil 1kg', 'Carrefour Ribeirão', 7.99, 8.99, True),
            ('Feijão Preto Camil 1kg', 'Extra Hiper', 8.49, None, False),
            ('Feijão Preto Camil 1kg', 'Dalben Supermercados', 8.99, None, False),
            ('Feijão Preto Camil 1kg', 'Savegnago Supermercados', 9.49, None, False),
            ('Feijão Preto Camil 1kg', 'Paulistão Supermercados', 9.99, None, False),
        ]
        
        for product_name, market_name, price, original_price, is_promotion in prices_data:
            if product_name in product_ids and market_name in market_ids:
                conn.execute(text("""
                    INSERT INTO prices (product_id, market_id, price, original_price, is_promotion, source, captured_at)
                    VALUES (:product_id, :market_id, :price, :original_price, :is_promotion, 'seed', NOW())
                """), {
                    'product_id': product_ids[product_name],
                    'market_id': market_ids[market_name],
                    'price': price,
                    'original_price': original_price,
                    'is_promotion': is_promotion
                })
        
        conn.commit()
        print(f"✅ {len(prices_data)} preços criados!")

if __name__ == '__main__':
    try:
        create_tables()
        seed_data()
        print("\n🎉 Setup do banco concluído!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
