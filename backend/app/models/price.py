
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Date
from app.core.database import Base, GUID


class Price(Base):
    __tablename__ = "prices"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    product_id = Column(GUID, nullable=False, index=True)
    market_id = Column(GUID, nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)
    is_promotion = Column(Boolean, default=False)
    promotion_ends_at = Column(Date, nullable=True)
    source = Column(String(50), nullable=False)
    source_id = Column(GUID, nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(GUID, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
