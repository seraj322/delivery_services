from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parcel_type import ParcelType
from app.schemas.parcel_type import ParcelTypeRead
from app.crud.parcel_type import ParcelTypeCRUD
from app.core.logging import logger

class ParcelTypeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.parcel_type_crud = ParcelTypeCRUD(db)

    async def get_all_types(self) -> List[ParcelTypeRead]:
        """Получение всех типов посылок"""
        try:
            types = await self.parcel_type_crud.get_all_types()
            logger.info(f"Получено типов посылок: {len(types)}")
            return types
        except Exception as e:
            logger.error(f"Ошибка при получении типов посылок: {e}")
            raise 