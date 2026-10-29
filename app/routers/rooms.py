
"""Маршруты просмотра переговорных комнат и доступных слотов."""

import datetime

from fastapi import APIRouter

from .. import models, schemas
from ..services import room_service
from ..auth import CurrentUserDep
from ..dependencies import SessionDep
from app.services.object_lookup import get_db_object_by_id


router = APIRouter()

@router.get(
    '/rooms/available/{date}',
    response_model=schemas.AvailableRoomsResponse,
    description='Возвращает доступные комнаты и свободные временные слоты на выбранную дату.'
)
async def get_date_available_bookings(
        date: datetime.date,
        _current_user: CurrentUserDep,
        session: SessionDep
):
    return await room_service.get_date_available_bookings(session, date)


@router.get(
    '/rooms',
    response_model=schemas.RoomsResponse,
    description='Возвращает список всех переговорных комнат. Требует авторизации.'
)
async def get_all_rooms_info(
        session: SessionDep,
        _current_user: CurrentUserDep,
):
    return await room_service.get_all_rooms_info(session)


@router.get(
    '/rooms/{room_id}',
    response_model=schemas.RoomResponse,
    description='Возвращает переговорную комнату по идентификатору. Требует авторизации.'
)
async def get_room_info_by_id(
        session: SessionDep,
        _current_user: CurrentUserDep,
        room_id: int
):
    return await get_db_object_by_id(
        session, models.Room, room_id
    )
