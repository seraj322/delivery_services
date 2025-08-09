from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import async_session
from app.schemas.parcel import ParcelCreate, ParcelRead
from app.services.parcel_service import ParcelService
from app.core.logging import logger
from fastapi.responses import JSONResponse
from typing import List, Optional

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
            parcel_service = ParcelService(db)
            session_id = parcel_service.generate_session_id()
            request.session["session_id"] = session_id
        
        parcel_service = ParcelService(db)
        return await parcel_service.register_parcel(parcel, session_id)
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
        
        parcel_service = ParcelService(db)
        return await parcel_service.get_user_parcels(
            session_id, type_id, has_delivery_price, page, page_size
        )
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
        
        parcel_service = ParcelService(db)
        return await parcel_service.get_parcel_by_id(id, session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Посылка не найдена")
    except Exception as e:
        logger.error(f"Ошибка при получении посылки: {e}")
        return JSONResponse(status_code=400, content={"detail": "Ошибка получения посылки"}) 