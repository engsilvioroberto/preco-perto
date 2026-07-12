from .base import Base
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    market_id = Column(Integer, ForeignKey("markets.id"))
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")
    market = relationship("Market")
