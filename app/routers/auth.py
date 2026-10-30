"""Маршруты регистрации и авторизации пользователей."""

from fastapi import APIRouter

from .. import schemas
from ..dependencies import SessionDep
from ..services import auth_service

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=schemas.GetUserResponse,
    summary="Регистрация сотрудника",
    description=(
        "Создаёт пользователя с ролью `employee`. "
        "Роль администратора через публичную регистрацию получить нельзя."
    ),
    responses={
        409: {
            "description": "Имя пользователя, email или телефон уже заняты."
        },
    },
)

async def register(
        user_data: schemas.RegisterRequest,
        session: SessionDep
):
    return await auth_service.register_user(session, user_data)



@router.post(
    "/login",
    response_model=schemas.LoginResponse,
    summary="Вход в систему",
    description=(
        "Проверяет имя пользователя и пароль. "
        "При успешной аутентификации возвращает JWT access token. "
        "Токен необходимо передавать в заголовке "
        "`Authorization: Bearer <token>`."
    ),
    responses={
        401: {
            "description": "Неверный логин или пароль."
        },
    },
)

async def login(
        login_data: schemas.LoginRequest,
        session: SessionDep
):
    return await auth_service.login_user(session, login_data)