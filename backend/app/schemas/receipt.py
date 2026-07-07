from decimal import Decimal
from pydantic import BaseModel


class ReceiptItemIn(BaseModel):
    description: str
    price: Decimal


class ReceiptUploadResponse(BaseModel):
    receipt_id: str
    products_created: int
    prices_created: int
