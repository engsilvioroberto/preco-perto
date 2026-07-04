
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from typing import Optional

router = APIRouter()

@router.post("/")
async def upload_receipt(
    image: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload e processar nota fiscal"""
    # TODO: Implement receipt upload and OCR processing
    return {
        "receipt_id": "placeholder",
        "status": "processing",
        "message": "Nota fiscal enviada para processamento"
    }
