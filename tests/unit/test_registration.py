from unittest.mock import AsyncMock, MagicMock

import pytest

from app import models, schemas
from app.services import auth_service


@pytest.mark.asyncio
async def test_first_registered_user_is_employee(monkeypatch):
    """Первый пользователь не получает права администратора."""

    session = MagicMock()
    session.scalar = AsyncMock(return_value=0)

    async def fake_commit_refresh_db(*, model, error, session):
        return model

    monkeypatch.setattr(
        auth_service,
        "commit_refresh_db",
        fake_commit_refresh_db
    )

    user_data = schemas.RegisterRequest(
        username="first_employee",
        email="first_employee@example.com",
        password="password123"
    )

    user = await auth_service.register_user(session, user_data)

    assert user.role == models.UserRole.EMPLOYEE
    session.add.assert_called_once_with(user)
