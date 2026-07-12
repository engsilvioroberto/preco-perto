from .base import Base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

class Market(Base):
    __tablename__ = "markets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
