from fastapi import APIRouter
from app.tasks.worker import celery_app
from app.core.logging import logger
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/задачи", tags=["Задачи"])

@router.post("/рассчитать-доставку", summary="Ручной запуск расчёта стоимости доставки")
async def рассчитать_доставку():
    try:
        celery_app.send_task("app.tasks.delivery.рассчитать_стоимость_доставки")
        logger.info("Ручной запуск задачи расчёта стоимости доставки")
        return {"detail": "Задача на расчёт стоимости доставки запущена"}
    except Exception as e:
        logger.error(f"Ошибка при запуске задачи: {e}")
        return JSONResponse(status_code=400, content={"detail": "Ошибка запуска задачи"}) 