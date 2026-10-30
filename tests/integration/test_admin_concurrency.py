
"""Проверка конкурентного изменения ролей администраторов."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import httpx

from app import models
from app.database import AsyncSessionLocal, engine
from tests.integration.helpers import BASE_URL, auth_headers


def test_concurrent_admin_demotions_preserve_last_admin(
    api_client, admin_token, create_test_user
):
    """Одновременное понижение двух администраторов сохраняет одного."""

    # Получаем первоначального администратора.
    response = api_client.get(
        "/users/self",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    original_admin_id = response.json()["id"]

    # Создаём второго администратора.
    second_user, second_token = create_test_user()
    second_admin_id = second_user["id"]

    response = api_client.patch(
        f"/users/{second_admin_id}",
        headers=auth_headers(admin_token),
        json={"role": "admin"},
    )
    assert response.status_code == 200

    barrier = Barrier(2)

    def demote(user_id: int, token: str):
        """Отправляет запрос после синхронизации потоков."""
        with httpx.Client(
            base_url=BASE_URL,
            timeout=25.0,
        ) as client:
            barrier.wait(timeout=15)

            return client.patch(
                f"/users/{user_id}",
                headers=auth_headers(token),
                json={"role": "employee"},
            )

    try:
        # Оба администратора одновременно понижают себя.
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(
                demote, original_admin_id, admin_token
            )
            second = pool.submit(
                demote, second_admin_id, second_token
            )

            responses = [first.result(), second.result()]

        statuses = sorted(
            response.status_code for response in responses
        )

        # Один запрос проходит, другой отклоняется.
        # 400 — последний администратор.
        # 403 — права изменились до обработки второго запроса.
        assert statuses in ([200, 400], [200, 403]), [
            (response.status_code, response.text)
            for response in responses
        ]

        # Проверяем фактическое состояние обоих пользователей.
        first_profile = api_client.get(
            "/users/self",
            headers=auth_headers(admin_token),
        )
        second_profile = api_client.get(
            "/users/self",
            headers=auth_headers(second_token),
        )

        assert first_profile.status_code == 200
        assert second_profile.status_code == 200

        roles = [
            first_profile.json()["role"],
            second_profile.json()["role"],
        ]

        assert roles.count("admin") == 1

    finally:
        # Восстанавливаем исходные роли независимо от результата теста.
        async def restore_roles():
            try:
                async with (
                    AsyncSessionLocal() as session,
                    session.begin(),
                ):
                    original = await session.get(
                        models.User, original_admin_id
                    )
                    additional = await session.get(
                        models.User, second_admin_id
                    )

                    original.role = models.UserRole.ADMIN
                    additional.role = models.UserRole.EMPLOYEE
            finally:
                await engine.dispose()

        asyncio.run(restore_roles())
