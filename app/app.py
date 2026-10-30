
"""Создание FastAPI-приложения и регистрация маршрутов."""

from fastapi import FastAPI

from .lifespan import lifespan
from .routers.auth import router as auth_router
from .routers.bookings import router as bookings_router
from .routers.health import router as health_router
from .routers.rooms import router as rooms_router
from .routers.users import router as users_router

app = FastAPI(
    title="Meeting Room Booking API",
    description=(
        "REST API для бронирования переговорных комнат.\n\n"
        "Сотрудники могут просматривать доступные временные слоты, "
        "создавать и отменять бронирования. Администраторы "
        "управляют пользователями и имеют доступ ко всем бронированиям.\n\n"
        "Для защищённых маршрутов используется JWT Bearer-токен. "
        "Получить его можно через `POST /login`, затем указать "
        "в окне **Authorize**."
    ),
    version="0.9.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Регистрация сотрудников и получение JWT-токена.",
        },
        {
            "name": "Users",
            "description": "Профили пользователей и управление ролями.",
        },
        {
            "name": "Rooms",
            "description": "Переговорные комнаты и свободные временные слоты.",
        },
        {
            "name": "Bookings",
            "description": "Создание, просмотр и отмена бронирований.",
        },
        {
            "name": "Health",
            "description": "Проверка доступности приложения и PostgreSQL.",
        },
    ],
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(health_router)
