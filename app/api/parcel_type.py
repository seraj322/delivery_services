from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import async_session
from app.models.parcel_type import ParcelType
from app.schemas.parcel_type import ParcelTypeRead
from typing import List
from app.core.logging import logger
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings

router = APIRouter(prefix="/типы-посылок", tags=["Типы посылок"])

async def get_db():
    async with async_session() as session:
        yield session

@router.get("/", response_model=List[ParcelTypeRead], summary="Получить все типы посылок")
async def получить_типы_посылок(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            ParcelType.__table__.select()
        )
        types = result.fetchall()
        logger.info(f"Получено типов посылок: {len(types)}")
        return types
    except Exception as e:
        logger.error(f"Ошибка при получении типов посылок: {e}")
        return JSONResponse(status_code=400, content={"detail": "Ошибка получения типов посылок"}) 