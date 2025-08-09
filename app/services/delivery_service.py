from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parcel import Parcel
from app.crud.parcel import ParcelCRUD
from app.core.logging import logger
import httpx
import redis.asyncio as aioredis
from app.core.config import settings

REDIS_KEY = "usd_rub_rate"

class DeliveryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.parcel_crud = ParcelCRUD(db)

    async def fetch_usd_rub_rate(self) -> float:
        """Получение курса доллара к рублю с кэшированием в Redis"""
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

    async def calculate_delivery_price(self, weight: float, value_usd: float) -> float:
        """Расчет стоимости доставки по формуле"""
        usd_rub = await self.fetch_usd_rub_rate()
        return (weight * 0.5 + value_usd * 0.01) * usd_rub

    async def process_uncalculated_parcels(self) -> int:
        """Обработка всех посылок без рассчитанной стоимости доставки"""
        try:
            parcels = await self.parcel_crud.get_uncalculated_parcels()
            if not parcels:
                logger.info("Нет посылок для расчёта стоимости доставки")
                return 0
            
            processed_count = 0
            for parcel in parcels:
                price = await self.calculate_delivery_price(
                    float(parcel.weight), 
                    float(parcel.value_usd)
                )
                await self.parcel_crud.update_delivery_price(parcel.id, price)
                logger.info(f"Стоимость доставки рассчитана для посылки id={parcel.id}")
                processed_count += 1
            
            logger.info(f"Рассчитано {processed_count} посылок")
            return processed_count
        except Exception as e:
            logger.error(f"Ошибка при расчете стоимости доставки: {e}")
            raise 