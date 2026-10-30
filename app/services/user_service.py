
"""Сервис управления пользователями."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..repositories import user_repository
from .object_lookup import get_db_object_by_id
from .transactions import commit_refresh_db


async def get_users(session: AsyncSession) -> dict:
    """Возвращает список всех пользователей."""

    users = await user_repository.get_all_users(session)

    return {
        'users': users
    }



async def update_user_by_id(
        session: AsyncSession,
        user_id: int,
        update_data: schemas.UpdateUserRequest,
        current_user: models.User
) -> models.User:
    """Обновляет данные пользователя.

    Обычный пользователь может изменять только свои данные.
    Администратор может изменять данные любого пользователя.

    При изменении роли проверяется, что в системе не останется
    ни одного администратора.

    Поля, которые не были переданы в запросе, не изменяются.
    """

    if current_user.role == models.UserRole.EMPLOYEE:
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Сотрудники могут менять только свой профиль'
            )

        if 'role' in update_data.model_fields_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Только Администраторы могут менять роли пользователей'
            )

    user = await get_db_object_by_id(
        session, models.User, user_id
    )

    update_dict = update_data.model_dump(exclude_unset=True)

    for field in ('username', 'email', 'role'):
        if field in update_dict and update_dict[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"{field} не может быть null"
            )

    if (
            update_dict.get('role') == models.UserRole.EMPLOYEE
            and user.role == models.UserRole.ADMIN
    ):
        await user_repository.lock_admin_role_changes(session)

        admins_count = await user_repository.count_admins(session)

        if admins_count == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Нельзя снять роль у последнего администратора'
            )

    for key, value in update_dict.items():
        setattr(user, key, value)

    return await commit_refresh_db(
        model=user,
        error='Пользователь с таким именем/почтой/телефоном уже существует',
        session=session
    )
