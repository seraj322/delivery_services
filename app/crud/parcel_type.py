from typing import List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.parcel_type import ParcelType
from app.schemas.parcel_type import ParcelTypeRead

class ParcelTypeCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_types(self) -> List[ParcelTypeRead]:
        """Получение всех типов посылок"""
        result = await self.db.execute(select(ParcelType))
        types = result.scalars().all()
        return [ParcelTypeRead(id=t.id, name=t.name) for t in types]

    async def get_type_by_id(self, type_id: int) -> Optional[ParcelType]:
        """Получение типа посылки по ID"""
        result = await self.db.execute(select(ParcelType).where(ParcelType.id == type_id))
        return result.scalar_one_or_none()

    async def get_types_by_ids(self, type_ids: Set[int]) -> List[ParcelType]:
        """Получение типов посылок по списку ID"""
        if not type_ids:
            return []
        result = await self.db.execute(select(ParcelType).where(ParcelType.id.in_(type_ids)))
        return result.scalars().all() 