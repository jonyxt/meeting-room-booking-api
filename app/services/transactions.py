from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


ModelType = TypeVar("ModelType")


async def commit_refresh_db(
    model: ModelType,
    error: str,
    session: AsyncSession,
) -> ModelType:
    """Сохраняет транзакцию и обновляет ORM-объект."""

    try:
        await session.commit()

    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error,
        ) from exc

    await session.refresh(model)
    return model
