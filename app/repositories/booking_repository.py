
"""Операции чтения и блокировки бронирований в базе данных."""

import datetime
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import models


async def get_valid_time_window(
        session: AsyncSession,
        room_id: int,
        time_window_id: int
) -> models.TimeWindow | None:
    """Проверяет существование слота в активной комнате.

    Возвращает временной слот, если он принадлежит указанной
    активной комнате, иначе None.
    """

    query = (
        select(models.TimeWindow)
        .join(
            models.Room,
            models.Room.id == models.TimeWindow.room_id
        )
        .where(
            models.TimeWindow.id == time_window_id,
            models.TimeWindow.room_id == room_id,
            models.Room.is_active.is_(True)
        )
    )

    return await session.scalar(query)


async def get_all_bookings(
        session: AsyncSession,
        date: datetime.date | None = None
) -> Sequence[models.Booking]:
    """Возвращает все бронирования с возможной фильтрацией по дате."""

    query = (
        select(models.Booking)
        .options(
            selectinload(models.Booking.owner),
            selectinload(models.Booking.room),
            selectinload(models.Booking.time_window),
            selectinload(models.Booking.cancelled_by),
        )
    )

    if date is not None:
        query = query.where(models.Booking.date == date)

    result = await session.execute(query)

    return result.scalars().unique().all()


async def get_user_bookings(
        session: AsyncSession,
        user_id: int
) -> Sequence[models.Booking]:
    """Возвращает все бронирования указанного пользователя."""

    query = (
        select(models.Booking)
        .where(models.Booking.owner_id == user_id)
        .options(
            selectinload(models.Booking.owner),
            selectinload(models.Booking.room),
            selectinload(models.Booking.time_window),
            selectinload(models.Booking.cancelled_by),
        )
    )

    result = await session.execute(query)

    return result.scalars().unique().all()


async def lock_booking_for_update(
        session: AsyncSession,
        booking_id: int
) -> None:
    """Блокирует строку бронирования до завершения транзакции.

    Использует SELECT FOR UPDATE для последовательного
    выполнения конкурентных операций отмены.
    """

    await session.execute(
        select(models.Booking.id)
        .where(models.Booking.id == booking_id)
        .with_for_update()
    )
