
"""Общие операции чтения ORM-объектов из базы данных."""

from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


async def get_by_id(
        session: AsyncSession,
        orm_model: type[ModelType],
        db_object_id: int
) -> ModelType | None:
    """Возвращает ORM-объект по первичному ключу.

    Если объект не найден, возвращает None.
    """

    query = select(orm_model).where(
        orm_model.id == db_object_id
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()
