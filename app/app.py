"""Точка входа FastAPI-приложения.

Создаёт экземпляр приложения, подключает жизненный цикл
и регистрирует HTTP-маршруты.
"""

from fastapi import FastAPI

from .lifespan import lifespan
from .routers.auth import router as auth_router
from .routers.users import router as users_router
from .routers.bookings import router as bookings_router
from .routers.rooms import router as rooms_router


app = FastAPI(
    title='Booking service',
    description='Тестовое задание по бронированию конференц залов',
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(bookings_router)
app.include_router(rooms_router)
