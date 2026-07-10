
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Float, ForeignKey
from app.core.database import Base, GUID


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    receipt_id = Column(GUID, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(GUID, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 3), default=Decimal("1"))
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    confidence = Column(Float, nullable=True)
    is_confirmed = Column(Boolean, default=True)
