
"""Операции чтения пользователей из базы данных."""

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models


async def get_user_by_username(
        session: AsyncSession,
        username: str
) -> models.User | None:
    """Возвращает пользователя по имени или None."""

    query = select(models.User).where(
        models.User.username == username
    )

    return await session.scalar(query)


async def get_all_users(
        session: AsyncSession
) -> list[models.User]:
    """Возвращает список всех пользователей."""

    query = select(models.User)
    result = await session.execute(query)

    return result.scalars().unique().all()


async def count_admins(
        session: AsyncSession
) -> int:
    """Возвращает количество администраторов."""

    query = (
        select(func.count())
        .select_from(models.User)
        .where(models.User.role == models.UserRole.ADMIN)
    )

    return await session.scalar(query)

async def lock_admin_role_changes(
    session: AsyncSession,
) -> None:
    """Сериализует операции понижения администраторов."""

    await session.execute(
        text("SELECT pg_advisory_xact_lock(812741099)")
    )