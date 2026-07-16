# AGENTS.md — PreçoPerto

**Monorepo**: `backend/` (FastAPI + SQLAlchemy async) and `frontend/` (React 19 + Vite 8 + TypeScript 6). No root package manager.

## Commands

### Backend (from `backend/`, activate venv first)
```bash
# PowerShell: backend\venv\Scripts\Activate.ps1
# Linux/Mac:   source venv/bin/activate

uvicorn app.main:app --reload --port 8000   # dev → localhost:8000, docs at /docs
python scripts/seed_db.py                    # DROPs all data, recreates tables, seeds demo
pytest                                       # run backend tests (in-memory SQLite)
```
- No Alembic wired up; schema created by `seed_db.py` via `Base.metadata.create_all`. Running seed = data loss.
- Dev DB: `sqlite+aiosqlite:///./preco_perto.db` (from `backend/.env`). Prod expects Supabase Postgres.
- CORS allowed origins: `https://precoperto.app`, `localhost:5173`, `localhost:3000`, `*.github.io` (`main.py`).

### Frontend (from `frontend/`)
```bash
npm run dev       # port 3000, proxies /api → localhost:8000
npm run build     # tsc -b && vite build  (typecheck + build gate)
npm run lint      # oxlint
npm run test      # vitest run (node env, no DOM APIs without mock)
npm run preview   # serve production build
```
- `npm run build` is the typecheck gate — `tsc -b` must pass before `vite build`.
- Router basename + Vite base = `/preco-perto/` — keep in sync (GitHub Pages deploy).

## Deploy

| Service | Platform | Config |
|---------|----------|--------|
| Frontend | Vercel | Root dir: `frontend/`, build: `npm run build`, output: `dist` |
| Backend | Railway | `backend/Dockerfile`, env vars from `.env.production.example` |
| Database | Supabase | PostgreSQL + PostGIS, storage buckets: `receipts`, `offer_flyers` |
| Cache | Upstash | Redis REST URL |

### Environment files
- `backend/.env` — local dev (SQLite). **Not committed** (gitignored).
- `backend/.env.example` — template, committed.
- `backend/.env.production.example` — prod template, committed.
- `frontend/.env` — local dev (`VITE_API_URL=http://localhost:8000`). **Not committed**.
- `frontend/.env.production.example` — prod template, committed.

### Setup
1. Copy `.env.example` → `.env` in `backend/` and `frontend/`, fill in real values.
2. For prod: set env vars in Vercel dashboard and Railway dashboard.
3. CI runs on PRs: lint + build + test (`.github/workflows/ci.yml`).

## Architecture

### Backend
- Routes: `/api/v1/<resource>` — auth, products, markets, prices, receipts, admin.
- **Rate limiter** middleware on all routes (`core/rate_limit.py`). Tests override it via `conftest.py`.
- **Dual-dialect DB**: custom `GUID` TypeDecorator in `core/database.py` (Postgres UUID / SQLite CHAR(36)). Use `GUID` for all id/foreign-key columns. Never import Postgres UUID types directly.
- **Config** (`core/config.py`): pydantic-settings from `backend/.env`. Required: `SUPABASE_URL`, `SUPABASE_KEY`, `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`.
- **Auth**: bcrypt + JWT (HS256). Guards in `deps.py`: `get_current_user`, `get_current_admin`.
- **Uploads dir** (`backend/uploads/`) created on startup, mounted at `/uploads`.

### Frontend
- **API**: `src/services/api.ts` (axios). JWT in `localStorage` as `precoperto_token` (+ user as `precoperto_user`). 401 interceptor clears both and redirects to `/preco-perto/login`.
- `src/pages/` (route screens), `src/components/` (MarketCard, PriceList, PriceMap, etc.), `src/hooks/` (useProducts, usePrices, useGeolocation), `src/contexts/` (AuthContext), `src/types/`.
- PWA assets static in `frontend/public/` (`manifest.json`, `sw.js`, icons) — no build plugin.

### OCR
- **Client**: `tesseract.js` in `ReceiptScanner.tsx` — camera → canvas → OCR → parse items.
- **Server**: `pytesseract` in admin routes (`/api/v1/admin/offer-flyers`) for flyer processing.

### Key data flow
- `GET /api/v1/prices/product/{id}?lat&lng&radius` — main price comparison. Filters to last 90 days (stale at 30), Haversine distance, cheapest-first, cost-benefit per transport mode.

## Tests
- Frontend: `src/services/ocr.test.ts` (vitest, node env). Add tests alongside features.
- Backend: `pytest` + `httpx` + `pytest-asyncio` in `requirements.txt`. Tests in `backend/tests/` use in-memory SQLite with `conftest.py` fixtures. Write as needed.

## SDD
Check `specs/001-price-comparison/` before implementing features. Principles in `.specify/memory/constitution.md`.
