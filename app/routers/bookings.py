"""Маршруты управления бронированиями переговорных комнат."""

import datetime

from fastapi import APIRouter

from .. import schemas
from ..auth import AdminUserDep, CurrentUserDep
from ..dependencies import SessionDep
from ..services import booking_service

router = APIRouter()

@router.post(
    '/bookings',
    response_model=schemas.GetBookingResponse,
    description='Создает бронирование переговорной комнаты на выбранную дату и временной слот.'
)
async def book_room(
        booking_data: schemas.CreateBookingRequest,
        current_user: CurrentUserDep,
        session: SessionDep
):
    return await booking_service.book_room(session, current_user, booking_data)


@router.get(
    '/bookings/all',
    response_model=schemas.GetBookingsResponse,
    description='Возвращает все бронирования. Можно отфильтровать результат '
                'по query-параметру date. Доступно только администратору.'
)
async def get_all_bookings(
        _admin: AdminUserDep,
        session: SessionDep,
        date: datetime.date | None = None
):
    return await booking_service.get_all_bookings(session, date)


@router.get(
    '/bookings/{booking_id}',
    response_model=schemas.GetBookingResponse,
    description='Возвращает бронирование по идентификатору. Сотрудник видит '
                'только свои бронирования, администратор — любые.'
)
async def book_room_info(
        booking_id: int,
        current_user: CurrentUserDep,
        session: SessionDep
):
    return await booking_service.book_room_info(
        session, current_user, booking_id
    )


@router.get(
    '/bookings',
    response_model=schemas.GetBookingsResponse,
    description='Возвращает все бронирования текущего авторизованного пользователя.'
)
async def get_all_user_bookings(
        current_user: CurrentUserDep,
        session: SessionDep
):
    return await booking_service.get_all_user_bookings(
        session, current_user
    )


@router.patch(
    '/bookings/cancel/{booking_id}',
    response_model=schemas.CancelResponse,
    description='Отменяет бронирование. Сотрудник может отменить только свое '
                'бронирование, администратор — любое.'
)
async def book_room_update(
        current_user: CurrentUserDep,
        session: SessionDep,
        booking_id: int
):
    return await booking_service.book_room_cancel(
        session, current_user, booking_id
    )