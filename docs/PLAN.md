# Plan Técnico — PreçoPerto

> Documento de arquitetura, stack e decisões técnicas do MVP.
> **Versão**: 1.0 · **Data**: 2026-07-09 · **Autor**: Hermes (Dev Agent)
> **Status**: rascunho para revisão (complementa `CONSTITUTION.md` e `TASKS.md`).

---

## 1. Visão geral

O PreçoPerto é um **comparador de preços colaborativo** focado em Ribeirão Preto. O usuário escaneia uma nota fiscal (NFC-e), o sistema extrai produtos e preços via OCR, geolocaliza o estabelecimento e alimenta um mapa público de preços por bairro.

**Objetivo do MVP**: provar o loop *scan → OCR → mapa* com dados reais, sem autenticação, sem ranking social, sem histórico de usuário. Tudo público, tudo aberto (Art. 2 da Constituição).

---

## 2. Stack detalhada

### 2.1 Frontend (`/frontend` — React + Vite + TypeScript)

| Camada | Tecnologia | Versão | Justificativa |
|---|---|---|---|
| Framework UI | React | 19.x | Ecossistema maduro, `react-leaflet` nativo |
| Build tool | Vite | 8.x | HMR instantâneo, bundle otimizado para PWA |
| Linguagem | TypeScript | 6.x | Tipagem estrita para schemas de API e OCR |
| Roteamento | react-router-dom | 7.x | SPA com rotas `/`, `/map`, `/scan`, `/search` |
| Mapas | Leaflet + react-leaflet | 1.9 / 5.x | Gratuito, tiles OSM, sem vendor lock-in |
| OCR cliente | tesseract.js | 7.x | Pré-processamento no browser (preview) |
| HTTP | axios | 1.x | Interceptors, cancel tokens, timeout |
| Lint | oxlint | 1.x | Rápido, zero-config, substitui ESLint |

**PWA**: `vite-plugin-pwa` (a adicionar) com service worker para cache da última busca e ícones instaláveis.

### 2.2 Backend (`/server` — FastAPI + SQLAlchemy + SQLite)

| Camada | Tecnologia | Versão | Justificativa |
|---|---|---|---|
| Framework HTTP | FastAPI | ≥0.115 | Async nativo, OpenAPI automático, Pydantic v2 |
| ORM | SQLAlchemy 2.0 | ≥2.0 | API moderna com `async/await` |
| Driver DB | aiosqlite | ≥0.20 | SQLite assíncrono para dev/MVP |
| Validação | Pydantic v2 + pydantic-settings | ≥2.0 | Schemas de request/response + env vars |
| Migrations | Alembic | latest | Versionamento de schema (a adicionar) |
| OCR server | Tesseract 5.x (CLI) ou Google Vision | — | Decisão pendente (ver §6.2) |
| Fuzzy match | rapidfuzz | latest | Normalização de nomes de produtos |
| Geocoding | Nominatim (OSM) | — | Gratuito, suficiente para Ribeirão Preto |
| Rotas/distance | OSRM público | — | Cálculo de distância real entre pontos |
| Testes | pytest + pytest-asyncio + httpx | — | Testes async de endpoints |
| Format/lint | black + ruff | 24 / 0.7 | Padrão de código consistente |

### 2.3 Dados e mapas

- **Tiles de mapa**: OpenStreetMap (CC-BY-SA) via `tile.openstreetmap.org`.
- **Geocoding**: Nominatim (rate-limit 1 req/s) — suficiente para seed inicial de mercados.
- **Dados de produtos**: seed manual de ~100 produtos da cesta básica + 5+ mercados de RP.
- **Jornais de oferta**: ingestão manual (OCR + revisão humana) na Fase 4.

### 2.4 Infra (MVP → launch)

| Ambiente | Hospedagem | Custo |
|---|---|---|
| Dev local | `uvicorn --reload` + `vite dev` | R$ 0 |
| Staging | Railway ou Fly.io (backend) + Vercel (frontend) | ~R$ 25/mês |
| Produção MVP | Supabase (Postgres + Auth) + Vercel | ~R$ 50/mês |
| Domínio | `precoperto.com.br` (Registro.br) | R$ 40/ano |

---

## 3. Arquitetura em camadas

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Home /  │  │   Mapa   │  │  Scanner │  │   Busca    │  │
│  │  Search  │  │ Leaflet  │  │  tesser  │  │  autocomplete│ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│       └──────────────┴─────────────┴──────────────┘         │
│                          │ axios                             │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTPS (JSON)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI + async)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Router layer: /products, /markets, /prices, /ocr    │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Service layer:                                      │   │
│  │   • OCRService (Tesseract / Vision)                  │   │
│  │   • InvoiceParser (extrai CNPJ, itens, totais)       │   │
│  │   • ProductService (fuzzy match → produto canônico)  │   │
│  │   • GeoService (Nominatim + OSRM)                    │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Repository layer (SQLAlchemy async)                 │   │
│  │   Product | Market | Price | Invoice | User (futuro) │   │
│  └───────────────────────┬──────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────┘
                           ▼
              ┌────────────────────────┐
              │  SQLite (MVP)          │
              │  → Postgres/Supabase   │
              │    (produção)          │
              └────────────────────────┘
```

### 3.1 Separação de responsabilidades

- **Router**: recebe request, valida com Pydantic, delega ao service. Não contém lógica de negócio.
- **Service**: orquestra OCR, fuzzy match, geocoding. Testável isoladamente (mock do repo).
- **Repository**: acesso a dados. Uma função por operação atômica. Nunca chamada direto do router.
- **Models**: SQLAlchemy declarativo + Pydantic schemas de resposta (separados).

### 3.2 Endpoints MVP

| Método | Rota | Descrição |
|---|---|---|
| GET | `/products?q=` | Busca com fuzzy (retorna canônicos) |
| GET | `/products/{id}/prices?lat=&lon=&radius=` | Preços de um produto ordenados por distância+preço |
| GET | `/markets` | Lista mercados com coordenadas |
| GET | `/markets/{id}` | Detalhe + preços recentes |
| POST | `/invoices` | Upload de imagem de NF → OCR → revisão → grava |
| GET | `/prices/map?bbox=` | Preços dentro de bounding box (para pins do mapa) |
| GET | `/health` | Healthcheck para deploy |

---

## 4. Fluxo de dados — scan de NF

```
Usuário                 Frontend                  Backend                 DB/OCR
   │                       │                         │                       │
   │ 1. tira foto da NF    │                         │                       │
   │──────────────────────>│                         │                       │
   │                       │ 2. preview + crop       │                       │
   │                       │ (tesseract.js local)    │                       │
   │                       │                         │                       │
   │ 3. confirma upload    │                         │                       │
   │──────────────────────>│                         │                       │
   │                       │ 4. POST /invoices       │                       │
   │                       │   (multipart image)     │                       │
   │                       │────────────────────────>│                       │
   │                       │                         │ 5. envia p/ Tesseract │
   │                       │                         │──────────────────────>│
   │                       │                         │ 6. texto bruto        │
   │                       │                         │<──────────────────────│
   │                       │                         │                       │
   │                       │                         │ 7. parse NFC-e:       │
   │                       │                         │    CNPJ, itens, total │
   │                       │                         │                       │
   │                       │                         │ 8. fuzzy match cada   │
   │                       │                         │    item → Product can.│
   │                       │                         │                       │
   │                       │ 9. 200 {invoice_id,     │                       │
   │                       │     items_matched,       │                       │
   │                       │     items_to_review}     │                       │
   │                       │<────────────────────────│                       │
   │                       │                         │                       │
   │ 10. tela de revisão   │                         │                       │
   │<──────────────────────│                         │                       │
   │                       │                         │                       │
   │ 11. corrige + confirma│                         │                       │
   │──────────────────────>│                         │                       │
   │                       │ 12. PUT /invoices/{id}  │                       │
   │                       │    (items corrigidos)   │                       │
   │                       │────────────────────────>│ 13. grava Price rows  │
   │                       │                         │──────────────────────>│
   │                       │ 14. 200 OK              │                       │
   │                       │<────────────────────────│                       │
   │ 15. "Obrigado!"       │                         │                       │
   │<──────────────────────│                         │                       │
```

### 4.1 Pontos críticos do fluxo

- **Pré-processamento da imagem**: binarização, deskew, contraste (OpenCV no backend se necessário).
- **Parsing de NFC-e**: regex para blocos `CNPJ`, `DD/MM/AAAA HH:MM`, linhas `PRODUTO QTD x VALOR`.
- **Fuzzy match**: threshold ≥ 85% (rapidfuzz `WRatio`) para evitar falsos positivos.
- **Revisão humana**: itens abaixo do threshold vão para tela de revisão — nunca gravados sem confirmação (Art. 6).
- **Geolocalização do mercado**: CNPJ → consulta em base local (seed) ou Nominatim → lat/lon do mercado.

---

## 5. MVP Scope (Fases 1–5 do `TASKS.md`)

### 5.1 O que **está** no MVP

- ✅ Scan de nota fiscal (foto → OCR → revisão → grava preço)
- ✅ Mapa de preços em Ribeirão Preto (pins por mercado, filtro por produto)
- ✅ Busca por produto (autocomplete + lista ordenada por preço/distância)
- ✅ Seed de 100+ produtos e 5+ mercados de RP
- ✅ Dados 100% públicos (sem login para consultar)
- ✅ PWA instalável (manifest + service worker básico)
- ✅ Mobile-first, WCAG 2.1 AA

### 5.2 O que **NÃO está** no MVP

- ❌ Autenticação de usuário (todos são anônimos)
- ❌ Ranking/gamificação (contribuidores do mês, badges)
- ❌ Histórico pessoal de scans
- ❌ Notificações push ("abaixou o preço do arroz")
- ❌ Jornais de oferta (ingestão automática)
- ❌ Multi-cidade (só Ribeirão Preto — Art. 8)
- ❌ Pagamentos, monetização, anúncios

### 5.3 Critérios de aceite do MVP

1. Usuário escaneia uma NF real em ≤ 30s (do clique ao "obrigado").
2. ≥ 80% dos itens da NF são matched automaticamente (validado em 10 NFs reais — Task 4.8).
3. Mapa carrega em < 3s em 4G (Task 5.8).
4. 50+ usuários beta em Ribeirão Preto no primeiro mês (Task 5.10).

---

## 6. Decisões arquiteturais e trade-offs

### 6.1 SQLite (MVP) → Postgres (produção)

**Decisão**: começar com SQLite + aiosqlite, migrar para Supabase (Postgres) no launch.

| Prós SQLite | Contras SQLite |
|---|---|
| Zero infra, zero custo | Sem concorrência de escrita |
| Backup = copiar arquivo | Sem full-text search nativo robusto |
| Testes rápidos (in-memory) | Escala horizontal impossível |
| Dev local idêntico a prod (quase) | — |

**Mitigação**: usar SQLAlchemy com dialect-agnostic SQL (sem `RETURNING` específico, sem JSONB no MVP). A migration para Postgres na Task 5.1 é troca de `DATABASE_URL` + revisão de migrations Alembic.

**Gatilho para migrar**: >100 scans/dia ou >10 usuários concorrentes.

### 6.2 OCR: Tesseract local vs. Google Vision API

**Decisão pendente** (Task 4.1). Recomendação inicial: **Tesseract self-hosted** no MVP.

| Critério | Tesseract | Google Vision |
|---|---|---|
| Custo | R$ 0 (CPU do servidor) | US$ 1.50/1000 imgs |
| Precisão em NF brasileira | ~75–85% (requer tuning) | ~92–97% |
| Latência | 2–5s (CPU) | 1–2s (rede) |
| Privacidade | Imagem não sai do servidor | Imagem vai pro Google |
| Setup | Instalar `tesseract-ocr` + `por` | API key + billing |

**Recomendação**: Tesseract para MVP (Art. 3 — gratuito sempre). Se precisão < 80% após tuning (Task 4.8), migrar para Vision no pós-launch. Manter interface `OCRService` abstrata para trocar provider sem mudar callers.

### 6.3 OCR no cliente (tesseract.js) vs. servidor

**Decisão**: **ambos**, com papéis diferentes.

- **Cliente (tesseract.js)**: preview instantâneo da NF, feedback visual ("encontramos X itens"), redução de uploads inválidos.
- **Servidor (Tesseract CLI)**: OCR definitivo, com pré-processamento pesado (OpenCV), parsing de NFC-e, persistência.

**Por quê**: OCR no cliente é impreciso para NF térmica (baixo contraste), mas é ótimo para UX ("veja o que estamos lendo"). O servidor faz o trabalho pesado com modelo treinado + tuning para português brasileiro.

### 6.4 Leaflet + OSM vs. Google Maps

**Decisão**: **Leaflet + OSM** (feita, imutável).

- Google Maps cobra por carga após 28k loads/mês — incompatível com Art. 3.
- OSM tem cobertura boa em Ribeirão Preto (validar na Task 4.4).
- Leaflet é leve (~40KB gzip), PWA-friendly, sem vendor lock-in.

### 6.5 Fuzzy match: rapidfuzz vs. embeddings

**Decisão**: **rapidfuzz** (Levenshtein/WRatio) no MVP.

- Embeddings (OpenAI, sentence-transformers) seriam mais precisos para sinônimos ("agua sanitária" vs "água sanitária 1L").
- Mas: latência, custo, dependência externa, complexidade.
- rapidfuzz é determinístico, testável, <1ms por match.
- **Futuro**: adicionar embeddings como fallback quando rapidfuzz < 70%.

### 6.6 Geocoding: Nominatim vs. Google Geocoding

**Decisão**: **Nominatim (OSM)** no MVP.

- Google cobra US$ 5/1000 requests — inviável para seed de milhares de preços.
- Nominatim tem rate-limit de 1 req/s (usar com cache agressivo).
- Para endereços de mercados (≤50 no MVP), é suficiente.
- **Fallback**: geocoding manual via admin panel se Nominatim falhar.

### 6.7 Autenticação: nenhum (MVP) → Supabase Auth (pós-MVP)

**Decisão**: **sem auth no MVP**. Todos os dados são públicos (Art. 2), então não há necessidade de login para consultar.

**Por que não auth desde o início?**:
- Adiciona complexidade (tokens, refresh, logout).
- Atrita onboarding (Art. 7 — simplicidade).
- Ranking/histórico (que exigiriam auth) não estão no MVP.

**Pós-MVP**: Supabase Auth (email/senha + Google OAuth) quando introduzirmos ranking e histórico pessoal.

---

## 7. Modelo de dados (MVP)

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Product   │       │    Price    │       │   Market    │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ product_id  │       │ id (PK)     │
│ name        │       │ market_id   │──────►│ name        │
│ canonical   │       │ price       │       │ cnpj        │
│ category    │       │ quantity    │       │ address     │
│ unit        │       │ scanned_at  │       │ lat, lon    │
│ created_at  │       │ invoice_id  │       │ neighborhood│
└─────────────┘       │ confidence  │       │ created_at  │
                      └─────────────┘       └─────────────┘
                             │
                             │ FK
                             ▼
                      ┌─────────────┐
      ┌──────────────│  Invoice    │
      │              ├─────────────┤
      │              │ id (PK)     │
      │              │ market_id   │──► (opcional, inferido do CNPJ)
      │              │ cnpj        │
      │              │ scanned_at  │
      │              │ raw_text    │
      │              │ image_url   │
      │              │ reviewed    │
      │              │ created_at  │
      │              └─────────────┘
      │
      │  (futuro, pós-MVP)
      │
┌─────┴───────┐       ┌─────────────┐
│    User     │       │  OfferPaper │
├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │
│ email       │       │ market_id   │
│ name        │       │ image_url   │
│ created_at  │       │ valid_from  │
└─────────────┘       │ valid_until │
                      │ parsed_data │
                      └─────────────┘
```

**Notas**:
- `Product.canonical` é o nome normalizado (fuzzy match target).
- `Price.confidence` é 0.0–1.0, vindo do OCR (Art. 6 — transparência).
- `Invoice.reviewed` é boolean: se `false`, preços ficam marcados como "não revisado" no mapa.
- `Market.neighborhood` é texto livre (ex: "Centro", "Zona Sul") — usado para filtro grosseiro quando lat/lon não disponível.

---

## 8. Roadmap pós-MVP (V2+)

Funcionalidades planejadas para **depois** do launch em Ribeirão Preto, em ordem de prioridade:

1. **Autenticação** (Supabase Auth) — habilita ranking e histórico.
2. **Ranking de contribuidores** — gamificação leve (badges, "top scanner do mês").
3. **Histórico pessoal** — "minhas notas escaneadas", "meus produtos salvos".
4. **Notificações push** — "o arroz que você compra baixou 15% no Carrefour do Centro".
5. **Jornais de oferta automáticos** — ingestão de PDFs/imagens de encartes semanais.
6. **Lista de compras inteligente** — usuário monta lista, app sugere mercado mais barato considerando distância.
7. **Expansão para outras cidades** — São Paulo, Campinas (Art. 8).
8. **API pública** — para pesquisadores, jornalistas, gestores públicos (Art. 2).
9. **Modo offline completo** — cache de preços recentes, sync quando reconectar.
10. **Integração com códigos de barras** — scan de produto (não só NF) para consulta instantânea.

---

## 9. Riscos técnicos e mitigação

| Risco | Impacto | Probabilidade | Mitigação |
|---|---|---|---|
| OCR < 80% de precisão em NFs reais | Alto | Média | Tuning de Tesseract (por, psm 6), pré-processamento OpenCV, fallback p/ Vision |
| Nominatim não encontra endereços em RP | Médio | Baixa | Seed manual de mercados + geocoding manual via admin |
| SQLite não aguenta carga no launch | Alto | Baixa | Migrar para Supabase antes do soft-launch (Task 5.1) |
| tesseract.js lento no mobile | Médio | Alta | Limitar a preview de baixa resolução, OCR definitivo no servidor |
| Fuzzy match gera falsos positivos | Alto | Média | Threshold 85%, revisão humana obrigatória abaixo disso (Art. 6) |
| OSM sem cobertura de mercados em RP | Médio | Baixa | Validação na Task 4.4, fallback para geocoding manual |

---

## 10. Critérios de qualidade

- **Testes**: ≥ 80% de cobertura no backend (services + repositories), testes E2E (Playwright) para fluxos críticos.
- **Performance**: API responde em < 500ms (p95), mapa carrega em < 3s (4G).
- **Acessibilidade**: WCAG 2.1 AA, testado com Lighthouse ≥ 90.
- **Segurança**: inputs validados (Pydantic), SQL injection impossível (SQLAlchemy), imagens sanitizadas antes do OCR.
- **LGPD**: sem dados pessoais no MVP (tudo anônimo). Pós-MVP: termos + política + consentimento (Task 5.9).

---

## 11. Comandos de desenvolvimento

```bash
# Backend
cd server
uv sync
uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev  # http://localhost:5173

# Testes
cd server && uv run pytest
cd frontend && npm run lint

# Build de produção
cd frontend && npm run build  # → dist/
```

---

## 12. Referências

- [Constituição do PreçoPerto](./CONSTITUTION.md) — princípios não-negociáveis.
- [Tasks do MVP](./TASKS.md) — decomposição em 5 fases (38 dias úteis).
- [Spec-Driven Development](./SPEC_DRIVEN_DEVELOPMENT.md) — metodologia.
- [FastAPI docs](https://fastapi.tiangolo.com/) — backend.
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) — ORM async.
- [Tesseract OCR](https://tesseract-ocr.github.io/) — OCR self-hosted.
- [Leaflet](https://leafletjs.com/) — mapas.
- [OpenStreetMap](https://www.openstreetmap.org/) — tiles e geodados.

---

**Próximos passos**:

1. Revisar este plan com o time (PO, ops, content).
2. Resolver clarifications pendentes no `spec.md` (Task 1.5).
3. Fechar decisão de OCR (Tesseract vs. Vision) com spike na Fase 2.
4. Aprovar modelo de dados (Task 1.6) antes de iniciar Fase 2.

---

*PreçoPerto — porque o melhor preço é o preço que a gente descobre junto.*
