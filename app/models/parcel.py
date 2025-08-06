from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.models.base import Base

class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    weight = Column(Float, nullable=False)
    type_id = Column(Integer, ForeignKey("parcel_types.id"), nullable=False)
    value_usd = Column(Numeric(10, 2), nullable=False)
    delivery_price_rub = Column(Numeric(12, 2), nullable=True)
    session_id = Column(String(128), index=True, nullable=False)

    type = relationship("ParcelType") 