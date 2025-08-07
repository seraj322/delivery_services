from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.parcel import Parcel
from app.models.parcel_type import ParcelType
from app.schemas.parcel import ParcelCreate, ParcelRead
from app.crud.parcel import ParcelCRUD
from app.crud.parcel_type import ParcelTypeCRUD
from app.core.logging import logger
import uuid

class ParcelService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.parcel_crud = ParcelCRUD(db)
        self.parcel_type_crud = ParcelTypeCRUD(db)

    async def register_parcel(self, parcel_data: ParcelCreate, session_id: str) -> dict:
        """Регистрация новой посылки"""
        try:
            parcel_id = await self.parcel_crud.create_parcel(parcel_data, session_id)
            logger.info(f"Посылка зарегистрирована: id={parcel_id}, session={session_id}")
            return {"id": parcel_id}
        except Exception as e:
            logger.error(f"Ошибка при регистрации посылки: {e}")
            raise

    async def get_user_parcels(
        self, 
        session_id: str, 
        type_id: Optional[int] = None,
        has_delivery_price: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> List[ParcelRead]:
        """Получение списка посылок пользователя с фильтрацией и пагинацией"""
        try:
            parcels = await self.parcel_crud.get_user_parcels(
                session_id, type_id, has_delivery_price, page, page_size
            )
            
            # Получаем имена типов
            type_ids = {p.type_id for p in parcels}
            types = await self.parcel_type_crud.get_types_by_ids(type_ids)
            type_map = {t.id: t.name for t in types}
            
            result = []
            for p in parcels:
                result.append(ParcelRead(
                    id=p.id,
                    name=p.name,
                    weight=p.weight,
                    type_id=p.type_id,
                    value_usd=float(p.value_usd),
                    delivery_price_rub=float(p.delivery_price_rub) if p.delivery_price_rub is not None else None,
                    type_name=type_map.get(p.type_id, "Неизвестно")
                ))
            
            logger.info(f"Получен список посылок для session={session_id}, count={len(result)}")
            return result
        except Exception as e:
            logger.error(f"Ошибка при получении списка посылок: {e}")
            raise

    async def get_parcel_by_id(self, parcel_id: int, session_id: str) -> ParcelRead:
        """Получение посылки по ID с проверкой принадлежности пользователю"""
        try:
            parcel = await self.parcel_crud.get_parcel_by_id(parcel_id, session_id)
            if not parcel:
                raise ValueError("Посылка не найдена")
            
            type_obj = await self.parcel_type_crud.get_type_by_id(parcel.type_id)
            
            result = ParcelRead(
                id=parcel.id,
                name=parcel.name,
                weight=parcel.weight,
                type_id=parcel.type_id,
                value_usd=float(parcel.value_usd),
                delivery_price_rub=float(parcel.delivery_price_rub) if parcel.delivery_price_rub is not None else None,
                type_name=type_obj.name if type_obj else "Неизвестно"
            )
            
            logger.info(f"Получены данные о посылке id={parcel_id} для session={session_id}")
            return result
        except Exception as e:
            logger.error(f"Ошибка при получении посылки: {e}")
            raise

    def generate_session_id(self) -> str:
        """Генерация нового session_id"""
        return str(uuid.uuid4()) 