# Graph Report - .  (2026-07-10)

## Corpus Check
- Corpus is ~40,139 words - fits in a single context window. You may not need a graph.

## Summary
- 40 nodes · 33 edges · 21 communities (5 shown, 16 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- CI/CD & Frontend Setup
- Backend & Geocoding
- OCR & Product Normalization
- Price Comparison & Cost-Benefit
- Development Principles
- usePrices Hook
- useProducts Hook
- OCR Text Extraction
- Receipt Parsing
- Auth Response Type
- Market Type
- MarketPrice Type
- OfferFlyerItem Type
- OfferFlyerUploadResponse Type
- ParsedReceipt Type
- ParsedReceiptItem Type
- Price Type
- PriceComparison Type
- Product Type
- ReceiptUploadResponse Type
- User Type

## God Nodes (most connected - your core abstractions)
1. `PreçoPerto` - 11 edges
2. `Backend (FastAPI + SQLAlchemy)` - 6 edges
3. `OCR Receipt Pipeline` - 5 edges
4. `Frontend (React 19 + Vite 8 + TS 6)` - 4 edges
5. `Cost-Benefit Calculation (Haversine + transport costs)` - 4 edges
6. `Spec-Driven Development` - 3 edges
7. `CI Pipeline (GitHub Actions)` - 3 edges
8. `Geocoding Service (Nominatim + Redis cache)` - 3 edges
9. `Distance Calculation Service (Haversine)` - 3 edges
10. `Mobile-First, PWA-First` - 2 edges

## Surprising Connections (you probably didn't know these)
- `Cost-Benefit Calculation (Haversine + transport costs)` --semantically_similar_to--> `Transparent Cost-Benefit`  [INFERRED] [semantically similar]
  specs/001-price-comparison/clarifications.md → .specify/memory/constitution.md
- `Fuzzy Product Matching (rapidfuzz, threshold 85)` --semantically_similar_to--> `Product Normalization Service (rapidfuzz)`  [INFERRED] [semantically similar]
  specs/001-price-comparison/clarifications.md → backend/SERVICES_SUMMARY.md
- `PreçoPerto` --conceptually_related_to--> `Geolocation as Core`  [EXTRACTED]
  README.md → .specify/memory/constitution.md
- `PreçoPerto` --conceptually_related_to--> `Transparent Cost-Benefit`  [EXTRACTED]
  README.md → .specify/memory/constitution.md
- `Backend (FastAPI + SQLAlchemy)` --references--> `Product Normalization Service (rapidfuzz)`  [EXTRACTED]
  AGENTS.md → backend/SERVICES_SUMMARY.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **OCR Receipt Full Pipeline** — ocr_pipeline, heuristic_parser, fuzzy_product_matching, specs_001_price_comparison_contracts_api_markets_by_cnpj, specs_001_price_comparison_contracts_api_receipts_upload, frontend_app, backend_app [EXTRACTED 1.00]
- **Constitutional Principles for PreçoPerto** — mobile_first_pwa_first, radical_simplicity, trusted_data, geolocation_core, transparent_cost_benefit, privacy_lgpd, initial_population_flyers [EXTRACTED 1.00]

## Communities (21 total, 16 thin omitted)

### Community 0 - "CI/CD & Frontend Setup"
Cohesion: 0.38
Nodes (7): Frontend (React 19 + Vite 8 + TS 6), CI Pipeline (GitHub Actions), GitHub Pages Deploy Pipeline, Initial Population via Offer Flyers, PreçoPerto, Privacy and LGPD, Trusted Data (timestamp + origin)

### Community 1 - "Backend & Geocoding"
Cohesion: 0.40
Nodes (5): Backend (FastAPI + SQLAlchemy), Dual-Dialect DB (SQLite/Supabase), Geocoding Service (Nominatim + Redis cache), Geolocation as Core, GET /api/v1/markets/by-cnpj

### Community 2 - "OCR & Product Normalization"
Cohesion: 0.40
Nodes (5): Fuzzy Product Matching (rapidfuzz, threshold 85), Heuristic Receipt Parser (regex-based), OCR Receipt Pipeline, Product Normalization Service (rapidfuzz), POST /api/v1/receipts/

### Community 3 - "Price Comparison & Cost-Benefit"
Cohesion: 0.67
Nodes (4): Cost-Benefit Calculation (Haversine + transport costs), Distance Calculation Service (Haversine), GET /api/v1/prices/product/{id}, Transparent Cost-Benefit

### Community 4 - "Development Principles"
Cohesion: 1.00
Nodes (3): Spec-Driven Development, Mobile-First, PWA-First, Radical Simplicity

## Knowledge Gaps
- **19 isolated node(s):** `usePrices`, `useProducts`, `extractText`, `parseReceiptText`, `Product` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PreçoPerto` connect `CI/CD & Frontend Setup` to `Backend & Geocoding`, `Price Comparison & Cost-Benefit`, `Development Principles`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Why does `Backend (FastAPI + SQLAlchemy)` connect `Backend & Geocoding` to `CI/CD & Frontend Setup`, `OCR & Product Normalization`, `Price Comparison & Cost-Benefit`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `OCR Receipt Pipeline` connect `OCR & Product Normalization` to `CI/CD & Frontend Setup`, `Backend & Geocoding`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **What connects `usePrices`, `useProducts`, `extractText` to the rest of the system?**
  _22 weakly-connected nodes found - possible documentation gaps or missing edges._