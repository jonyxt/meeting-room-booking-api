"""Маршруты управления пользователями."""

from fastapi import APIRouter

from .. import models, schemas
from ..auth import AdminUserDep, CurrentUserDep
from ..dependencies import SessionDep
from ..services import auth_service, user_service
from ..services.object_lookup import get_db_object_by_id

router = APIRouter()

@router.get(
    '/users/self',
    response_model=schemas.GetUserResponse,
    description='Возвращает профиль текущего авторизованного пользователя.'
)
async def get_self(
        current_user: CurrentUserDep
):
    return auth_service.get_self(current_user)


@router.get(
    '/users',
    response_model=schemas.GetUsersResponse,
    description='Возвращает список всех пользователей. Доступно только администратору.'
)
async def get_users(
        _admin: AdminUserDep,
        session: SessionDep
):
    return await user_service.get_users(session)


@router.get(
    '/users/{user_id}',
    response_model=schemas.GetUserResponse,
    description='Возвращает пользователя по идентификатору. Доступно только администратору.'
)
async def get_user(
        user_id: int,
        _admin: AdminUserDep,
        session: SessionDep
):
    return await get_db_object_by_id(
        session, models.User, user_id
    )


@router.patch(
    '/users/{user_id}',
    response_model=schemas.GetUserResponse,
    description='Обновляет данные пользователя. Сотрудник может изменять '
                'только свой профиль, администратор — любого пользователя.'
)
async def update_user(
        user_id: int,
        current_user: CurrentUserDep,
        session: SessionDep,
        update_data: schemas.UpdateUserRequest
):
    return await user_service.update_user_by_id(
        session, user_id, update_data, current_user
    )