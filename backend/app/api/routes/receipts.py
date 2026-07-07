import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
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


@router.post("/", response_model=ReceiptUploadResponse, status_code=status.HTTP_201_CREATED)
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
            source="receipt",
            source_id=receipt.id,
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
