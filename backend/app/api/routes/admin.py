import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.market import Market
from app.models.product import Product
from app.models.price import Price
from app.models.offer_flyer import OfferFlyer
from app.models.offer_flyer_item import OfferFlyerItem
from app.models.user import User
from app.schemas.offer_flyer import (
    OfferFlyerUploadResponse,
    OfferFlyerDetailResponse,
    OfferFlyerItemOut,
    OfferFlyerConfirmIn,
    OfferFlyerConfirmResponse,
    OfferFlyerItemConfirm,
)
from app.services.ocr import extract_text_from_image, parse_offer_flyer
from app.services.product_normalization import normalize_product, fuzzy_match
import asyncio

router = APIRouter()

FUZZY_MATCH_THRESHOLD = 85.0
UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads" / "offer-flyers"


@router.post("/offer-flyers", response_model=OfferFlyerUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_offer_flyer(
    image: UploadFile = File(...),
    market_id: str = Form(...),
    valid_from: str = Form(...),
    valid_until: str = Form(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Upload de jornal de ofertas com OCR server-side e extração de itens."""
    market_result = await db.execute(select(Market).where(Market.id == market_id))
    market = market_result.scalar_one_or_none()
    if not market:
        raise HTTPException(status_code=404, detail="Mercado não encontrado")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    image_id = uuid.uuid4()
    extension = Path(image.filename or "").suffix or ".jpg"
    image_path = UPLOAD_DIR / f"{image_id}{extension}"
    image_bytes = await image.read()
    image_path.write_bytes(image_bytes)

    try:
        ocr_text = await asyncio.to_thread(extract_text_from_image, str(image_path))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no processamento OCR: {str(exc)}",
        )

    raw_items = parse_offer_flyer(ocr_text)

    now = datetime.utcnow()
    flyer = OfferFlyer(
        id=uuid.uuid4(),
        admin_id=admin.id,
        market_id=market.id,
        image_url=f"/uploads/offer-flyers/{image_id}{extension}",
        ocr_text=ocr_text if ocr_text else None,
        valid_from=datetime.strptime(valid_from, "%Y-%m-%d").date(),
        valid_until=datetime.strptime(valid_until, "%Y-%m-%d").date(),
        status="completed",
        created_at=now,
        updated_at=now,
    )
    db.add(flyer)

    result = await db.execute(select(Product))
    existing_products = list(result.scalars().all())

    items_out = []
    for item in raw_items:
        matched_product = None
        best_score = 0.0
        for product in existing_products:
            score = fuzzy_match(item["description"], product.name)
            if score >= FUZZY_MATCH_THRESHOLD and score > best_score:
                matched_product = product
                best_score = score

        product_id = matched_product.id if matched_product else None

        flyer_item = OfferFlyerItem(
            id=uuid.uuid4(),
            offer_flyer_id=flyer.id,
            product_id=product_id,
            description=item["description"],
            price=item["price"],
            original_price=item.get("original_price"),
            confidence=item.get("confidence"),
            is_confirmed=False,
            created_at=now,
        )
        db.add(flyer_item)

        items_out.append(OfferFlyerItemOut(
            id=flyer_item.id,
            product_id=product_id,
            product_name=matched_product.name if matched_product else None,
            description=item["description"],
            price=float(item["price"]),
            original_price=float(item["original_price"]) if item.get("original_price") else None,
            confidence=float(item["confidence"]) if item.get("confidence") else None,
            is_confirmed=False,
        ))

    await db.commit()

    return OfferFlyerUploadResponse(
        offer_flyer_id=flyer.id,
        status="completed",
        items=items_out,
        total_items=len(items_out),
    )


@router.get("/offer-flyers/{offer_flyer_id}", response_model=OfferFlyerDetailResponse)
async def get_offer_flyer(
    offer_flyer_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Obter detalhes do jornal de ofertas com itens extraídos."""
    result = await db.execute(select(OfferFlyer).where(OfferFlyer.id == offer_flyer_id))
    flyer = result.scalar_one_or_none()
    if not flyer:
        raise HTTPException(status_code=404, detail="Jornal de ofertas não encontrado")

    market_result = await db.execute(select(Market).where(Market.id == flyer.market_id))
    market = market_result.scalar_one_or_none()

    items_result = await db.execute(
        select(OfferFlyerItem)
        .where(OfferFlyerItem.offer_flyer_id == flyer.id)
        .order_by(OfferFlyerItem.created_at)
    )
    items = items_result.scalars().all()

    items_out = []
    confirmed = 0
    for item in items:
        product_name = None
        if item.product_id:
            prod_result = await db.execute(select(Product).where(Product.id == item.product_id))
            prod = prod_result.scalar_one_or_none()
            if prod:
                product_name = prod.name

        items_out.append(OfferFlyerItemOut(
            id=item.id,
            product_id=item.product_id,
            product_name=product_name,
            description=item.description,
            price=float(item.price),
            original_price=float(item.original_price) if item.original_price else None,
            confidence=float(item.confidence) if item.confidence else None,
            is_confirmed=item.is_confirmed,
        ))
        if item.is_confirmed:
            confirmed += 1

    return OfferFlyerDetailResponse(
        id=flyer.id,
        status=flyer.status,
        market_id=flyer.market_id,
        market_name=market.name if market else None,
        valid_from=flyer.valid_from,
        valid_until=flyer.valid_until,
        items=items_out,
        total_items=len(items_out),
        confirmed_items=confirmed,
        pending_review=len(items_out) - confirmed,
    )


@router.patch("/offer-flyers/{offer_flyer_id}/items", response_model=OfferFlyerConfirmResponse)
async def confirm_offer_flyer_items(
    offer_flyer_id: str,
    confirm_data: OfferFlyerConfirmIn,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Confirmar itens do jornal de ofertas e criar registros de preço."""
    result = await db.execute(select(OfferFlyer).where(OfferFlyer.id == offer_flyer_id))
    flyer = result.scalar_one_or_none()
    if not flyer:
        raise HTTPException(status_code=404, detail="Jornal de ofertas não encontrado")

    now = datetime.utcnow()
    prices_added = 0
    confirmed_items = 0

    for confirm_item in confirm_data.items:
        item_result = await db.execute(
            select(OfferFlyerItem)
            .where(
                OfferFlyerItem.id == confirm_item.item_id,
                OfferFlyerItem.offer_flyer_id == flyer.id,
            )
        )
        flyer_item = item_result.scalar_one_or_none()
        if not flyer_item:
            continue

        if confirm_item.is_confirmed and confirm_item.product_id:
            flyer_item.product_id = confirm_item.product_id
            flyer_item.is_confirmed = True

            # Check if price already exists for this product+market+captured_at
            existing_price = await db.execute(
                select(Price).where(
                    Price.product_id == confirm_item.product_id,
                    Price.market_id == flyer.market_id,
                    Price.captured_at == now,
                )
            )
            if existing_price.scalar_one_or_none():
                continue

            price = Price(
                id=uuid.uuid4(),
                product_id=confirm_item.product_id,
                market_id=flyer.market_id,
                price=flyer_item.price,
                original_price=flyer_item.original_price,
                is_promotion=flyer_item.original_price is not None,
                promotion_ends_at=flyer.valid_until,
                source="oferta_flyer",
                source_id=flyer.id,
                captured_at=now,
                expires_at=datetime.combine(flyer.valid_until, datetime.min.time()),
                created_by=admin.id,
                created_at=now,
                updated_at=now,
            )
            db.add(price)
            prices_added += 1
            confirmed_items += 1
        elif not confirm_item.is_confirmed:
            flyer_item.is_confirmed = False
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Item {confirm_item.item_id}: product_id é obrigatório para is_confirmed=True",
            )

    await db.commit()

    return OfferFlyerConfirmResponse(
        offer_flyer_id=flyer.id,
        status="completed",
        confirmed_items=confirmed_items,
        prices_added=prices_added,
        message=f"Jornal de ofertas confirmado. {prices_added} preços adicionados ao sistema.",
    )
