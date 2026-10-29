"""Сервис проверки готовности инфраструктурных зависимостей."""

import asyncio
import logging

from sqlalchemy import text

from ..database import engine


logger = logging.getLogger(__name__)

DATABASE_HEALTH_TIMEOUT_SECONDS = 2.0


async def check_database_ready() -> bool:
    """Проверяет доступность PostgreSQL.

    Возвращает True при успешном выполнении SELECT 1.
    При ошибке подключения или превышении таймаута
    возвращает False.
    """

    try:
        async with asyncio.timeout(
            DATABASE_HEALTH_TIMEOUT_SECONDS
        ):
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))

        return True

    except Exception as exc:
        logger.warning(
            "Database readiness check failed: %s",
            type(exc).__name__,
        )
        return False
