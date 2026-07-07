import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Text, DateTime, Numeric, Boolean, ForeignKey
from app.core.database import Base, GUID


class OfferFlyerItem(Base):
    __tablename__ = "offer_flyer_items"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    offer_flyer_id = Column(GUID, ForeignKey("offer_flyers.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=True, index=True)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)
    unit = Column(String(50), nullable=True)
    confidence = Column(Numeric(5, 2), nullable=True)
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
