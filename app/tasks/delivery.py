from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.delivery_service import DeliveryService
from app.core.logging import logger
from asgiref.sync import async_to_sync

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@shared_task(name="app.tasks.delivery.рассчитать_стоимость_доставки")
def рассчитать_стоимость_доставки():
    logger.info("Запущена задача расчёта стоимости доставки")
    async_to_sync(_рассчитать_стоимость_доставки_async)()

async def _рассчитать_стоимость_доставки_async():
    async with async_session() as db:
        delivery_service = DeliveryService(db)
        await delivery_service.process_uncalculated_parcels() 