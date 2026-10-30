
from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import common_repository

ModelType = TypeVar("ModelType")


async def get_db_object_by_id(
    session: AsyncSession,
    orm_model: type[ModelType],
    db_object_id: int,
) -> ModelType:
    """Возвращает ORM-объект по ID или выбрасывает HTTP 404."""

    db_object = await common_repository.get_by_id(
        session,
        orm_model,
        db_object_id,
    )

    if db_object is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{orm_model.__name__} с id {db_object_id} не найден",
        )

    return db_object
