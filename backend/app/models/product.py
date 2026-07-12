from .base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    brand = Column(String)
    barcode = Column(String, unique=True, index=True)
