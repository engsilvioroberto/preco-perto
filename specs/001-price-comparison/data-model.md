# Data Model — PreçoPerto MVP

**Versão**: 1.0  
**Data**: 2026-07-04  
**Database**: Supabase (PostgreSQL 15 + PostGIS)

---

## Schema Overview

```sql
-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabelas principais
-- 1. users (autenticação)
-- 2. markets (mercados com geolocalização)
-- 3. products (produtos normalizados)
-- 4. prices (preços por produto/mercado)
-- 5. receipts (notas fiscais escaneadas)
-- 6. receipt_items (itens da nota fiscal)
-- 7. offer_flyers (jornais de ofertas)
-- 8. offer_flyer_items (itens do jornal)
```

---

## Tabela: users

**Descrição**: Usuários do sistema (consumidores e admins)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Índices
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_admin ON users(is_admin);
```

**Campos**:
- `id`: UUID único do usuário
- `email`: Email único (login)
- `password_hash`: Senha hasheada (bcrypt)
- `name`: Nome do usuário
- `is_admin`: Flag para admins (podem cadastrar mercados, upload jornais)
- `created_at`: Data de cadastro
- `updated_at`: Última atualização
- `last_login`: Último login

---

## Tabela: markets

**Descrição**: Mercados/supermercados com geolocalização

```sql
CREATE TABLE markets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18), -- Formato: 00.000.000/0000-00
    address TEXT NOT NULL,
    neighborhood VARCHAR(255),
    city VARCHAR(255) DEFAULT 'Ribeirão Preto',
    state VARCHAR(2) DEFAULT 'SP',
    zipcode VARCHAR(10),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    location GEOGRAPHY(POINT, 4326), -- PostGIS
    opening_hours JSONB, -- {"monday": {"open": "08:00", "close": "22:00"}, ...}
    categories TEXT[], -- ["supermercado", "atacado", "hortifruti"]
    phone VARCHAR(20),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_markets_location ON markets USING GIST(location);
CREATE INDEX idx_markets_city ON markets(city);
CREATE INDEX idx_markets_neighborhood ON markets(neighborhood);
CREATE INDEX idx_markets_cnpj ON markets(cnpj);

-- Trigger para atualizar location a partir de lat/lng
CREATE OR REPLACE FUNCTION update_market_location()
RETURNS TRIGGER AS $$
BEGIN
    NEW.location := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_market_location
BEFORE INSERT OR UPDATE ON markets
FOR EACH ROW
EXECUTE FUNCTION update_market_location();
```

**Campos**:
- `id`: UUID único do mercado
- `name`: Nome do mercado
- `cnpj`: CNPJ (opcional, para extração de notas fiscais)
- `address`: Endereço completo
- `neighborhood`: Bairro
- `city`: Cidade (default: Ribeirão Preto)
- `state`: Estado (default: SP)
- `zipcode`: CEP
- `latitude`: Latitude (WGS84)
- `longitude`: Longitude (WGS84)
- `location`: PostGIS geography point (para cálculos de distância)
- `opening_hours`: JSON com horários de funcionamento
- `categories`: Array de categorias
- `phone`: Telefone de contato
- `created_by`: Usuário que cadastrou (admin)

---

## Tabela: products

**Descrição**: Produtos normalizados (catálogo)

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255) NOT NULL, -- Nome normalizado (lowercase, sem acentos)
    category VARCHAR(100), -- "laticínios", "higiene", "limpeza", etc
    unit VARCHAR(50), -- "kg", "L", "un", "g", "ml"
    quantity DECIMAL(10, 3), -- Quantidade (1.0 kg, 2.0 L, etc)
    brand VARCHAR(255), -- Marca (opcional)
    barcode VARCHAR(50), -- Código de barras (EAN-13, opcional)
    image_url TEXT, -- URL da imagem do produto
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(normalized_name, brand, unit, quantity)
);

-- Índices
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_normalized_name ON products(normalized_name);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_barcode ON products(barcode);

-- Full-text search
CREATE INDEX idx_products_name_search ON products USING GIN(to_tsvector('portuguese', name));
```

**Campos**:
- `id`: UUID único do produto
- `name`: Nome original do produto
- `normalized_name`: Nome normalizado (para comparação)
- `category`: Categoria do produto
- `unit`: Unidade de medida
- `quantity`: Quantidade (ex: 1.0 kg, 2.0 L)
- `brand`: Marca (opcional)
- `barcode`: Código de barras (opcional)
- `image_url`: URL da imagem
- **UNIQUE constraint**: Evita duplicatas (mesmo produto normalizado)

---

## Tabela: prices

**Descrição**: Preços de produtos por mercado (tabela principal de comparação)

```sql
CREATE TABLE prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    market_id UUID NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL, -- Preço em R$
    original_price DECIMAL(10, 2), -- Preço original (se em promoção)
    is_promotion BOOLEAN DEFAULT FALSE,
    promotion_ends_at DATE, -- Data de validade da promoção
    source VARCHAR(50) NOT NULL, -- "oferta_flyer", "receipt", "manual"
    source_id UUID, -- ID do receipt ou offer_flyer de origem
    captured_at TIMESTAMP WITH TIME ZONE NOT NULL, -- Quando o preço foi capturado
    expires_at TIMESTAMP WITH TIME ZONE, -- Quando o preço expira (ofertas)
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, market_id, captured_at) -- Evita duplicatas no mesmo timestamp
);

-- Índices
CREATE INDEX idx_prices_product ON prices(product_id);
CREATE INDEX idx_prices_market ON prices(market_id);
CREATE INDEX idx_prices_price ON prices(price);
CREATE INDEX idx_prices_captured_at ON prices(captured_at DESC);
CREATE INDEX idx_prices_source ON prices(source);
CREATE INDEX idx_prices_expires_at ON prices(expires_at);

-- Índice composto para busca rápida de preços por produto
CREATE INDEX idx_prices_product_date ON prices(product_id, captured_at DESC);

-- View para preços mais recentes por produto/mercado
CREATE OR REPLACE VIEW latest_prices AS
SELECT DISTINCT ON (product_id, market_id)
    product_id,
    market_id,
    price,
    original_price,
    is_promotion,
    promotion_ends_at,
    source,
    captured_at,
    expires_at
FROM prices
ORDER BY product_id, market_id, captured_at DESC;
```

**Campos**:
- `id`: UUID único do preço
- `product_id`: Produto (FK)
- `market_id`: Mercado (FK)
- `price`: Preço atual em R$
- `original_price`: Preço original (se em promoção)
- `is_promotion`: Flag de promoção
- `promotion_ends_at`: Data de validade da promoção
- `source`: Origem do preço ("oferta_flyer", "receipt", "manual")
- `source_id`: ID da fonte (receipt ou offer_flyer)
- `captured_at`: Quando o preço foi capturado
- `expires_at`: Quando expira (ofertas têm validade)
- `created_by`: Usuário que capturou
- **UNIQUE constraint**: Evita duplicatas no mesmo timestamp

---

## Tabela: receipts

**Descrição**: Notas fiscais escaneadas por usuários

```sql
CREATE TABLE receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    market_id UUID REFERENCES markets(id), -- Pode ser NULL se mercado não identificado
    image_url TEXT NOT NULL, -- URL da imagem no Supabase Storage
    ocr_text TEXT, -- Texto bruto extraído via OCR
    cnpj_extracted VARCHAR(18), -- CNPJ extraído da nota
    total_value DECIMAL(10, 2), -- Valor total da nota
    receipt_date TIMESTAMP WITH TIME ZONE, -- Data/hora da nota fiscal
    status VARCHAR(50) DEFAULT 'pending', -- "pending", "processing", "completed", "failed"
    user_location GEOGRAPHY(POINT, 4326), -- GPS do usuário ao escanear
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_receipts_user ON receipts(user_id);
CREATE INDEX idx_receipts_market ON receipts(market_id);
CREATE INDEX idx_receipts_status ON receipts(status);
CREATE INDEX idx_receipts_date ON receipts(receipt_date DESC);
CREATE INDEX idx_receipts_location ON receipts USING GIST(user_location);
```

**Campos**:
- `id`: UUID único da nota fiscal
- `user_id`: Usuário que escaneou
- `market_id`: Mercado identificado (pode ser NULL inicialmente)
- `image_url`: URL da imagem no Supabase Storage
- `ocr_text`: Texto bruto extraído via OCR
- `cnpj_extracted`: CNPJ extraído da nota
- `total_value`: Valor total da nota
- `receipt_date`: Data/hora da nota fiscal
- `status`: Status do processamento
- `user_location`: GPS do usuário ao escanear

---

## Tabela: receipt_items

**Descrição**: Itens extraídos de notas fiscais

```sql
CREATE TABLE receipt_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_id UUID NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id), -- NULL se produto não identificado
    description TEXT NOT NULL, -- Descrição original na nota
    quantity DECIMAL(10, 3) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    confidence DECIMAL(5, 2), -- Confiança do OCR (0-100%)
    is_confirmed BOOLEAN DEFAULT FALSE, -- Usuário confirmou/corrigiu
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_receipt_items_receipt ON receipt_items(receipt_id);
CREATE INDEX idx_receipt_items_product ON receipt_items(product_id);
CREATE INDEX idx_receipt_items_confidence ON receipt_items(confidence);
```

**Campos**:
- `id`: UUID único do item
- `receipt_id`: Nota fiscal (FK)
- `product_id`: Produto identificado (FK, pode ser NULL)
- `description`: Descrição original na nota
- `quantity`: Quantidade
- `unit_price`: Preço unitário
- `total_price`: Preço total (quantity × unit_price)
- `confidence`: Confiança do OCR (0-100%)
- `is_confirmed`: Usuário confirmou/corrigiu

---

## Tabela: offer_flyers

**Descrição**: Jornais de ofertas uploadados por admins

```sql
CREATE TABLE offer_flyers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    market_id UUID NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL, -- URL da imagem/PDF no Supabase Storage
    ocr_text TEXT, -- Texto bruto extraído via OCR
    valid_from DATE NOT NULL,
    valid_until DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- "pending", "processing", "completed", "failed"
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_offer_flyers_market ON offer_flyers(market_id);
CREATE INDEX idx_offer_flyers_valid ON offer_flyers(valid_from, valid_until);
CREATE INDEX idx_offer_flyers_status ON offer_flyers(status);
```

**Campos**:
- `id`: UUID único do jornal
- `admin_id`: Admin que uploadou
- `market_id`: Mercado da oferta
- `image_url`: URL da imagem/PDF
- `ocr_text`: Texto bruto extraído
- `valid_from`: Data de início da validade
- `valid_until`: Data de fim da validade
- `status`: Status do processamento

---

## Tabela: offer_flyer_items

**Descrição**: Itens extraídos de jornais de ofertas

```sql
CREATE TABLE offer_flyer_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    offer_flyer_id UUID NOT NULL REFERENCES offer_flyers(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id), -- NULL se produto não identificado
    description TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2), -- Preço original (se em promoção)
    unit VARCHAR(50),
    confidence DECIMAL(5, 2), -- Confiança do OCR
    is_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_offer_flyer_items_flyer ON offer_flyer_items(offer_flyer_id);
CREATE INDEX idx_offer_flyer_items_product ON offer_flyer_items(product_id);
```

**Campos**:
- `id`: UUID único do item
- `offer_flyer_id`: Jornal de ofertas (FK)
- `product_id`: Produto identificado (FK, pode ser NULL)
- `description`: Descrição original
- `price`: Preço em promoção
- `original_price`: Preço original (se houver)
- `unit`: Unidade
- `confidence`: Confiança do OCR
- `is_confirmed`: Admin confirmou/corrigiu

---

## Relacionamentos

```
users (1) ──────< (N) receipts
users (1) ──────< (N) offer_flyers
users (1) ──────< (N) prices
users (1) ──────< (N) markets (created_by)

markets (1) ──────< (N) prices
markets (1) ──────< (N) receipts
markets (1) ──────< (N) offer_flyers

products (1) ──────< (N) prices
products (1) ──────< (N) receipt_items
products (1) ──────< (N) offer_flyer_items

receipts (1) ──────< (N) receipt_items
offer_flyers (1) ──────< (N) offer_flyer_items
```

---

## Funções e Procedures

### Calcular distância entre usuário e mercado

```sql
CREATE OR REPLACE FUNCTION calculate_distance(
    user_lat DOUBLE PRECISION,
    user_lng DOUBLE PRECISION,
    market_id UUID
) RETURNS DOUBLE PRECISION AS $$
DECLARE
    market_location GEOGRAPHY;
    user_location GEOGRAPHY;
BEGIN
    SELECT location INTO market_location FROM markets WHERE id = market_id;
    user_location := ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326)::geography;
    RETURN ST_Distance(user_location, market_location) / 1000; -- Retorna em km
END;
$$ LANGUAGE plpgsql;
```

### Buscar preços de produto por proximidade

```sql
CREATE OR REPLACE FUNCTION get_prices_by_proximity(
    product_id UUID,
    user_lat DOUBLE PRECISION,
    user_lng DOUBLE PRECISION,
    radius_km DOUBLE PRECISION DEFAULT 10.0
) RETURNS TABLE (
    market_id UUID,
    market_name VARCHAR,
    price DECIMAL,
    distance_km DOUBLE PRECISION,
    captured_at TIMESTAMP WITH TIME ZONE
) AS $$
DECLARE
    user_location GEOGRAPHY;
BEGIN
    user_location := ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326)::geography;
    
    RETURN QUERY
    SELECT 
        m.id,
        m.name,
        lp.price,
        ST_Distance(user_location, m.location) / 1000 AS distance_km,
        lp.captured_at
    FROM latest_prices lp
    JOIN markets m ON lp.market_id = m.id
    WHERE lp.product_id = product_id
      AND ST_DWithin(user_location, m.location, radius_km * 1000)
    ORDER BY distance_km ASC, lp.price ASC;
END;
$$ LANGUAGE plpgsql;
```

---

## Seed Data (População Inicial)

### Mercados de Ribeirão Preto (exemplo)

```sql
INSERT INTO markets (name, address, neighborhood, latitude, longitude) VALUES
('Carrefour Ribeirão', 'Av. Presidente Vargas, 2001', 'Centro', -21.1767, -47.8208),
('Extra Ribeirão', 'Av. Wladimir Meirelles Ferreira, 2500', 'Jardim Botânico', -21.1900, -47.8100),
('Dalben Supermercados', 'Rua General Osório, 1500', 'Campos Elíseos', -21.1850, -47.8250),
('Savegnago Supermercados', 'Av. Costabile Romano, 1000', 'Quintino Facci I', -21.2000, -47.8300),
('Paulistão Supermercados', 'Av. Presidente Vargas, 3500', 'Ipiranga', -21.1800, -47.8150);
```

### Produtos comuns (exemplo)

```sql
INSERT INTO products (name, normalized_name, category, unit, quantity) VALUES
('Leite Integral Piracanjuba 1L', 'leite integral piracanjuba 1l', 'laticínios', 'L', 1.0),
('Arroz Tio João 5kg', 'arroz tio joao 5kg', 'grãos', 'kg', 5.0),
('Feijão Camil Preto 1kg', 'feijao camil preto 1kg', 'grãos', 'kg', 1.0),
('Açúcar União Cristal 1kg', 'acucar uniao cristal 1kg', 'adoçantes', 'kg', 1.0),
('Café Melitta Tradicional 500g', 'cafe melitta tradicional 500g', 'bebidas', 'g', 500.0),
('Óleo de Soja Liza 900ml', 'oleo soja liza 900ml', 'óleos', 'ml', 900.0),
('Macarrão Barilla Espaguete 500g', 'macarrao barilla espaguete 500g', 'massas', 'g', 500.0),
('Sabão em Pó Omo Lavagem Perfeita 1.6kg', 'sabao po omo lavagem perfeita 1.6kg', 'limpeza', 'kg', 1.6),
('Shampoo Pantene Restauração 400ml', 'shampoo pantene restauracao 400ml', 'higiene', 'ml', 400.0),
('Papel Higiênico Personal Vip 30m 12 Rolos', 'papel higienico personal vip 30m 12 rolos', 'higiene', 'un', 12.0);
```

---

## Migrações

Usar Alembic para gerenciar migrações:

```bash
# Criar migration inicial
alembic revision --autogenerate -m "Initial schema"

# Aplicar migrations
alembic upgrade head

# Reverter migration
alembic downgrade -1
```

---

**Aprovado por**: Hermione (autonomia delegada por Silvio)
