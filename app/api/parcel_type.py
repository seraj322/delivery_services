from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import async_session
from app.schemas.parcel_type import ParcelTypeRead
from app.services.parcel_type_service import ParcelTypeService
from app.core.logging import logger
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter(prefix="/типы-посылок", tags=["Типы посылок"])

async def get_db():
    async with async_session() as session:
        yield session

@router.get("/", response_model=List[ParcelTypeRead], summary="Получить все типы посылок")
async def получить_типы_посылок(db: AsyncSession = Depends(get_db)):
    try:
        parcel_type_service = ParcelTypeService(db)
        return await parcel_type_service.get_all_types()
    except Exception as e:
        logger.error(f"Ошибка при получении типов посылок: {e}")
        return JSONResponse(status_code=400, content={"detail": "Ошибка получения типов посылок"}) 