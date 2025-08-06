from pydantic import BaseModel, Field

class ParcelTypeBase(BaseModel):
    name: str

class ParcelTypeCreate(ParcelTypeBase):
    pass

class ParcelTypeRead(ParcelTypeBase):
    id: int = Field(..., description="ID типа посылки")

    class Config:
        orm_mode = True 