"""Маршруты управления бронированиями переговорных комнат."""

import datetime

from fastapi import APIRouter

from .. import schemas
from ..auth import AdminUserDep, CurrentUserDep
from ..dependencies import SessionDep
from ..services import booking_service

router = APIRouter(tags=["Bookings"])


@router.post(
    "/bookings",
    response_model=schemas.GetBookingResponse,
    summary="Создать бронирование",
    description=(
        "Бронирует переговорную комнату на указанную дату и временной слот.\n\n"
        "Комната должна быть активной, а слот — принадлежать этой комнате. "
        "Бронирование на прошедшую дату запрещено.\n\n"
        "Идентификаторы комнат и свободных слотов можно получить "
        "через `GET /rooms/available/{date}`."
    ),
    responses={
        400: {
            "description": "Недопустимая дата, комната или временной слот."
        },
        409: {
            "description": "Временной слот уже забронирован."
        },
    },
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
    summary='Получить все бронирования',
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
    summary='Получить бронирование',
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
    summary='Получить свои бронирования',
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
    "/bookings/cancel/{booking_id}",
    response_model=schemas.CancelResponse,
    summary="Отменить бронирование",
    description=(
        "Сотрудник может отменить собственное бронирование, "
        "администратор — любое.\n\n"
        "При отмене бронирование помечается неактивным. "
        "Запись сохраняется в истории вместе со временем отмены "
        "и пользователем, выполнившим операцию."
    ),
    responses={
        400: {
            "description": "Бронирование уже отменено."
        },
        403: {
            "description": "Недостаточно прав для отмены."
        },
        404: {
            "description": "Бронирование не найдено."
        },
        409: {
            "description": "Конфликт данных при сохранении изменений."
        },
    },
)

async def book_room_update(
        current_user: CurrentUserDep,
        session: SessionDep,
        booking_id: int
):
    return await booking_service.book_room_cancel(
        session, current_user, booking_id
    )