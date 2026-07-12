import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Receipt(Base):
    __tablename__ = "receipts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    market_id = Column(String, ForeignKey("markets.id"))
    image_url = Column(Text, nullable=False)
    ocr_text = Column(Text)
    cnpj_extracted = Column(String)
    total_value = Column(Float)
    receipt_date = Column(DateTime)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    user_latitude = Column(Float)
    user_longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="receipts")
    market = relationship("Market", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")


class ReceiptItem(Base):
    __tablename__ = "receipt_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    receipt_id = Column(String, ForeignKey("receipts.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"))
    description = Column(Text, nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    confidence = Column(Float)
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    receipt = relationship("Receipt", back_populates="items")
    product = relationship("Product", back_populates="receipt_items")
