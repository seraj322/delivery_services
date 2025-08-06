from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.parcel import Parcel
from app.models.parcel_type import ParcelType
import httpx
import redis.asyncio as aioredis
import asyncio
from app.core.logging import logger
from asgiref.sync import async_to_sync

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

REDIS_KEY = "usd_rub_rate"

async def fetch_usd_rub_rate():
    redis_client = aioredis.from_url(settings.REDIS_URL)
    rate = await redis_client.get(REDIS_KEY)
    if rate:
        return float(rate)
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://www.cbr-xml-daily.ru/daily_json.js")
        resp.raise_for_status()
        data = resp.json()
        rate = float(data["Valute"]["USD"]["Value"])
        await redis_client.set(REDIS_KEY, rate, ex=60*10)  # 10 минут
        return rate

@shared_task(name="app.tasks.delivery.рассчитать_стоимость_доставки")
def рассчитать_стоимость_доставки():
    logger.info("Запущена задача расчёта стоимости доставки")
    async_to_sync(_рассчитать_стоимость_доставки_async)()

async def _рассчитать_стоимость_доставки_async():
    async with async_session() as db:
        # Получаем все посылки без рассчитанной стоимости
        result = await db.execute(
            Parcel.__table__.select().where(Parcel.delivery_price_rub == None)
        )
        parcels = result.fetchall()
        if not parcels:
            logger.info("Нет посылок для расчёта стоимости доставки")
            return
        usd_rub = await fetch_usd_rub_rate()
        for row in parcels:
            parcel = row
            price = (float(parcel.weight) * 0.5 + float(parcel.value_usd) * 0.01) * usd_rub
            await db.execute(
                Parcel.__table__.update().where(Parcel.id == parcel.id).values(delivery_price_rub=price)
            )
            logger.info(f"Стоимость доставки рассчитана для посылки id={parcel.id}")
        await db.commit()
        logger.info(f"Рассчитано {len(parcels)} посылок") 