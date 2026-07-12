from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.receipt import Receipt, ReceiptItem
from app.models.user import User
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/")
async def upload_receipt(
    image: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload and process a receipt"""
    # TODO: Implement actual OCR processing
    # For now, just create a placeholder receipt
    
    receipt_id = str(uuid.uuid4())
    
    # Save image (placeholder - in production, upload to storage)
    image_url = f"/uploads/{receipt_id}.jpg"
    
    receipt = Receipt(
        id=receipt_id,
        user_id="placeholder-user-id",  # TODO: Get from auth
        image_url=image_url,
        status="processing",
        user_latitude=latitude,
        user_longitude=longitude
    )
    
    db.add(receipt)
    db.commit()
    
    return {
        "receipt_id": receipt_id,
        "status": "processing",
        "message": "Nota fiscal enviada para processamento"
    }


@router.get("/{receipt_id}")
def get_receipt(receipt_id: str, db: Session = Depends(get_db)):
    """Get receipt status and results"""
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    items = db.query(ReceiptItem).filter(ReceiptItem.receipt_id == receipt_id).all()
    
    return {
        "id": receipt.id,
        "status": receipt.status,
        "market_id": receipt.market_id,
        "total_value": receipt.total_value,
        "receipt_date": receipt.receipt_date.isoformat() if receipt.receipt_date else None,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "confidence": item.confidence,
                "is_confirmed": item.is_confirmed
            }
            for item in items
        ]
    }
