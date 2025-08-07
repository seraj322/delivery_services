from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.parcel import Parcel
from app.schemas.parcel import ParcelCreate

class ParcelCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_parcel(self, parcel_data: ParcelCreate, session_id: str) -> int:
        """Создание новой посылки"""
        db_parcel = Parcel(
            name=parcel_data.name,
            weight=parcel_data.weight,
            type_id=parcel_data.type_id,
            value_usd=parcel_data.value_usd,
            session_id=session_id
        )
        self.db.add(db_parcel)
        await self.db.commit()
        await self.db.refresh(db_parcel)
        return db_parcel.id

    async def get_user_parcels(
        self, 
        session_id: str, 
        type_id: Optional[int] = None,
        has_delivery_price: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> List[Parcel]:
        """Получение посылок пользователя с фильтрацией и пагинацией"""
        query = select(Parcel).where(Parcel.session_id == session_id)
        
        if type_id:
            query = query.where(Parcel.type_id == type_id)
        
        if has_delivery_price is not None:
            if has_delivery_price:
                query = query.where(Parcel.delivery_price_rub.isnot(None))
            else:
                query = query.where(Parcel.delivery_price_rub.is_(None))
        
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_parcel_by_id(self, parcel_id: int, session_id: str) -> Optional[Parcel]:
        """Получение посылки по ID с проверкой принадлежности пользователю"""
        result = await self.db.execute(
            select(Parcel).where(Parcel.id == parcel_id, Parcel.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_uncalculated_parcels(self) -> List[Parcel]:
        """Получение всех посылок без рассчитанной стоимости доставки"""
        result = await self.db.execute(
            select(Parcel).where(Parcel.delivery_price_rub == None)
        )
        return result.scalars().all()

    async def update_delivery_price(self, parcel_id: int, price: float) -> None:
        """Обновление стоимости доставки для посылки"""
        await self.db.execute(
            Parcel.__table__.update().where(Parcel.id == parcel_id).values(delivery_price_rub=price)
        )
        await self.db.commit() 