from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.api import parcel_router, parcel_type_router, tasks_router

app = FastAPI(
    title="Служба международной доставки",
    description="API для регистрации и отслеживания международных посылок. Все ручки и ответы на русском языке.",
    version="1.0.0",
    contact={
        "name": "Служба поддержки",
        "email": "support@deliveryservice.ru"
    }
)

# Добавляем middleware для сессий
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# Импортируем и подключаем роуты (будут добавлены позже)
app.include_router(parcel_router)
app.include_router(parcel_type_router)
app.include_router(tasks_router)

@app.get("/")
def root():
    return {"message": "International Delivery Service API"} 