
"""Сервис регистрации и аутентификации пользователей."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .. import auth, models, schemas
from ..repositories import user_repository
from .transactions import commit_refresh_db


async def register_user(
        session: AsyncSession,
        user_data: schemas.RegisterRequest
) -> models.User:
    """Регистрирует нового пользователя с ролью employee.

    Пароль сохраняется в базе данных только в виде хеша.
    """
    new_user = models.User(
        username=user_data.username,
        hashed_password=auth.hash_password(user_data.password),
        email=user_data.email,
        phone=user_data.phone,
        role=models.UserRole.EMPLOYEE
    )

    session.add(new_user)

    return await commit_refresh_db(
        model=new_user,
        error='Пользователь с таким именем/почтой/телефоном уже существует',
        session=session
    )


async def login_user(
        session: AsyncSession,
        login_data: schemas.LoginRequest
) -> schemas.LoginResponse:
    """Проверяет логин и пароль и возвращает JWT-токен."""

    user = await user_repository.get_user_by_username(
        session,
        login_data.username
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail='Неверный логин или пароль'
        )

    if not auth.check_password(
            login_data.password,
            user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail='Неверный логин или пароль'
        )

    token = auth.create_access_token(user_id=user.id)

    return schemas.LoginResponse(access_token=token)


def get_self(current_user: models.User) -> models.User:
    """Возвращает данные текущего авторизованного пользователя."""
    return current_user
