# API Contracts — PreçoPerto MVP

**Versão**: 1.0  
**Data**: 2026-07-04  
**Base URL**: `https://api.precoperto.app` (produção) ou `http://localhost:8000` (local)

---

## Authentication

**Tipo**: JWT Bearer Token  
**Header**: `Authorization: Bearer <token>`

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "João Silva",
    "is_admin": false
  }
}
```

**Response 401**:
```json
{
  "detail": "Credenciais inválidas"
}
```

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "João Silva"
}
```

**Response 201**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "João Silva",
    "is_admin": false
  }
}
```

---

## Products

### Buscar Produtos (autocomplete)

```http
GET /api/v1/products/search?q=leite&limit=10
```

**Query Params**:
- `q` (required): Termo de busca
- `limit` (optional, default: 10): Máximo de resultados

**Response 200**:
```json
{
  "products": [
    {
      "id": "uuid",
      "name": "Leite Integral Piracanjuba 1L",
      "normalized_name": "leite integral piracanjuba 1l",
      "category": "laticínios",
      "unit": "L",
      "quantity": 1.0,
      "brand": "Piracanjuba",
      "image_url": "https://..."
    }
  ],
  "total": 5
}
```

### Obter Produto por ID

```http
GET /api/v1/products/{product_id}
```

**Response 200**:
```json
{
  "id": "uuid",
  "name": "Leite Integral Piracanjuba 1L",
  "normalized_name": "leite integral piracanjuba 1l",
  "category": "laticínios",
  "unit": "L",
  "quantity": 1.0,
  "brand": "Piracanjuba",
  "image_url": "https://...",
  "created_at": "2026-07-04T10:00:00Z"
}
```

---

## Markets

### Listar Mercados Próximos

```http
GET /api/v1/markets/nearby?lat=-21.1767&lng=-47.8208&radius=10
```

**Query Params**:
- `lat` (required): Latitude do usuário
- `lng` (required): Longitude do usuário
- `radius` (optional, default: 10): Raio em km

**Response 200**:
```json
{
  "markets": [
    {
      "id": "uuid",
      "name": "Carrefour Ribeirão",
      "address": "Av. Presidente Vargas, 2001",
      "neighborhood": "Centro",
      "latitude": -21.1767,
      "longitude": -47.8208,
      "distance_km": 0.5,
      "opening_hours": {
        "monday": {"open": "08:00", "close": "22:00"},
        "tuesday": {"open": "08:00", "close": "22:00"}
      },
      "categories": ["supermercado"]
    }
  ],
  "total": 5
}
```

### Obter Mercado por ID

```http
GET /api/v1/markets/{market_id}
```

**Response 200**:
```json
{
  "id": "uuid",
  "name": "Carrefour Ribeirão",
  "cnpj": "12.345.678/0001-90",
  "address": "Av. Presidente Vargas, 2001",
  "neighborhood": "Centro",
  "city": "Ribeirão Preto",
  "state": "SP",
  "zipcode": "14000-000",
  "latitude": -21.1767,
  "longitude": -47.8208,
  "opening_hours": {
    "monday": {"open": "08:00", "close": "22:00"},
    "tuesday": {"open": "08:00", "close": "22:00"}
  },
  "categories": ["supermercado"],
  "phone": "(16) 3333-4444",
  "created_at": "2026-07-04T10:00:00Z"
}
```

---

## Prices

### Buscar Preços de Produto (comparação)

```http
GET /api/v1/prices/product/{product_id}?lat=-21.1767&lng=-47.8208&radius=10
```

**Query Params**:
- `lat` (required): Latitude do usuário
- `lng` (required): Longitude do usuário
- `radius` (optional, default: 10): Raio em km

**Response 200**:
```json
{
  "product": {
    "id": "uuid",
    "name": "Leite Integral Piracanjuba 1L",
    "category": "laticínios",
    "unit": "L",
    "quantity": 1.0
  },
  "prices": [
    {
      "market_id": "uuid",
      "market_name": "Carrefour Ribeirão",
      "market_address": "Av. Presidente Vargas, 2001",
      "market_neighborhood": "Centro",
      "market_latitude": -21.1767,
      "market_longitude": -47.8208,
      "price": 4.99,
      "original_price": 5.99,
      "is_promotion": true,
      "promotion_ends_at": "2026-07-10",
      "distance_km": 0.5,
      "captured_at": "2026-07-03T15:30:00Z",
      "source": "oferta_flyer",
      "cost_benefit": {
        "savings_vs_most_expensive": 1.50,
        "most_expensive_price": 6.49,
        "most_expensive_market": "Mercado X",
        "transport_cost_walking": 0.0,
        "transport_cost_car": 0.38,
        "transport_cost_bus": 4.40,
        "worth_it_walking": true,
        "worth_it_car": true,
        "worth_it_bus": false
      }
    }
  ],
  "cheapest_price": 4.99,
  "most_expensive_price": 6.49,
  "average_price": 5.50,
  "total_markets": 5
}
```

### Buscar Preços por Mercado

```http
GET /api/v1/prices/market/{market_id}?limit=50
```

**Query Params**:
- `limit` (optional, default: 50): Máximo de resultados

**Response 200**:
```json
{
  "market": {
    "id": "uuid",
    "name": "Carrefour Ribeirão",
    "address": "Av. Presidente Vargas, 2001"
  },
  "prices": [
    {
      "product_id": "uuid",
      "product_name": "Leite Integral Piracanjuba 1L",
      "product_category": "laticínios",
      "price": 4.99,
      "original_price": 5.99,
      "is_promotion": true,
      "captured_at": "2026-07-03T15:30:00Z",
      "source": "oferta_flyer"
    }
  ],
  "total": 150
}
```

---

## Receipts (Notas Fiscais)

### Upload e Processar Nota Fiscal

```http
POST /api/v1/receipts
Authorization: Bearer <token>
Content-Type: multipart/form-data

image: <file>
latitude: -21.1767
longitude: -47.8208
```

**Form Data**:
- `image` (required): Imagem da nota fiscal (JPEG, PNG, PDF)
- `latitude` (optional): Latitude do usuário ao escanear
- `longitude` (optional): Longitude do usuário ao escanear

**Response 201**:
```json
{
  "receipt_id": "uuid",
  "status": "processing",
  "message": "Nota fiscal enviada para processamento. Você receberá os resultados em breve."
}
```

### Obter Status e Resultado da Nota Fiscal

```http
GET /api/v1/receipts/{receipt_id}
Authorization: Bearer <token>
```

**Response 200** (status: completed):
```json
{
  "id": "uuid",
  "status": "completed",
  "market_id": "uuid",
  "market_name": "Carrefour Ribeirão",
  "cnpj_extracted": "12.345.678/0001-90",
  "total_value": 150.75,
  "receipt_date": "2026-07-03T15:30:00Z",
  "items": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "product_name": "Leite Integral Piracanjuba 1L",
      "description": "LEITE INT PIRAC 1L",
      "quantity": 2.0,
      "unit_price": 4.99,
      "total_price": 9.98,
      "confidence": 95.5,
      "is_confirmed": false
    },
    {
      "id": "uuid",
      "product_id": null,
      "product_name": null,
      "description": "PRODUTO NAO IDENTIFICADO",
      "quantity": 1.0,
      "unit_price": 15.00,
      "total_price": 15.00,
      "confidence": 45.2,
      "is_confirmed": false
    }
  ],
  "total_items": 15,
  "confirmed_items": 12,
  "pending_review": 3
}
```

### Confirmar/Corrigir Itens da Nota Fiscal

```http
PATCH /api/v1/receipts/{receipt_id}/items
Authorization: Bearer <token>
Content-Type: application/json

{
  "items": [
    {
      "item_id": "uuid",
      "product_id": "uuid",
      "is_confirmed": true
    },
    {
      "item_id": "uuid",
      "product_id": "uuid",
      "quantity": 3.0,
      "unit_price": 5.50,
      "is_confirmed": true
    }
  ]
}
```

**Response 200**:
```json
{
  "receipt_id": "uuid",
  "status": "completed",
  "confirmed_items": 15,
  "prices_added": 15,
  "message": "Nota fiscal confirmada. 15 preços adicionados ao sistema."
}
```

---

## Offer Flyers (Jornais de Ofertas) — Admin Only

### Upload Jornal de Ofertas

```http
POST /api/v1/admin/offer-flyers
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

image: <file>
market_id: uuid
valid_from: 2026-07-01
valid_until: 2026-07-10
```

**Form Data**:
- `image` (required): Imagem/PDF do jornal (JPEG, PNG, PDF)
- `market_id` (required): ID do mercado
- `valid_from` (required): Data de início da validade
- `valid_until` (required): Data de fim da validade

**Response 201**:
```json
{
  "offer_flyer_id": "uuid",
  "status": "processing",
  "message": "Jornal de ofertas enviado para processamento."
}
```

### Obter Status e Resultado do Jornal

```http
GET /api/v1/admin/offer-flyers/{offer_flyer_id}
Authorization: Bearer <admin_token>
```

**Response 200** (status: completed):
```json
{
  "id": "uuid",
  "status": "completed",
  "market_id": "uuid",
  "market_name": "Carrefour Ribeirão",
  "valid_from": "2026-07-01",
  "valid_until": "2026-07-10",
  "items": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "product_name": "Leite Integral Piracanjuba 1L",
      "description": "Leite Integral Piracanjuba 1L",
      "price": 4.99,
      "original_price": 5.99,
      "confidence": 92.3,
      "is_confirmed": false
    }
  ],
  "total_items": 50,
  "confirmed_items": 45,
  "pending_review": 5
}
```

### Confirmar Itens do Jornal

```http
PATCH /api/v1/admin/offer-flyers/{offer_flyer_id}/items
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "items": [
    {
      "item_id": "uuid",
      "product_id": "uuid",
      "is_confirmed": true
    }
  ]
}
```

**Response 200**:
```json
{
  "offer_flyer_id": "uuid",
  "status": "completed",
  "confirmed_items": 50,
  "prices_added": 50,
  "message": "Jornal de ofertas confirmado. 50 preços adicionados ao sistema."
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Campo obrigatório ausente: email"
}
```

### 401 Unauthorized
```json
{
  "detail": "Token de autenticação inválido ou expirado"
}
```

### 403 Forbidden
```json
{
  "detail": "Acesso negado. Requer privilégios de administrador."
}
```

### 404 Not Found
```json
{
  "detail": "Produto não encontrado"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": "Dados inválidos",
  "errors": [
    {
      "field": "email",
      "message": "Email inválido"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Erro interno do servidor. Tente novamente mais tarde."
}
```

---

## Rate Limiting

- **Autenticação**: 5 requests/minuto por IP
- **Busca de produtos**: 60 requests/minuto por usuário
- **Upload de notas fiscais**: 10 requests/minuto por usuário
- **Upload de jornais (admin)**: 20 requests/minuto por admin

**Headers de Rate Limit**:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1625097600
```

---

## CORS

**Origens permitidas**:
- `https://precoperto.app` (produção)
- `https://*.github.io` (GitHub Pages)
- `http://localhost:5173` (desenvolvimento)

**Métodos permitidos**: GET, POST, PATCH, DELETE  
**Headers permitidos**: Authorization, Content-Type

---

**Aprovado por**: Hermione (autonomia delegada por Silvio)
