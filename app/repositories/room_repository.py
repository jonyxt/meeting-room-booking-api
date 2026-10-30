
"""Операции чтения переговорных комнат и временных слотов."""

import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models


async def get_all_rooms(
        session: AsyncSession
):
    """Возвращает все переговорные комнаты."""

    query = select(models.Room)
    result = await session.execute(query)

    return result.scalars().unique().all()


async def get_available_room_windows(
        session: AsyncSession,
        date: datetime.date
):
    """Возвращает комнаты и свободные временные слоты на дату.

    Исключает слоты, занятые активными бронированиями.
    Неактивные комнаты не включаются в результат.
    """

    occupied_query = (
        select(models.Booking.id)
        .where(
            and_(
                models.Booking.room_id == models.Room.id,
                models.Booking.time_window_id == models.TimeWindow.id,
                models.Booking.date == date,
                models.Booking.is_active.is_(True)
            )
        )
        .exists()
    )

    query = (
        select(models.Room, models.TimeWindow)
        .join(
            models.TimeWindow,
            models.TimeWindow.room_id == models.Room.id
        )
        .where(
            models.Room.is_active.is_(True),
            ~occupied_query
        )
        .order_by(
            models.Room.id,
            models.TimeWindow.start_time
        )
    )

    result = await session.execute(query)

    return result.all()
