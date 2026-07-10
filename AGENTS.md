# AGENTS.md — PreçoPerto

**Monorepo with two independent apps**: `backend/` (FastAPI + SQLAlchemy async) and `frontend/` (React 19 + Vite 8). No root-level package manager.

## Commands

### Backend (from `backend/`, activate venv first)
```bash
# On Windows (PowerShell): backend\venv\Scripts\Activate.ps1
# On Linux/Mac: source venv/bin/activate

uvicorn app.main:app --reload --port 8000   # dev → http://localhost:8000, docs at /docs
python scripts/seed_db.py                    # DROPs all data, recreates tables, seeds demo data
```
- No Alembic wired up; schema created by `seed_db.py` via `Base.metadata.create_all`. Running seed = data loss.
- Dev DB: `sqlite+aiosqlite:///./preco_perto.db` (from `backend/.env`). Prod expects Supabase Postgres.
- Tests: `pytest` + `httpx` + `pytest-asyncio` in `requirements.txt` but **no backend tests written yet**.

### Frontend (from `frontend/`)
```bash
npm run dev       # port 3000, proxies /api → localhost:8000
npm run build     # tsc -b && vite build  (typecheck + build)
npm run lint      # oxlint
npm run test      # vitest run
npm run preview   # serve production build
```
- One frontend test file: `src/services/ocr.test.ts` (vitest).
- `npm run build` is the typecheck gate — `tsc -b` fails on type errors before `vite build`.

## Architecture

### Backend
- All routes under `/api/v1/<resource>`: auth, products, markets, prices, receipts, **admin**.
- **All routes are async.** Use `AsyncSession = Depends(get_db)`, `await db.execute(select(...))`.
- **Dual-dialect DB**: custom `GUID` TypeDecorator in `core/database.py` (Postgres UUID / SQLite CHAR(36)). Use `GUID` for all id/foreign-key columns. Never import Postgres UUID types directly.
- **Config** (`core/config.py`): pydantic-settings loaded from `backend/.env`. Required: `SUPABASE_URL`, `SUPABASE_KEY`, `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`.
- **Auth** (`core/security.py`): bcrypt + JWT (HS256). `deps.py`: `get_current_user` + `get_current_admin` for route guards.
- **CORS** limited to specific origins (`main.py`), not wide open.

### Frontend
- **Router basename** and **Vite base** are both `/preco-perto/` for GitHub Pages — keep in sync.
- All API access through `src/services/api.ts` (axios). Uses `VITE_API_URL` env var.
- Pages at `src/pages/`, components at `src/components/`, hooks at `src/hooks/`, types at `src/types/`.
- PWA assets static in `frontend/public/` (no build plugin).

### OCR split
- **Client-side**: `tesseract.js` in `ReceiptScanner.tsx` — camera → canvas → OCR text → parse items.
- **Server-side**: `pytesseract` in `backend` admin routes (`/api/v1/admin/offer-flyers`) for offer flyer processing.

### Key data flow
- `GET /api/v1/prices/product/{id}?lat&lng&radius` — main price comparison endpoint. Filters prices to last 90 days (30-day stale flag), computes distance via Haversine, sorts cheapest-first, attaches cost-benefit per transport mode.

## Methodology (SDD)
Check `specs/001-price-comparison/` (`spec.md`, `plan.md`, `data-model.md`, `contracts/api.md`) before implementing features. Immutable principles in `.specify/memory/constitution.md`. Key constraints: mobile-first PWA, every Price requires `source` + `captured_at`, geolocation-anchored data, transparent cost-benefit.
