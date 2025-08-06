from pydantic import BaseModel, Field
from typing import Optional

class ParcelBase(BaseModel):
    name: str = Field(..., example="T-shirt")
    weight: float = Field(..., gt=0, example=1.2)
    type_id: int = Field(..., example=1)
    value_usd: float = Field(..., gt=0, example=100.0)

class ParcelCreate(ParcelBase):
    pass

class ParcelRead(ParcelBase):
    id: int
    delivery_price_rub: Optional[float] = Field(None, description="Стоимость доставки в рублях или 'Не рассчитано'")
    type_name: str = Field(..., description="Название типа посылки")

    class Config:
        orm_mode = True

class ParcelFilter(BaseModel):
    type_id: Optional[int] = None
    has_delivery_price: Optional[bool] = None
    page: int = 1
    page_size: int = 10 