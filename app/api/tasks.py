from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import async_session
from app.services.delivery_service import DeliveryService
from app.core.logging import logger
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/задачи", tags=["Задачи"])

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/рассчитать-доставку", summary="Ручной запуск расчёта стоимости доставки")
async def рассчитать_доставку(db: AsyncSession = Depends(get_db)):
    try:
        delivery_service = DeliveryService(db)
        processed_count = await delivery_service.process_uncalculated_parcels()
        logger.info("Ручной запуск задачи расчёта стоимости доставки")
        return {
            "detail": "Задача на расчёт стоимости доставки запущена",
            "processed_count": processed_count
        }
    except Exception as e:
        logger.error(f"Ошибка при запуске задачи: {e}")
        return JSONResponse(status_code=400, content={"detail": "Ошибка запуска задачи"}) 