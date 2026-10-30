
"""Проверка метаданных и структуры OpenAPI."""

import re

from app.app import app


def test_openapi_metadata():
    schema = app.openapi()

    assert schema["info"]["title"] == "Meeting Room Booking API"
    assert schema["info"]["version"] == "0.9.0"

    assert {tag["name"] for tag in schema["tags"]} == {
        "Authentication",
        "Users",
        "Rooms",
        "Bookings",
        "Health",
    }


def test_openapi_route_tags():
    schema = app.openapi()
    paths = schema["paths"]

    assert paths["/login"]["post"]["tags"] == ["Authentication"]
    assert paths["/users/self"]["get"]["tags"] == ["Users"]
    assert paths["/rooms"]["get"]["tags"] == ["Rooms"]
    assert paths["/bookings"]["post"]["tags"] == ["Bookings"]
    assert paths["/health/ready"]["get"]["tags"] == ["Health"]


def test_openapi_bearer_authentication():
    schema = app.openapi()

    bearer = schema["components"]["securitySchemes"]["HTTPBearer"]

    assert bearer["type"] == "http"
    assert bearer["scheme"] == "bearer"

    # Бронирование требует JWT.
    assert schema["paths"]["/bookings"]["post"]["security"] == [
        {"HTTPBearer": []}
    ]

    # Вход в систему доступен без JWT.
    assert "security" not in schema["paths"]["/login"]["post"]


def test_openapi_request_examples():
    """Проверяет примеры запросов в OpenAPI."""

    schemas = app.openapi()["components"]["schemas"]

    register_example = schemas["RegisterRequest"]["examples"][0]
    login_example = schemas["LoginRequest"]["examples"][0]
    booking_example = schemas["CreateBookingRequest"]["examples"][0]

    assert register_example["username"] == "employee_demo"
    assert register_example["email"] == "employee@example.com"
    assert login_example["username"] == register_example["username"]

    assert booking_example["room_id"] == 1
    assert booking_example["time_window_id"] == 1
    assert booking_example["date"] == "2030-06-15"


def test_openapi_business_errors():
    """Проверяет документированные бизнес-ошибки."""

    paths = app.openapi()["paths"]

    assert "409" in paths["/register"]["post"]["responses"]
    assert "401" in paths["/login"]["post"]["responses"]

    booking_responses = paths["/bookings"]["post"]["responses"]
    assert "400" in booking_responses
    assert "409" in booking_responses

    cancel_responses = paths[
        "/bookings/cancel/{booking_id}"
    ]["patch"]["responses"]

    for status_code in ("400", "403", "404", "409"):
        assert status_code in cancel_responses


def test_openapi_operations_have_russian_summaries():
    """Проверяет русские названия всех операций API."""

    schema = app.openapi()
    methods = {"get", "post", "put", "patch", "delete"}

    for path, operations in schema["paths"].items():
        for method, operation in operations.items():
            if method not in methods:
                continue

            summary = operation["summary"]

            assert re.search(r"[А-Яа-яЁё]", summary), (
                f"{method.upper()} {path}: {summary}"
            )