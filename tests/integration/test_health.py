"""Интеграционные тесты Health Checks."""


def test_liveness_endpoint(api_client):
    """Запущенное приложение отвечает на liveness."""

    response = api_client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_endpoint(api_client):
    """Приложение с доступной PostgreSQL готово к работе."""

    response = api_client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_health_routes_in_openapi(api_client):
    """Оба маршрута зарегистрированы в FastAPI."""

    response = api_client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/health/live" in paths
    assert "/health/ready" in paths
