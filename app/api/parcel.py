from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.base import async_session
from app.models.parcel import Parcel
from app.models.parcel_type import ParcelType
from app.schemas.parcel import ParcelCreate, ParcelRead, ParcelFilter
from typing import List, Optional
from app.core.logging import logger
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/посылки", tags=["Посылки"])

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/", response_model=dict, summary="Зарегистрировать посылку")
async def зарегистрировать_посылку(
    parcel: ParcelCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        session_id = request.session.get("session_id")
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            request.session["session_id"] = session_id
        db_parcel = Parcel(
            name=parcel.name,
            weight=parcel.weight,
            type_id=parcel.type_id,
            value_usd=parcel.value_usd,
            session_id=session_id
        )
        db.add(db_parcel)
        await db.commit()
        await db.refresh(db_parcel)
        logger.info(f"Посылка зарегистрирована: id={db_parcel.id}, session={session_id}")
        return {"id": db_parcel.id}
    except Exception as e:
        logger.error(f"Ошибка при регистрации посылки: {e}")
        return JSONResponse(status_code=400, content={"detail": "Ошибка регистрации посылки"})

@router.get("/", response_model=List[ParcelRead], summary="Получить список своих посылок")
async def получить_посылки(
    request: Request,
    db: AsyncSession = Depends(get_db),
    type_id: Optional[int] = Query(None, description="Фильтр по типу посылки"),
    has_delivery_price: Optional[bool] = Query(None, description="Только с рассчитанной стоимостью доставки"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    try:
        session_id = request.session.get("session_id")
        if not session_id:
            return []
        query = select(Parcel).where(Parcel.session_id == session_id)
        if type_id:
            query = query.where(Parcel.type_id == type_id)
        if has_delivery_price is not None:
            if has_delivery_price:
                query = query.where(Parcel.delivery_price_rub.isnot(None))
            else:
                query = query.where(Parcel.delivery_price_rub.is_(None))
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        parcels = result.scalars().all()
        # Получаем имена типов
        type_ids = {p.type_id for p in parcels}
        types = await db.execute(select(ParcelType).where(ParcelType.id.in_(type_ids)))
        type_map = {t.id: t.name for t in types.scalars().all()}
        logger.info(f"Получен список посылок для session={session_id}, count={len(parcels)}")
        return [ParcelRead(
            id=p.id,
            name=p.name,
            weight=p.weight,
            type_id=p.type_id,
            value_usd=float(p.value_usd),
            delivery_price_rub=float(p.delivery_price_rub) if p.delivery_price_rub is not None else None,
            type_name=type_map.get(p.type_id, "Неизвестно")
        ) for p in parcels]
    except Exception as e:
        logger.error(f"Ошибка при получении списка посылок: {e}")
        return JSONResponse(status_code=400, content={"detail": "Ошибка получения списка посылок"})

@router.get("/{id}", response_model=ParcelRead, summary="Получить данные о посылке по id")
async def получить_посылку(
    id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        session_id = request.session.get("session_id")
        if not session_id:
            raise HTTPException(status_code=404, detail="Посылка не найдена")
        parcel = await db.get(Parcel, id)
        if not parcel or parcel.session_id != session_id:
            raise HTTPException(status_code=404, detail="Посылка не найдена")
        type_obj = await db.get(ParcelType, parcel.type_id)
        logger.info(f"Получены данные о посылке id={id} для session={session_id}")
        return ParcelRead(
            id=parcel.id,
            name=parcel.name,
            weight=parcel.weight,
            type_id=parcel.type_id,
            value_usd=float(parcel.value_usd),
            delivery_price_rub=float(parcel.delivery_price_rub) if parcel.delivery_price_rub is not None else None,
            type_name=type_obj.name if type_obj else "Неизвестно"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении посылки: {e}")
        return JSONResponse(status_code=400, content={"detail": "Ошибка получения посылки"}) 