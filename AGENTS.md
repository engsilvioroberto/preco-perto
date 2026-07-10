# AGENTS.md — PreçoPerto

**Monorepo**: `backend/` (FastAPI + SQLAlchemy async) and `frontend/` (React 19 + Vite 8 + TypeScript 6). No root package manager.

## Commands

### Backend (from `backend/`, activate venv first)
```bash
# PowerShell: backend\venv\Scripts\Activate.ps1
# Linux/Mac:   source venv/bin/activate

uvicorn app.main:app --reload --port 8000   # dev → localhost:8000, docs at /docs
python scripts/seed_db.py                    # DROPs all data, recreates tables, seeds demo
```
- No Alembic wired up; schema created by `seed_db.py` via `Base.metadata.create_all`. Running seed = data loss.
- Dev DB: `sqlite+aiosqlite:///./preco_perto.db` (from `backend/.env`). Prod expects Supabase Postgres.
- CORS allowed origins: `precoperto.app`, `localhost:5173`, `localhost:3000`, `*.github.io` (`main.py`).

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

## Architecture

### Backend
- Routes: `/api/v1/<resource>` — auth, products, markets, prices, receipts, admin.
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
- Backend: **none yet** — `pytest` + `httpx` + `pytest-asyncio` in `requirements.txt`, write as needed.

## SDD
Check `specs/001-price-comparison/` before implementing features. Principles in `.specify/memory/constitution.md`.
