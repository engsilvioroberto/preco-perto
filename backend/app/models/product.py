import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, UniqueConstraint
from app.core.database import Base, GUID


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("normalized_name", "brand", "unit", "quantity", name="uq_product_normalized"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    normalized_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    unit = Column(String(50), nullable=True)
    quantity = Column(Numeric(10, 3), nullable=True)
    brand = Column(String(255), nullable=True, index=True)
    barcode = Column(String(50), nullable=True, index=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
