import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=True)
    image_url = Column(Text, nullable=False)
    ocr_text = Column(Text, nullable=True)
    cnpj_extracted = Column(String(18), nullable=True)
    total_value = Column(Numeric(10, 2), nullable=True)
    receipt_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="pending")  # "pending", "processing", "completed", "failed"
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
