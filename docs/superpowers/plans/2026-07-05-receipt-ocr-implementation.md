# Receipt OCR Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the stubbed receipt scanner (fake simulated results, unused camera capture, no-op backend endpoint) with a real pipeline: capture image (camera or file upload) → Tesseract.js OCR → heuristic parser extracts CNPJ/items/total → resolve market (by CNPJ, or manual pick from nearby list) → user reviews/edits items → backend persists `Receipt` + creates/reuses `Product` + creates `Price` rows.

**Architecture:** OCR and parsing run entirely client-side (Tesseract.js + a pure regex-based parser function). The backend receives already-parsed, user-confirmed items as JSON plus the original image, resolves or validates the market, and does product fuzzy-matching + persistence — no OCR happens server-side.

**Tech Stack:** tesseract.js 7.0.0 (already a frontend dependency, unused until now), vitest (new, for testing the pure parser function), FastAPI + SQLAlchemy async (existing backend stack), existing `product_normalization.fuzzy_match`/`normalize_product` services.

## Global Constraints

- No automated browser/camera testing is available to whoever executes this plan. Any step touching `getUserMedia`, `<video>`/`<canvas>` capture, or the real Tesseract.js worker must be verified **manually in a real browser** — say so explicitly in that step rather than claiming an automated pass.
- Receipts are attributed to a fixed seed user (`joao@gmail.com`) — there is no login flow yet. Do not build login as part of this plan.
- The parser is best-effort. Do not try to make it handle every possible Brazilian receipt layout — the review UI (editable items) is the safety net, not the parser.
- Fuzzy-match threshold for reusing an existing `Product` instead of creating a new one is `85.0` (score from `fuzzy_match`, which returns 0–100).
- Design reference: `docs/superpowers/specs/2026-07-05-receipt-ocr-design.md`.

---

### Task 1: Backend — market lookup by CNPJ

**Files:**
- Modify: `backend/app/api/routes/markets.py`

**Interfaces:**
- Consumes: existing `Market` model (`backend/app/models/market.py`) — fields `id`, `name`, `cnpj` (nullable `String(18)`); existing `MarketResponse` schema (`backend/app/schemas/market.py`).
- Produces: `GET /api/v1/markets/by-cnpj?cnpj=<string>` → `200` with a `MarketResponse` body, or `404` with `{"detail": "Mercado não encontrado para este CNPJ"}`. CNPJ comparison ignores punctuation (`.`, `/`, `-`) on both sides.

- [ ] **Step 1: Add the route**

Open `backend/app/api/routes/markets.py`. Add `import re` to the top imports (it currently reads `from fastapi import APIRouter, Depends, HTTPException, Query`, `from sqlalchemy.ext.asyncio import AsyncSession`, `from sqlalchemy import select, func, text`, `from app.core.database import get_db`, `from app.models.market import Market`, `from app.schemas.market import MarketResponse`, `from typing import List`, `import math`).

Insert the new route **between** the existing `get_nearby_markets` function and the existing `get_market` function (the one with path `/{market_id}`). Ordering matters: FastAPI matches routes in registration order, and `/{market_id}` would otherwise swallow requests to `/by-cnpj` by treating `"by-cnpj"` as a market id.

```python
@router.get("/by-cnpj", response_model=MarketResponse)
async def get_market_by_cnpj(cnpj: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Buscar mercado pelo CNPJ extraído de uma nota fiscal escaneada"""
    digits_only = re.sub(r'\D', '', cnpj)
    result = await db.execute(select(Market))
    markets = result.scalars().all()

    for market in markets:
        if market.cnpj and re.sub(r'\D', '', market.cnpj) == digits_only:
            return market

    raise HTTPException(status_code=404, detail="Mercado não encontrado para este CNPJ")
```

- [ ] **Step 2: Restart the backend and verify with curl**

The dev server auto-reloads on file save (`uvicorn --reload`). If it's not running, start it from `backend/`:

```bash
venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

Run (from `backend/`, in a separate terminal):

```bash
curl -s "http://localhost:8000/api/v1/markets/by-cnpj?cnpj=45.543.915/0001-81"
```

Expected: JSON body with `"name":"Carrefour Ribeirão"` (this is the seeded CNPJ for that market — confirm your local seed still has it via `venv/Scripts/python.exe -c "import sqlite3; print(sqlite3.connect('preco_perto.db').execute(\"SELECT name, cnpj FROM markets\").fetchall())"` if the response doesn't match).

Then verify punctuation-insensitivity:

```bash
curl -s "http://localhost:8000/api/v1/markets/by-cnpj?cnpj=45543915000181"
```

Expected: identical JSON body to the previous call.

Then verify the 404 path:

```bash
curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8000/api/v1/markets/by-cnpj?cnpj=00000000000000"
```

Expected: `404`

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/routes/markets.py
git commit -m "feat: add GET /markets/by-cnpj lookup endpoint"
```

---

### Task 2: Backend — real receipt upload pipeline

**Files:**
- Create: `backend/app/schemas/receipt.py`
- Modify: `backend/app/api/routes/receipts.py` (full rewrite)
- Modify: `backend/app/main.py` (mount `/uploads` static dir)
- Create: `backend/.gitignore`

**Interfaces:**
- Consumes: `Market` model, `Product` model (`backend/app/models/product.py`), `Price` model (`backend/app/models/price.py`), `Receipt` model (`backend/app/models/receipt.py`), `User` model (`backend/app/models/user.py`), `normalize_product(name: str) -> str` and `fuzzy_match(name1: str, name2: str) -> float` from `backend/app/services/product_normalization.py`.
- Produces: `POST /api/v1/receipts/` accepting `multipart/form-data` with fields `image` (file), `market_id` (str), `items` (str, JSON array of `{"description": str, "price": number}`), `cnpj` (optional str), `ocr_text` (optional str), `latitude`/`longitude` (optional float) → `200` with `{"receipt_id": str, "products_created": int, "prices_created": int}`. Images are saved to `backend/uploads/receipts/<uuid><ext>` and served at `/uploads/receipts/<uuid><ext>`.

- [ ] **Step 1: Create the receipt schemas**

Create `backend/app/schemas/receipt.py`:

```python
from decimal import Decimal
from pydantic import BaseModel


class ReceiptItemIn(BaseModel):
    description: str
    price: Decimal


class ReceiptUploadResponse(BaseModel):
    receipt_id: str
    products_created: int
    prices_created: int
```

- [ ] **Step 2: Rewrite the receipts route**

Replace the entire contents of `backend/app/api/routes/receipts.py` with:

```python
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.market import Market
from app.models.product import Product
from app.models.price import Price
from app.models.receipt import Receipt
from app.models.user import User
from app.schemas.receipt import ReceiptItemIn, ReceiptUploadResponse
from app.services.product_normalization import normalize_product, fuzzy_match

router = APIRouter()

TEST_USER_EMAIL = "joao@gmail.com"
FUZZY_MATCH_THRESHOLD = 85.0
UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads" / "receipts"


@router.post("/", response_model=ReceiptUploadResponse)
async def upload_receipt(
    image: UploadFile = File(...),
    market_id: str = Form(...),
    items: str = Form(...),
    cnpj: Optional[str] = Form(None),
    ocr_text: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload e processamento de nota fiscal escaneada (itens já extraídos e revisados no client)"""
    result = await db.execute(select(Market).where(Market.id == market_id))
    market = result.scalar_one_or_none()
    if not market:
        raise HTTPException(status_code=404, detail="Mercado não encontrado")

    result = await db.execute(select(User).where(User.email == TEST_USER_EMAIL))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=500, detail="Usuário de teste não encontrado — rode scripts/seed_db.py")

    try:
        raw_items = json.loads(items)
        parsed_items = [ReceiptItemIn(**item) for item in raw_items]
    except (json.JSONDecodeError, TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Campo 'items' inválido, esperado JSON com lista de {description, price}"
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    image_id = uuid.uuid4()
    extension = Path(image.filename or "").suffix or ".jpg"
    image_path = UPLOAD_DIR / f"{image_id}{extension}"
    image_bytes = await image.read()
    image_path.write_bytes(image_bytes)

    now = datetime.utcnow()
    receipt = Receipt(
        id=uuid.uuid4(),
        user_id=user.id,
        market_id=market.id,
        image_url=f"/uploads/receipts/{image_id}{extension}",
        ocr_text=ocr_text,
        cnpj_extracted=cnpj,
        status="completed",
        created_at=now,
        updated_at=now,
    )
    db.add(receipt)

    result = await db.execute(select(Product))
    existing_products = list(result.scalars().all())

    products_created = 0
    prices_created = 0

    for item in parsed_items:
        matched_product = None
        best_score = 0.0
        for product in existing_products:
            score = fuzzy_match(item.description, product.name)
            if score >= FUZZY_MATCH_THRESHOLD and score > best_score:
                matched_product = product
                best_score = score

        if matched_product is None:
            matched_product = Product(
                id=uuid.uuid4(),
                name=item.description,
                normalized_name=normalize_product(item.description),
                created_at=now,
                updated_at=now,
            )
            db.add(matched_product)
            existing_products.append(matched_product)
            products_created += 1

        price = Price(
            id=uuid.uuid4(),
            product_id=matched_product.id,
            market_id=market.id,
            price=item.price,
            source="receipt_scan",
            created_by=user.id,
            captured_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(price)
        prices_created += 1

    await db.commit()

    return ReceiptUploadResponse(
        receipt_id=str(receipt.id),
        products_created=products_created,
        prices_created=prices_created,
    )
```

- [ ] **Step 3: Mount the uploads directory as static files**

Open `backend/app/main.py`. It currently reads:

```python

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, products, markets, prices, receipts

app = FastAPI(
    title="PreçoPerto API",
    version="1.0.0",
    description="API para comparação de preços colaborativa"
)
```

Change it to:

```python

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import auth, products, markets, prices, receipts

app = FastAPI(
    title="PreçoPerto API",
    version="1.0.0",
    description="API para comparação de preços colaborativa"
)

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
```

Leave the rest of the file (CORS middleware, routers, `/` and `/health` endpoints) unchanged.

- [ ] **Step 4: Ignore uploaded files in git**

Create `backend/.gitignore`:

```
uploads/
```

- [ ] **Step 5: Verify end-to-end with curl**

Restart the backend if `main.py` changes weren't picked up by `--reload` (StaticFiles mounts sometimes need a manual restart):

```bash
cd backend
venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

In another terminal, from `backend/`, look up the Carrefour market id dynamically (don't hardcode it — it's a random UUID regenerated every time `seed_db.py` runs), create a throwaway image file, and upload a receipt with one item that should match an existing seeded product and one that should create a new product:

```bash
cd backend
MARKET_ID=$(curl -s "http://localhost:8000/api/v1/markets/by-cnpj?cnpj=45.543.915/0001-81" | venv/Scripts/python.exe -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "fake receipt image bytes" > test_receipt.jpg
curl -s -X POST "http://localhost:8000/api/v1/receipts/" \
  -F "image=@test_receipt.jpg;type=image/jpeg" \
  -F "market_id=$MARKET_ID" \
  -F "cnpj=45.543.915/0001-81" \
  -F 'items=[{"description":"Leite Integral Piracanjuba 1L","price":"4.99"},{"description":"Iogurte Grego Danone 170g","price":"6.50"}]' \
  -F "latitude=-21.1767" -F "longitude=-47.8208"
rm test_receipt.jpg
```

Expected JSON response: `{"receipt_id":"<some-uuid>","products_created":1,"prices_created":2}` — `"Leite Integral Piracanjuba 1L"` matches the existing seeded product (score 100, reused), `"Iogurte Grego Danone 170g"` doesn't exist yet (new product created).

Verify the DB state directly:

```bash
venv/Scripts/python.exe -c "
import sqlite3
conn = sqlite3.connect('preco_perto.db')
cur = conn.cursor()
print('Receipts:', cur.execute(\"SELECT status, cnpj_extracted, image_url FROM receipts ORDER BY created_at DESC LIMIT 1\").fetchall())
print('New product:', cur.execute(\"SELECT name FROM products WHERE name LIKE '%Iogurte%'\").fetchall())
print('New prices:', cur.execute(\"SELECT price, source FROM prices WHERE source='receipt_scan'\").fetchall())
"
```

Expected: one receipt row with `status='completed'`, the CNPJ, and an `image_url` starting with `/uploads/receipts/`; one product row for "Iogurte Grego Danone 170g"; two price rows with `source='receipt_scan'` (values `4.99` and `6.50`).

Confirm the image was actually saved and is servable:

```bash
ls backend/uploads/receipts/
IMAGE_URL=$(venv/Scripts/python.exe -c "
import sqlite3
conn = sqlite3.connect('preco_perto.db')
print(conn.execute('SELECT image_url FROM receipts ORDER BY created_at DESC LIMIT 1').fetchone()[0])
")
curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8000$IMAGE_URL"
```

Expected: `200`.

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/receipt.py backend/app/api/routes/receipts.py backend/app/main.py backend/.gitignore
git commit -m "feat: implement real receipt upload with product fuzzy-match and price creation"
```

---

### Task 3: Frontend — add vitest test infrastructure

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/services/sanity.test.ts` (temporary, deleted in this same task once it's served its purpose)

**Interfaces:**
- Produces: `npm run test` (from `frontend/`) runs vitest once and exits; used by Task 4 to TDD the OCR parser.

- [ ] **Step 1: Install vitest**

```bash
cd frontend
npm install -D vitest
```

- [ ] **Step 2: Add the test script**

Modify `frontend/package.json` — add `"test": "vitest run"` to the `"scripts"` block (currently `dev`, `build`, `lint`, `preview`):

```json
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "oxlint",
    "preview": "vite preview",
    "test": "vitest run"
  },
```

- [ ] **Step 3: Add vitest config**

Create `frontend/vitest.config.ts`:

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
  },
});
```

- [ ] **Step 4: Write a throwaway sanity test and verify the runner works**

Create `frontend/src/services/sanity.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';

describe('sanity', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2);
  });
});
```

Run:

```bash
npm run test
```

Expected: output shows `1 passed` (or similar), exit code 0.

- [ ] **Step 5: Delete the sanity test**

It served only to confirm the runner works; Task 4 adds the real test file.

```bash
rm frontend/src/services/sanity.test.ts
```

- [ ] **Step 6: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vitest.config.ts
git commit -m "chore: add vitest test runner"
```

---

### Task 4: Frontend — OCR text extraction and heuristic parser

**Files:**
- Create: `frontend/src/services/ocr.ts`
- Create: `frontend/src/services/ocr.test.ts`
- Modify: `frontend/src/types/index.ts`

**Interfaces:**
- Consumes: `createWorker` from `tesseract.js` (already a dependency, `createWorker(langs?: string | string[]): Promise<Worker>`, `Worker.recognize(image): Promise<{data: {text: string}}>`, `Worker.terminate(): Promise<void>` — confirmed against the installed v7.0.0 type declarations).
- Produces (used by Task 6): `extractText(imageDataUrl: string): Promise<string>` and `parseReceiptText(text: string): ParsedReceipt` from `frontend/src/services/ocr.ts`; types `ParsedReceiptItem { description: string; price: number; include: boolean }` and `ParsedReceipt { cnpj: string | null; total: number | null; date: string | null; items: ParsedReceiptItem[] }` from `frontend/src/types/index.ts`.

- [ ] **Step 1: Add the new types**

Modify `frontend/src/types/index.ts` — append at the end of the file (after the existing `User` interface):

```typescript

export interface ParsedReceiptItem {
  description: string;
  price: number;
  include: boolean;
}

export interface ParsedReceipt {
  cnpj: string | null;
  total: number | null;
  date: string | null;
  items: ParsedReceiptItem[];
}

export interface ReceiptUploadResponse {
  receipt_id: string;
  products_created: number;
  prices_created: number;
}
```

- [ ] **Step 2: Write the failing parser tests**

Create `frontend/src/services/ocr.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { parseReceiptText } from './ocr';

describe('parseReceiptText', () => {
  it('extracts cnpj, date, total and items from a typical cupom fiscal', () => {
    const text = [
      'SUPERMERCADO EXEMPLO LTDA',
      'CNPJ: 45.543.915/0001-81',
      'AV PRESIDENTE VARGAS 2001',
      'CUPOM FISCAL ELETRONICO - SAT',
      '------------------------------',
      '001 LEITE INTEGRAL PIRACANJUBA 1L UN 4,99',
      '002 ARROZ TIO JOAO 5KG UN 25,90',
      '003 FEIJAO PRETO CAMIL 1KG UN 9,50',
      '------------------------------',
      'TOTAL R$ 40,39',
      'FORMA PAGAMENTO: DINHEIRO',
      'DATA: 05/07/2026 14:32:10',
    ].join('\n');

    const result = parseReceiptText(text);

    expect(result.cnpj).toBe('45.543.915/0001-81');
    expect(result.date).toBe('05/07/2026');
    expect(result.total).toBe(40.39);
    expect(result.items).toEqual([
      { description: 'LEITE INTEGRAL PIRACANJUBA 1L', price: 4.99, include: true },
      { description: 'ARROZ TIO JOAO 5KG', price: 25.90, include: true },
      { description: 'FEIJAO PRETO CAMIL 1KG', price: 9.50, include: true },
    ]);
  });

  it('matches a CNPJ with no punctuation and a price prefixed with R$', () => {
    const text = [
      'FARMACIA TESTE',
      'CNPJ 12345678000199',
      'SHAMPOO PANTENE 400ML R$ 15,90',
      'TOTAL 15,90',
    ].join('\n');

    const result = parseReceiptText(text);

    expect(result.cnpj).toBe('12345678000199');
    expect(result.total).toBe(15.90);
    expect(result.items).toEqual([
      { description: 'SHAMPOO PANTENE 400ML', price: 15.90, include: true },
    ]);
  });

  it('parses a total with a thousands separator', () => {
    const text = 'TOTAL R$ 1.234,56';

    const result = parseReceiptText(text);

    expect(result.total).toBe(1234.56);
  });

  it('returns empty items and null fields for text with no recognizable lines', () => {
    const text = 'ALGUM TEXTO SEM ITENS\nOUTRA LINHA QUALQUER';

    const result = parseReceiptText(text);

    expect(result.cnpj).toBeNull();
    expect(result.total).toBeNull();
    expect(result.date).toBeNull();
    expect(result.items).toEqual([]);
  });
});
```

- [ ] **Step 3: Run the tests to verify they fail**

```bash
cd frontend
npm run test
```

Expected: FAIL — `Cannot find module './ocr'` (the file doesn't exist yet).

- [ ] **Step 4: Implement `ocr.ts`**

Create `frontend/src/services/ocr.ts`:

```typescript
import { createWorker } from 'tesseract.js';
import type { ParsedReceipt, ParsedReceiptItem } from '../types';

const CNPJ_REGEX = /(\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2})/;
const DATE_REGEX = /(\d{2}\/\d{2}\/\d{4})/;
const PRICE_AT_END_REGEX = /(?:R\$\s?)?(\d{1,3}(?:\.\d{3})*,\d{2})\s*$/;
const LEADING_CODE_REGEX = /^\d+\s+/;
const QUANTITY_MARKER_REGEX = /\b(UN|KG|X\s?\d+)\b/gi;

function parsePriceToken(token: string): number {
  return parseFloat(token.replace(/\./g, '').replace(',', '.'));
}

/**
 * Extracts raw text from a captured receipt image using Tesseract.js.
 * Real OCR runtime behavior (worker download, recognition quality) can only
 * be verified manually in a browser — see Task 6 verification steps.
 */
export async function extractText(imageDataUrl: string): Promise<string> {
  const worker = await createWorker('por');
  try {
    const { data } = await worker.recognize(imageDataUrl);
    return data.text;
  } finally {
    await worker.terminate();
  }
}

export function parseReceiptText(text: string): ParsedReceipt {
  const lines = text.split('\n').map((line) => line.trim()).filter(Boolean);

  let cnpj: string | null = null;
  let total: number | null = null;
  let date: string | null = null;
  const items: ParsedReceiptItem[] = [];

  for (const line of lines) {
    if (!cnpj) {
      const cnpjMatch = line.match(CNPJ_REGEX);
      if (cnpjMatch) cnpj = cnpjMatch[1];
    }

    if (!date) {
      const dateMatch = line.match(DATE_REGEX);
      if (dateMatch) date = dateMatch[1];
    }

    if (/total/i.test(line)) {
      const totalMatch = line.match(PRICE_AT_END_REGEX);
      if (totalMatch) {
        total = parsePriceToken(totalMatch[1]);
        continue;
      }
    }

    const priceMatch = line.match(PRICE_AT_END_REGEX);
    if (priceMatch && typeof priceMatch.index === 'number') {
      let description = line.slice(0, priceMatch.index).trim();
      description = description.replace(LEADING_CODE_REGEX, '');
      description = description.replace(QUANTITY_MARKER_REGEX, '');
      description = description.replace(/\s+/g, ' ').trim();

      if (description.length > 0) {
        items.push({
          description,
          price: parsePriceToken(priceMatch[1]),
          include: true,
        });
      }
    }
  }

  return { cnpj, total, date, items };
}
```

- [ ] **Step 5: Run the tests to verify they pass**

```bash
npm run test
```

Expected: all 4 tests in `ocr.test.ts` PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/services/ocr.ts frontend/src/services/ocr.test.ts frontend/src/types/index.ts
git commit -m "feat: add Tesseract.js OCR wrapper and heuristic receipt parser"
```

---

### Task 5: Frontend — file upload capture in ReceiptScanner

**Files:**
- Modify: `frontend/src/components/ReceiptScanner.tsx`
- Modify: `frontend/src/App.css`

**Interfaces:**
- Produces: `ReceiptScanner`'s `onCapture` prop changes from `() => void` to `(imageDataUrl: string) => void`, called with a base64 data URL both when capturing from the live camera and when selecting a file. `Scan.tsx` (rewritten in Task 6) is the only consumer — no other code references this component today, and TypeScript's parameter bivariance means the current `Scan.tsx` (which passes a zero-argument `handleCapture`) still compiles unchanged against the new signature.

- [ ] **Step 1: Replace the component**

Replace the entire contents of `frontend/src/components/ReceiptScanner.tsx`:

```tsx
import { useState, useRef } from 'react';

interface ReceiptScannerProps {
  onCapture: (imageDataUrl: string) => void;
}

export const ReceiptScanner = ({ onCapture }: ReceiptScannerProps) => {
  const [preview, setPreview] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      alert('Não foi possível acessar a câmera. Verifique as permissões.');
    }
  };

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg');
        setPreview(imageData);
        onCapture(imageData);
      }
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const imageData = reader.result as string;
      setPreview(imageData);
      onCapture(imageData);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="receipt-scanner">
      {!preview ? (
        <div className="camera-container">
          <video ref={videoRef} autoPlay playsInline />
          <button onClick={startCamera} className="btn-start-camera">
            📷 Abrir Câmera
          </button>
          <button onClick={captureImage} className="btn-capture">
            Capturar
          </button>
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          <button onClick={() => fileInputRef.current?.click()} className="btn-upload">
            🖼️ Selecionar Arquivo
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
        </div>
      ) : (
        <div className="preview-container">
          <img src={preview} alt="Preview" />
        </div>
      )}
    </div>
  );
};
```

- [ ] **Step 2: Add styles for the new upload button**

Append to `frontend/src/App.css`, right after the existing `.btn-capture` rule (around line 386):

```css

.btn-upload {
  width: 100%;
  padding: 12px;
  margin-top: 8px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  background: #757575;
  color: white;
}
```

- [ ] **Step 3: Verify the frontend still builds**

```bash
cd frontend
npm run build
```

Expected: build succeeds with no TypeScript errors (confirms `Scan.tsx`'s current zero-arg `handleCapture` is still assignable to the new `onCapture` prop type).

- [ ] **Step 4: Manually verify file upload in the browser**

This cannot be automated — do it yourself:

1. Start the frontend dev server if it isn't running: `npm run dev` (from `frontend/`).
2. Open `http://localhost:3000/preco-perto/scan`.
3. Click "🖼️ Selecionar Arquivo" and pick any image file from your computer.
4. Expected: the chosen image replaces the camera view as a preview on screen.
5. Open the browser DevTools console — expected: no errors logged.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ReceiptScanner.tsx frontend/src/App.css
git commit -m "feat: support selecting an image file as an alternative to live camera capture"
```

---

### Task 6: Frontend — wire the full pipeline into the Scan page

**Files:**
- Modify: `frontend/src/services/api.ts`
- Modify: `frontend/src/pages/Scan.tsx` (full rewrite)
- Modify: `frontend/src/App.css`

**Interfaces:**
- Consumes: `GET /api/v1/markets/by-cnpj` (Task 1), `POST /api/v1/receipts/` (Task 2), `extractText`/`parseReceiptText` and `ParsedReceiptItem`/`ParsedReceipt`/`ReceiptUploadResponse` types (Task 4), `ReceiptScanner`'s `onCapture: (imageDataUrl: string) => void` (Task 5), existing `getNearbyMarkets(lat, lng, radius): Promise<Market[]>` and `useGeolocation()` (unchanged).
- Produces: a working `/scan` page — the end state of this plan.

- [ ] **Step 1: Add API client functions**

Open `frontend/src/services/api.ts`. Change the type import line at the top from:

```typescript
import type { Product, Market, PriceComparison } from '../types';
```

to:

```typescript
import type { Product, Market, PriceComparison, ReceiptUploadResponse } from '../types';
```

Add this block right before the final `export default api;` line:

```typescript

// Receipts
export const lookupMarketByCnpj = async (cnpj: string): Promise<Market | null> => {
  try {
    const response = await api.get(`/api/v1/markets/by-cnpj`, { params: { cnpj } });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return null;
    }
    throw error;
  }
};

interface UploadReceiptPayload {
  image: Blob;
  marketId: string;
  items: { description: string; price: number }[];
  cnpj?: string;
  ocrText?: string;
  latitude?: number;
  longitude?: number;
}

export const uploadReceipt = async (payload: UploadReceiptPayload): Promise<ReceiptUploadResponse> => {
  const formData = new FormData();
  formData.append('image', payload.image, 'receipt.jpg');
  formData.append('market_id', payload.marketId);
  formData.append('items', JSON.stringify(payload.items));
  if (payload.cnpj) formData.append('cnpj', payload.cnpj);
  if (payload.ocrText) formData.append('ocr_text', payload.ocrText);
  if (payload.latitude !== undefined) formData.append('latitude', String(payload.latitude));
  if (payload.longitude !== undefined) formData.append('longitude', String(payload.longitude));

  // Do not set a Content-Type header manually — axios/the browser must set
  // multipart/form-data with the correct boundary automatically for FormData.
  const response = await api.post(`/api/v1/receipts/`, formData);
  return response.data;
};
```

- [ ] **Step 2: Rewrite the Scan page**

Replace the entire contents of `frontend/src/pages/Scan.tsx`:

```tsx

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ReceiptScanner } from '../components/ReceiptScanner';
import { useGeolocation } from '../hooks/useGeolocation';
import { extractText, parseReceiptText } from '../services/ocr';
import { lookupMarketByCnpj, uploadReceipt, getNearbyMarkets } from '../services/api';
import type { ParsedReceiptItem, Market, ReceiptUploadResponse } from '../types';

type ScanStage = 'idle' | 'ocr_processing' | 'resolving_market' | 'reviewing' | 'submitting' | 'done' | 'error';

export const Scan = () => {
  const navigate = useNavigate();
  const { latitude, longitude } = useGeolocation();

  const [stage, setStage] = useState<ScanStage>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [ocrText, setOcrText] = useState('');
  const [cnpj, setCnpj] = useState<string | null>(null);
  const [items, setItems] = useState<ParsedReceiptItem[]>([]);
  const [resolvedMarket, setResolvedMarket] = useState<Market | null>(null);
  const [nearbyMarkets, setNearbyMarkets] = useState<Market[]>([]);
  const [result, setResult] = useState<ReceiptUploadResponse | null>(null);

  const handleCapture = async (imageDataUrl: string) => {
    setCapturedImage(imageDataUrl);
    setStage('ocr_processing');
    setErrorMessage(null);

    try {
      const text = await extractText(imageDataUrl);
      setOcrText(text);
      const parsed = parseReceiptText(text);
      setCnpj(parsed.cnpj);
      setItems(parsed.items);

      setStage('resolving_market');

      if (parsed.cnpj) {
        const market = await lookupMarketByCnpj(parsed.cnpj);
        if (market) {
          setResolvedMarket(market);
          setStage('reviewing');
          return;
        }
      }

      if (latitude !== null && longitude !== null) {
        const nearby = await getNearbyMarkets(latitude, longitude, 10);
        setNearbyMarkets(nearby);
      }
      setStage('reviewing');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Erro ao processar a nota fiscal');
      setStage('error');
    }
  };

  const updateItem = (index: number, updates: Partial<ParsedReceiptItem>) => {
    setItems((prev) => prev.map((item, i) => (i === index ? { ...item, ...updates } : item)));
  };

  const handleSubmit = async () => {
    if (!resolvedMarket || !capturedImage) return;

    setStage('submitting');
    setErrorMessage(null);

    try {
      const includedItems = items.filter((item) => item.include);
      const imageBlob = await (await fetch(capturedImage)).blob();

      const response = await uploadReceipt({
        image: imageBlob,
        marketId: resolvedMarket.id,
        items: includedItems.map(({ description, price }) => ({ description, price })),
        cnpj: cnpj ?? undefined,
        ocrText,
        latitude: latitude ?? undefined,
        longitude: longitude ?? undefined,
      });

      setResult(response);
      setStage('done');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Erro ao enviar a nota fiscal');
      setStage('error');
    }
  };

  const reset = () => {
    setStage('idle');
    setCapturedImage(null);
    setOcrText('');
    setCnpj(null);
    setItems([]);
    setResolvedMarket(null);
    setNearbyMarkets([]);
    setResult(null);
    setErrorMessage(null);
  };

  return (
    <div className="scan-page">
      <header className="scan-header">
        <button onClick={() => navigate('/')} className="btn-back">←</button>
        <h2>Escanear Nota Fiscal</h2>
      </header>

      {stage === 'idle' && <ReceiptScanner onCapture={handleCapture} />}

      {(stage === 'ocr_processing' || stage === 'resolving_market') && (
        <div className="processing-overlay">
          <div className="spinner"></div>
          <p>{stage === 'ocr_processing' ? 'Lendo nota fiscal...' : 'Identificando mercado...'}</p>
        </div>
      )}

      {stage === 'reviewing' && (
        <div className="result-container">
          <h3>Produtos Extraídos</h3>

          {!resolvedMarket && (
            <div className="market-selector">
              <label htmlFor="market-select">Não identifiquei o mercado pelo CNPJ. Selecione:</label>
              <select
                id="market-select"
                defaultValue=""
                onChange={(e) => {
                  const market = nearbyMarkets.find((m) => m.id === e.target.value);
                  setResolvedMarket(market ?? null);
                }}
              >
                <option value="" disabled>Escolha um mercado</option>
                {nearbyMarkets.map((market) => (
                  <option key={market.id} value={market.id}>{market.name}</option>
                ))}
              </select>
            </div>
          )}

          {resolvedMarket && <p className="resolved-market">Mercado: {resolvedMarket.name}</p>}

          {items.length === 0 && <p>Nenhum item reconhecido. Tente uma foto mais nítida.</p>}

          <ul className="extracted-items">
            {items.map((item, index) => (
              <li key={index} className="extracted-item review-item">
                <input
                  type="checkbox"
                  checked={item.include}
                  onChange={(e) => updateItem(index, { include: e.target.checked })}
                />
                <input
                  type="text"
                  value={item.description}
                  onChange={(e) => updateItem(index, { description: e.target.value })}
                />
                <input
                  type="number"
                  step="0.01"
                  value={item.price}
                  onChange={(e) => updateItem(index, { price: parseFloat(e.target.value) || 0 })}
                />
              </li>
            ))}
          </ul>

          <button
            className="btn-confirm"
            onClick={handleSubmit}
            disabled={!resolvedMarket || items.every((item) => !item.include)}
          >
            Confirmar e Enviar
          </button>
        </div>
      )}

      {stage === 'submitting' && (
        <div className="processing-overlay">
          <div className="spinner"></div>
          <p>Enviando nota fiscal...</p>
        </div>
      )}

      {stage === 'done' && result && (
        <div className="result-container">
          <h3>Nota fiscal processada!</h3>
          <p>{result.products_created} produto(s) novo(s) criado(s)</p>
          <p>{result.prices_created} preço(s) registrado(s)</p>
          <button className="btn-primary" onClick={reset}>Escanear outra nota</button>
        </div>
      )}

      {stage === 'error' && (
        <div className="result-container">
          <p className="error-message">{errorMessage}</p>
          <button className="btn-secondary" onClick={reset}>Tentar novamente</button>
        </div>
      )}
    </div>
  );
};
```

- [ ] **Step 3: Add styles for the review UI**

Append to `frontend/src/App.css`, after the `.btn-confirm` rule block (end of the "Scan Page" section):

```css

.market-selector {
  margin-bottom: 16px;
}

.market-selector label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #666;
}

.market-selector select {
  width: 100%;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  font-size: 14px;
}

.resolved-market {
  font-weight: 600;
  margin-bottom: 12px;
}

.review-item {
  gap: 8px;
}

.review-item input[type="text"] {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 6px;
}

.review-item input[type="number"] {
  width: 80px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 6px;
}

.error-message {
  color: #c62828;
  margin-bottom: 12px;
}
```

- [ ] **Step 4: Verify the frontend builds**

```bash
cd frontend
npm run build
```

Expected: build succeeds with no TypeScript errors.

- [ ] **Step 5: Manually verify the full pipeline in a real browser**

This is the real test of this entire plan and cannot be automated — do it yourself, with both frontend (`npm run dev`) and backend (`uvicorn app.main:app --reload --port 8000`) running:

1. **Create a reliable test image first.** Photographing a real paper receipt is the realistic end goal, but printed thermal-paper OCR is unreliable and hard to reproduce. For a first pass, create a `.txt` file with this exact content, open it in Notepad, zoom in (Ctrl+Plus) until the text is large and crisp, and take a screenshot (Win+Shift+S) saved as a `.png`:
   ```
   SUPERMERCADO EXEMPLO LTDA
   CNPJ: 45.543.915/0001-81
   001 LEITE INTEGRAL PIRACANJUBA 1L UN 4,99
   002 ARROZ TIO JOAO 5KG UN 25,90
   TOTAL R$ 30,89
   DATA: 05/07/2026
   ```
   (This mirrors the fixture in `ocr.test.ts`, and the CNPJ matches the seeded Carrefour Ribeirão market, so you can verify automatic market resolution.)
2. Open `http://localhost:3000/preco-perto/scan`, allow location access if prompted.
3. Click "🖼️ Selecionar Arquivo" and choose the screenshot from step 1.
4. Expected: "Lendo nota fiscal..." spinner appears (this is Tesseract.js downloading the Portuguese language pack on first use — can take 10-30s depending on your connection — then running recognition).
5. Expected next: "Identificando mercado..." briefly, then the review screen appears showing "Mercado: Carrefour Ribeirão" (no manual selector, since the CNPJ matched) and a list with two editable items (Leite Integral..., Arroz Tio João...) with checkboxes and price fields.
6. If OCR misread something (expected with imperfect recognition), edit the description/price fields directly, or uncheck an item to exclude it.
7. Click "Confirmar e Enviar". Expected: "Enviando nota fiscal..." briefly, then "Nota fiscal processada!" with counts of products/prices created.
8. Open the Network tab in DevTools during this flow to confirm: a request to `/api/v1/markets/by-cnpj`, then a `multipart/form-data` POST to `/api/v1/receipts/` returning `200`.
9. **Then try a real photographed paper receipt** with the live camera ("📷 Abrir Câmera" → "Capturar") to see real-world OCR quality — expect it to be rougher, and use the review screen's edit fields to correct it before confirming.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/services/api.ts frontend/src/pages/Scan.tsx frontend/src/App.css
git commit -m "feat: wire OCR extraction, market resolution and review UI into the Scan page"
```
