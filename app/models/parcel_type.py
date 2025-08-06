from sqlalchemy import Column, Integer, String
from app.models.base import Base

class ParcelType(Base):
    __tablename__ = "parcel_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False) 