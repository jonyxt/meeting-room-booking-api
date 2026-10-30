
"""Сервис управления бронированиями переговорных комнат."""

import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..repositories import booking_repository
from .object_lookup import get_db_object_by_id
from .transactions import commit_refresh_db


async def book_room(
        session: AsyncSession,
        current_user: models.User,
        booking_data: schemas.CreateBookingRequest
) -> models.Booking:
    """Создаёт бронирование с проверкой бизнес-правил."""

    if booking_data.date < datetime.date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя создать бронирование на прошедшую дату'
        )

    time_window = await booking_repository.get_valid_time_window(
        session,
        booking_data.room_id,
        booking_data.time_window_id
    )

    if time_window is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Комната не существует, неактивна или слот не принадлежит выбранной комнате'
        )

    new_booking = models.Booking(
        owner_id=current_user.id,
        room_id=booking_data.room_id,
        date=booking_data.date,
        time_window_id=booking_data.time_window_id
    )

    session.add(new_booking)

    return await commit_refresh_db(
        model=new_booking,
        error='Такая бронь уже существует',
        session=session
    )


async def book_room_info(
        session: AsyncSession,
        current_user: models.User,
        booking_id: int
) -> models.Booking:
    """Возвращает бронирование с проверкой прав доступа."""

    booking = await get_db_object_by_id(
        session, models.Booking, booking_id
    )

    if (
            current_user.role == models.UserRole.EMPLOYEE
            and current_user.id != booking.owner_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для просмотра брони'
        )

    return booking


async def get_all_bookings(
        session: AsyncSession,
        date: datetime.date | None = None
) -> dict:
    """Возвращает все бронирования с возможной фильтрацией по дате."""

    bookings = await booking_repository.get_all_bookings(
        session,
        date
    )

    return {
        'bookings': bookings
    }


async def get_all_user_bookings(
        session: AsyncSession,
        current_user: models.User,
) -> dict:
    """Возвращает бронирования текущего пользователя."""

    bookings = await booking_repository.get_user_bookings(
        session,
        current_user.id
    )

    return {
        'bookings': bookings
    }


async def book_room_cancel(
        session: AsyncSession,
        current_user: models.User,
        booking_id: int
) -> dict:
    """Отменяет бронирование с проверкой прав и блокировкой строки."""

    # Блокировка действует до завершения транзакции.
    await booking_repository.lock_booking_for_update(
        session,
        booking_id
    )

    booking = await get_db_object_by_id(
        session, models.Booking, booking_id
    )

    if (
            current_user.role == models.UserRole.EMPLOYEE
            and current_user.id != booking.owner_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Сотрудники могут отменять только свои бронирования'
        )

    if booking.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Данное бронирование уже было отменено'
        )

    booking.is_active = False
    booking.cancelled_at = datetime.datetime.now(datetime.UTC)
    booking.cancelled_by_id = current_user.id

    await commit_refresh_db(
        model=booking,
        error='Конфликт данных при отмене бронирования',
        session=session
    )

    return {
        'status': 'Бронирование отменено'
    }
