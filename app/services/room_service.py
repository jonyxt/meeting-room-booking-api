
"""Сервис просмотра переговорных комнат и доступных временных слотов."""

import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories import room_repository


async def get_all_rooms_info(session: AsyncSession) -> dict:
    """Возвращает список всех переговорных комнат."""

    rooms = await room_repository.get_all_rooms(session)

    return {
        'rooms': rooms
    }


async def get_date_available_bookings(
        session: AsyncSession,
        date: datetime.date
) -> dict:
    """Формирует список комнат с доступными временными слотами."""

    rows = await room_repository.get_available_room_windows(
        session,
        date
    )

    rooms = {}

    for room, window in rows:
        if room.id not in rooms:
            rooms[room.id] = {
                'id': room.id,
                'room_name': room.room_name,
                'description': room.description,
                'available_time_windows': [],
            }

        rooms[room.id]['available_time_windows'].append({
            'id': window.id,
            'start_time': window.start_time,
            'end_time': window.end_time
        })

    return {
        'rooms': list(rooms.values())
    }
