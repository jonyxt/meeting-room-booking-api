"""Unit-тесты проверки готовности PostgreSQL."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import health_service


def make_mock_engine():
    """Создаёт поддельный SQLAlchemy engine."""

    connection = AsyncMock()

    connection_context = AsyncMock()
    connection_context.__aenter__.return_value = connection

    engine = MagicMock()
    engine.connect.return_value = connection_context

    return engine, connection, connection_context


@pytest.mark.asyncio
async def test_database_ready_success(monkeypatch):
    """Успешный SELECT 1 означает готовность БД."""

    engine, connection, _ = make_mock_engine()

    monkeypatch.setattr(health_service, "engine", engine)

    result = await health_service.check_database_ready()

    assert result is True

    engine.connect.assert_called_once_with()
    connection.execute.assert_awaited_once()

    statement = connection.execute.await_args.args[0]
    assert str(statement) == "SELECT 1"


@pytest.mark.asyncio
async def test_database_connection_failure(monkeypatch, caplog):
    """Ошибка подключения не раскрывает конфиденциальные данные."""

    engine, _, context = make_mock_engine()

    context.__aenter__.side_effect = OSError(
        "password=super_secret_password"
    )

    monkeypatch.setattr(health_service, "engine", engine)

    result = await health_service.check_database_ready()

    assert result is False
    assert "Database readiness check failed" in caplog.text
    assert "super_secret_password" not in caplog.text


@pytest.mark.asyncio
async def test_database_query_failure(monkeypatch):
    """Ошибка SQL-запроса означает неготовность БД."""

    engine, connection, _ = make_mock_engine()

    connection.execute.side_effect = RuntimeError(
        "Database query failed"
    )

    monkeypatch.setattr(health_service, "engine", engine)

    result = await health_service.check_database_ready()

    assert result is False


@pytest.mark.asyncio
async def test_database_timeout(monkeypatch):
    """Зависший запрос прерывается по таймауту."""

    engine, connection, _ = make_mock_engine()

    async def hanging_query(_statement):
        await asyncio.Event().wait()

    connection.execute.side_effect = hanging_query

    monkeypatch.setattr(health_service, "engine", engine)
    monkeypatch.setattr(
        health_service,
        "DATABASE_HEALTH_TIMEOUT_SECONDS",
        0.01,
    )

    result = await health_service.check_database_ready()

    assert result is False
