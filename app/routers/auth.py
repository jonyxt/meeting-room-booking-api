"""Маршруты регистрации и авторизации пользователей."""

from fastapi import APIRouter

from .. import schemas
from ..dependencies import SessionDep
from ..services import auth_service

router = APIRouter()

@router.post(
    '/register',
    response_model=schemas.GetUserResponse,
    description='Регистрирует нового пользователя с ролью employee.'
)
async def register(
        user_data: schemas.RegisterRequest,
        session: SessionDep
):
    return await auth_service.register_user(session, user_data)


@router.post(
    '/login',
    response_model=schemas.LoginResponse,
    description='Проверяет логин и пароль пользователя и возвращает '
                'JWT-токен для доступа к защищенным endpoint.'
)
async def login(
        login_data: schemas.LoginRequest,
        session: SessionDep
):
    return await auth_service.login_user(session, login_data)