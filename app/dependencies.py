"""Зависимости FastAPI.

Модуль содержит dependency-функции, которые используются
в обработчиках маршрутов для получения общих ресурсов приложения.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Предоставляет асинхронную сессию базы данных для одного запроса.

    Сессия создаётся через AsyncSessionLocal и автоматически закрывается
    после завершения обработки запроса.
    """
    async with AsyncSessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
