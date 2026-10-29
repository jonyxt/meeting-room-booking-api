"""Unit-тесты HTTP-маршрутов Health Checks."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.app import app
from app.services import health_service


@pytest.mark.asyncio
async def test_liveness_does_not_depend_on_database(monkeypatch):
    """Liveness не должен обращаться к PostgreSQL."""

    check = AsyncMock(
        side_effect=RuntimeError("Database must not be checked")
    )

    monkeypatch.setattr(
        health_service,
        "check_database_ready",
        check,
    )

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

    check.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "database_ready, expected_status, expected_body",
    [
        (True, 200, {"status": "ready"}),
        (
            False,
            503,
            {"detail": "Service is not ready"},
        ),
    ],
)
async def test_readiness_response(
    monkeypatch,
    database_ready,
    expected_status,
    expected_body,
):
    """Readiness возвращает статус в зависимости от БД."""

    check = AsyncMock(return_value=database_ready)

    monkeypatch.setattr(
        health_service,
        "check_database_ready",
        check,
    )

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/health/ready")

    assert response.status_code == expected_status
    assert response.json() == expected_body

    check.assert_awaited_once_with()
