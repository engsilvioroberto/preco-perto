
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Text, JSON
from app.core.database import Base, GUID


class Market(Base):
    __tablename__ = "markets"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(18), nullable=True)
    address = Column(Text, nullable=False)
    neighborhood = Column(String(255), nullable=True)
    city = Column(String(255), default="Ribeirão Preto")
    state = Column(String(2), default="SP")
    zipcode = Column(String(10), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    opening_hours = Column(JSON, nullable=True)
    categories = Column(JSON, nullable=True)
    phone = Column(String(20), nullable=True)
    created_by = Column(GUID, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
