# Tasks — PreçoPerto MVP

**Versão**: 1.0  
**Data**: 2026-07-04  
**Status**: ✅ Aprovado

---

## Phase 1: Setup (Infraestrutura)

### [T001] Configurar Supabase
- Criar projeto no Supabase (free tier)
- Habilitar extensões: PostGIS, uuid-ossp
- Criar tabelas conforme data-model.md
- Configurar Storage buckets (receipts, offer_flyers)
- Gerar API keys (anon, service_role)
- **Output**: Supabase URL + keys documentadas

### [T002] Configurar Upstash Redis
- Criar database no Upstash (free tier)
- Gerar REST URL + token
- Testar conexão
- **Output**: Redis URL + token documentados

### [T003] Setup Backend (FastAPI)
- Criar estrutura de diretórios: `backend/app/`
- Criar `requirements.txt` (fastapi, uvicorn, sqlalchemy, psycopg2-binary, redis, python-jose, passlib, python-multipart)
- Criar `backend/app/main.py` (FastAPI app)
- Criar `backend/app/core/config.py` (Supabase URL, Redis URL, JWT secret)
- Criar `backend/app/core/database.py` (SQLAlchemy async engine)
- **Output**: Backend rodando localmente (`uvicorn app.main:app --reload`)

### [T004] Setup Frontend (React + Vite)
- Criar projeto Vite: `npm create vite@latest frontend -- --template react-ts`
- Instalar deps: leaflet, react-leaflet, axios, react-router-dom, tesseract.js
- Criar `frontend/src/services/api.ts` (axios instance com base URL)
- Criar `frontend/vite.config.ts` (proxy para backend)
- **Output**: Frontend rodando localmente (`npm run dev`)

---

## Phase 2: Foundational (Core)

### [T005] Models (SQLAlchemy)
- Criar `backend/app/models/user.py`
- Criar `backend/app/models/market.py`
- Criar `backend/app/models/product.py`
- Criar `backend/app/models/price.py`
- Criar `backend/app/models/receipt.py`
- **Output**: Models importáveis e testáveis

### [T006] Schemas (Pydantic)
- Criar `backend/app/schemas/user.py`
- Criar `backend/app/schemas/market.py`
- Criar `backend/app/schemas/product.py`
- Criar `backend/app/schemas/price.py`
- **Output**: Schemas validando dados corretamente

### [T007] Services: Geocoding
- Criar `backend/app/services/geocoding.py`
- Integrar Nominatim (OpenStreetMap) para geocoding de endereços
- Implementar cache no Redis (TTL: 7 dias)
- **Output**: `geocode_address("Av. Presidente Vargas, 2001, Ribeirão Preto")` retorna lat/lng

### [T008] Services: Product Normalization
- Criar `backend/app/services/product_normalization.py`
- Implementar: lowercase, remover acentos, padronizar unidades
- Implementar fuzzy matching (Levenshtein distance)
- **Output**: `normalize_product("Leite Integral 1L")` retorna "leite integral 1l"

### [T009] Services: Distance Calculation
- Criar `backend/app/utils/distance.py`
- Implementar cálculo de distância (Haversine formula)
- Implementar cálculo de custo-benefício (a pé, carro, ônibus)
- **Output**: `calculate_distance(lat1, lng1, lat2, lng2)` retorna km; `calculate_cost_benefit(distance_km, price_diff)` retorna recomendação

---

## Phase 3: User Story 1 — Buscar Preço de Produto (P1 Core)

### [T010] API: Buscar Produtos (autocomplete)
- Endpoint: `GET /api/v1/products/search?q=leite&limit=10`
- Query Supabase com full-text search
- Cache no Redis (TTL: 1 hora)
- **Test**: Buscar "leite" retorna 5+ produtos

### [T011] API: Buscar Preços por Produto (comparação)
- Endpoint: `GET /api/v1/prices/product/{product_id}?lat=-21.1767&lng=-47.8208&radius=10`
- Query Supabase com PostGIS (ST_DWithin para raio)
- Calcular distância e custo-benefício para cada mercado
- Ordenar por preço (mais barato primeiro)
- **Test**: Buscar preço de produto retorna lista de mercados com distância e custo-benefício

### [T012] Frontend: ProductSearch Component
- Criar `frontend/src/components/ProductSearch.tsx`
- Input com autocomplete (debounce 300ms)
- Lista de resultados com nome, categoria, imagem
- Ao clicar, navegar para tela de comparação
- **Test**: Digitar "leite" mostra lista de produtos

### [T013] Frontend: PriceList Component
- Criar `frontend/src/components/PriceList.tsx`
- Lista de mercados com: nome, preço, distância, custo-benefício
- Badge "Mais barato" para o primeiro
- Badge "Vale a pena!" se custo-benefício positivo
- **Test**: Lista mostra 5+ mercados com preços e distâncias

### [T014] Frontend: Home Page
- Criar `frontend/src/pages/Home.tsx`
- Barra de busca no topo
- Geolocalização automática (navigator.geolocation)
- Fallback: input de CEP/bairro
- **Test**: Abre no celular, pede permissão de localização, mostra busca

---

## Phase 4: User Story 2 — Escanear Nota Fiscal (P1 Core)

### [T015] API: Upload Nota Fiscal
- Endpoint: `POST /api/v1/receipts` (multipart/form-data)
- Upload imagem para Supabase Storage
- Criar registro na tabela `receipts` (status: "processing")
- **Test**: Upload de imagem retorna receipt_id

### [T016] Services: OCR (Tesseract.js client-side)
- Criar `frontend/src/services/ocr.ts`
- Integrar Tesseract.js para extração de texto
- Processar imagem da nota fiscal
- Extrair: CNPJ, produtos, preços, data
- **Test**: Processar imagem de nota fiscal retorna texto extraído

### [T017] Services: Parser de Nota Fiscal
- Criar `backend/app/services/ocr.py`
- Parser regex para extrair: CNPJ, produtos (descrição, quantidade, preço), data
- Matching com produtos existentes (fuzzy)
- Criar receipt_items com confidence score
- **Test**: Parser extrai 80%+ dos campos de nota fiscal real

### [T018] Frontend: ReceiptScanner Component
- Criar `frontend/src/components/ReceiptScanner.tsx`
- Acesso à câmera (navigator.mediaDevices.getUserMedia)
- Preview da imagem antes de enviar
- Barra de progresso durante OCR
- Lista de produtos extraídos (editável)
- Botão "Confirmar" para enviar ao backend
- **Test**: Abre câmera no celular, tira foto, mostra produtos extraídos

### [T019] API: Confirmar Itens da Nota Fiscal
- Endpoint: `PATCH /api/v1/receipts/{receipt_id}/items`
- Atualizar receipt_items (product_id, is_confirmed)
- Criar registros na tabela `prices` para itens confirmados
- **Test**: Confirmar itens adiciona preços ao sistema

---

## Phase 5: User Story 3 — Upload Jornal de Ofertas (P1 Admin)

### [T020] API: Upload Jornal de Ofertas (Admin)
- Endpoint: `POST /api/v1/admin/offer-flyers` (multipart/form-data)
- Verificar permissão de admin (is_admin=true)
- Upload imagem/PDF para Supabase Storage
- Criar registro na tabela `offer_flyers` (status: "processing")
- **Test**: Admin uploada jornal, retorna offer_flyer_id

### [T021] Services: Parser de Jornal de Ofertas
- Parser regex para extrair: produtos, preços, validade
- Matching com produtos existentes (fuzzy)
- Criar offer_flyer_items com confidence score
- **Test**: Parser extrai 80%+ dos campos de jornal de ofertas

### [T022] Frontend: Admin Panel (Upload Jornal)
- Criar `frontend/src/pages/Admin.tsx`
- Formulário: upload de imagem, seleção de mercado, datas de validade
- Preview da imagem
- Lista de produtos extraídos (editável)
- Botão "Confirmar" para adicionar preços
- **Test**: Admin uploada jornal, revisa produtos, confirma

---

## Phase 6: User Story 4 — Mapa Interativo (P1 Core)

### [T023] Frontend: PriceMap Component
- Criar `frontend/src/components/PriceMap.tsx`
- Integrar Leaflet + react-leaflet
- Pins de mercados com preço do produto
- Clusterização (Leaflet.markercluster) para muitos pins
- Popup ao clicar no pin: nome, preço, distância, custo-benefício
- **Test**: Mapa mostra 5+ pins com preços, popup abre ao clicar

### [T024] Frontend: Integração Busca → Mapa
- Criar `frontend/src/pages/Map.tsx`
- Ao buscar produto, mostrar lista + botão "Ver no mapa"
- Navegar para tela de mapa com produto selecionado
- Mapa centraliza na localização do usuário
- **Test**: Busca produto, clica "Ver no mapa", mapa abre com pins

---

## Phase 7: Data Population (Seed)

### [T025] Script: Seed de Mercados
- Criar `scripts/seed_markets.py`
- Inserir 5+ mercados de Ribeirão Preto (Carrefour, Extra, Dalben, Savegnago, Paulistão)
- Geocoding de endereços (Nominatim)
- **Output**: 5+ mercados com lat/lng no Supabase

### [T026] Script: Seed de Produtos
- Criar `scripts/seed_products.py`
- Inserir 100+ produtos comuns (laticínios, grãos, higiene, limpeza)
- Normalização de nomes
- **Output**: 100+ produtos no Supabase

### [T027] Script: Seed de Preços (de jornais de ofertas reais)
- Criar `scripts/seed_prices.py`
- Buscar imagens de jornais de ofertas na internet (Google Images)
- Extrair preços via OCR (Tesseract)
- Parser de preços extraídos
- Inserir na tabela `prices`
- **Output**: 500+ preços (100 produtos × 5 mercados) no Supabase

---

## Phase 8: PWA Configuration

### [T028] PWA: manifest.json
- Criar `frontend/public/manifest.json`
- Nome: "PreçoPerto"
- Short name: "PreçoPerto"
- Icons: 192x192, 512x512
- Theme color: #4CAF50 (verde)
- Background color: #FFFFFF
- Display: standalone
- Start URL: /
- **Output**: PWA instalável no celular

### [T029] PWA: Service Worker
- Criar `frontend/public/sw.js`
- Cache de assets estáticos (HTML, CSS, JS)
- Cache de dados de produtos (stale-while-revalidate)
- Fallback offline (mostrar última busca)
- **Output**: App funciona offline (cache de última busca)

### [T030] PWA: Permissões de Câmera
- Testar `navigator.mediaDevices.getUserMedia({video: true})`
- Solicitar permissão ao clicar em "Escanear nota"
- Tratar erro (permissão negada) com mensagem amigável
- **Output**: Câmera abre no celular após permissão

---

## Phase 9: Deploy

### [T031] Deploy Backend (Railway/Render)
- Criar `backend/Dockerfile`
- Configurar Railway/Render (auto-deploy via GitHub)
- Variáveis de ambiente: SUPABASE_URL, SUPABASE_KEY, REDIS_URL, JWT_SECRET
- **Output**: Backend acessível em https://api.precoperto.app

### [T032] Deploy Frontend (GitHub Pages)
- Configurar `frontend/vite.config.ts` para GitHub Pages (base: '/preco-perto/')
- Criar GitHub Actions workflow (`.github/workflows/deploy.yml`)
- Build e deploy automático na branch `main`
- **Output**: Frontend acessível em https://engsilvioroberto.github.io/preco-perto/

### [T033] Testes no Celular
- Acessar GitHub Pages no celular (Chrome/Safari)
- Instalar PWA (Adicionar à tela inicial)
- Testar geolocalização (pedir permissão)
- Testar busca de produto
- Testar scanner de nota fiscal (câmera)
- Testar mapa com pins
- **Output**: Todos os fluxos funcionando no celular

---

## Phase 10: Documentation

### [T034] README.md
- Atualizar README.md com:
  - Screenshots (mobile)
  - Como rodar localmente
  - Como testar no celular
  - Stack técnica
  - Licença MIT
- **Output**: README completo e profissional

### [T035] Notion: Projeto e Tarefas
- Criar projeto "PreçoPerto" no Notion (database Projetos)
- Criar 35 tarefas individuais (T001-T035) no Notion (database Tarefas)
- Vincular tarefas ao projeto
- Status: "Em Andamento" para tarefas concluídas
- **Output**: Projeto e tarefas documentados no Notion

---

## Phase 11: Auth + Admin (Jornal de Ofertas) + Core Fixes

### [T036] Auth Foundation (Backend)
- Criar `app/api/deps.py` com `oauth2_scheme`, `get_current_user`, `get_current_admin`
- Wire `decode_access_token` (era código morto)
- `POST /auth/register` retorna Token+user (201, conforme contrato)
- `POST /auth/login` atualiza `User.last_login`
- `POST /receipts/` usa `Depends(get_current_user)` (remove `TEST_USER_EMAIL` hardcoded)
- CORS com origins explícitos (não mais `allow_origins=["*"]`)
- **Output**: Rotas protegidas + admin guard funcionando

### [T037] Core Bugs: Custo-Benefício + Staleness + Seed
- Corrigir baseline do cost_benefit: `savings = most_expensive - price` (era invertido)
- Alinhar shape ao contrato v1.2 (`savings_vs_most_expensive`, `most_expensive_price`, `most_expensive_market`)
- Preços >30 dias: marcar como `is_stale=True` e ordenar fresh-first (não mais hard-filter)
- `MarketPrice` schema ganha `is_stale: bool`
- `/products/search` retorna envelope `{products, total}`
- Seed: usar `normalize_product()` para `normalized_name` (não mais strip manual)
- Seed: `source="manual"` (era "seed")
- Geocoding Redis: usar `settings.REDIS_URL` (não mais `localhost` hardcoded)
- **Output**: Comparação de preços correta + preços desatualizados sinalizados

### [T038] Cadastro de Mercado (Admin)
- `POST /api/v1/markets` com `Depends(get_current_admin)` + geocoding automático
- `MarketCreate` schema com lat/lng opcionais
- Remover Haversine duplicado (reusar `calculate_distance`)
- **Output**: Admin pode cadastrar mercados via API

### [T039] Modelos OfferFlyer + OfferFlyerItem
- `models/offer_flyer.py`, `models/offer_flyer_item.py` conforme data-model
- FKs adicionadas em `Price.product_id/market_id/created_by`, `Market.created_by`
- UNIQUE constraints em `Product` e `Price`
- `models/__init__.py` re-exporta todos os modelos
- **Output**: Tabelas criadas no schema

### [T040] OCR Server-Side + Parser de Jornal (pytesseract)
- `services/ocr.py`: `extract_text_from_image()` (pytesseract, lang='por') + `parse_offer_flyer()` (regex para R$ X,XX + texto próximo + confidence)
- `requirements.txt`: pytesseract, Pillow, asyncpg, bcrypt, pytest, httpx, pytest-asyncio
- **Output**: OCR de jornais funcionando, retorna itens com confidence score
- **Risco**: Requer Tesseract-OCR binário no sistema (Windows: instalador UB-Mannheim)

### [T041] Rotas Admin (Offer Flyers)
- `POST /admin/offer-flyers` (upload + OCR síncrono via threadpool + fuzzy match + criação de items)
- `GET /admin/offer-flyers/{id}` (detail + items)
- `PATCH /admin/offer-flyers/{id}/items` (confirmar itens → criar Prices com source="oferta_flyer", promotion_ends_at=valid_until)
- **Output**: Fluxo completo de upload → revisão → confirmação de jornais de ofertas

### [T042] Frontend Auth
- `contexts/AuthContext.tsx` com user/token/login/register/logout
- `pages/Login.tsx`, `pages/Register.tsx`
- `api.ts`: interceptors de token (request) e 401 (response → redirect login)
- `App.tsx`: ProtectedRoute (scan, profile), AdminRoute (admin), bottom nav
- **Output**: Login/cadastro funcionando, rotas protegidas

### [T043] Frontend Admin Panel
- `pages/Admin.tsx` rewrite: abas "Jornal de Ofertas" (upload + review de items + confirm) + "Novo Mercado" (form com campos)
- API client: `createMarket`, `uploadOfferFlyer`, `getOfferFlyer`, `confirmOfferFlyerItems`, `listMarkets`
- **Output**: Admin consegue uploadar jornal, revisar itens, confirmar, e cadastrar mercados

### [T044] Frontend Core Fixes
- `PriceList.tsx`: usar `savings_vs_most_expensive` do cost_benefit, mostrar transport_cost/worth_it por modo, badge de stale
- `PriceMap.tsx`: fix do ícone do marcador react-leaflet (import de PNGs + L.icon), popup com cost_benefit completo
- `types/index.ts`: `is_stale` adicionado a `MarketPrice`, novos tipos `AuthResponse`, `OfferFlyerItem`, `OfferFlyerUploadResponse`
- `ProductSearch.tsx`/api.ts ajustado ao envelope `{products, total}`
- **Output**: Interface reflete dados corretos de custo-benefício e staleness

---

## Resumo de Fases (atualizado)

| Fase | Descrição | Tarefas | Prioridade |
|------|-----------|---------|------------|
| 1 | Setup | T001-T004 | 🔴 Crítica |
| 2 | Foundational | T005-T009 | 🔴 Crítica |
| 3 | US1: Buscar Preço | T010-T014 | 🔴 Crítica |
| 4 | US2: Escanear Nota | T015-T019 | 🟡 Alta |
| 5 | US3: Upload Jornal | T020-T022 | 🟡 Alta |
| 6 | US4: Mapa | T023-T024 | 🔴 Crítica |
| 7 | Data Population | T025-T027 | 🔴 Crítica |
| 8 | PWA | T028-T030 | 🟡 Alta |
| 9 | Deploy | T031-T033 | 🔴 Crítica |
| 10 | Documentation | T034-T035 | 🟢 Média |
| 11 | Auth + Admin + Core Fixes | T036-T044 | 🔴 Crítica |

**Total**: 44 tarefas  
**Estimativa**: 5-6 dias de trabalho (com subagentes paralelos)

---

**Aprovado por**: Hermione (autonomia delegada por Silvio)
