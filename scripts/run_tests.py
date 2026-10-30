"""Запуск интеграционного окружения и набора pytest."""

import subprocess
import sys
import time
import urllib.error
import urllib.request


def main() -> int:
    # Применяем миграции к тестовой PostgreSQL.
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
    )

    # Запускаем API для интеграционных тестов.
    server = subprocess.Popen([
        sys.executable,
        "-m",
        "uvicorn",
        "app.app:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ])

    try:
        # Ожидаем запуска HTTP-сервера.
        for _ in range(60):
            if server.poll() is not None:
                raise RuntimeError(
                    "Test API exited before becoming ready"
                )

            try:
                with urllib.request.urlopen(
                    "http://127.0.0.1:8000/health/ready",
                    timeout=2,
                ):
                    break

            except (urllib.error.URLError, TimeoutError):
                time.sleep(1)

        else:
            raise RuntimeError(
                "Test API did not become ready"
            )

        # Запускаем unit и integration тесты.
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            check=False,
        )

        return result.returncode

    finally:
        # Корректно останавливаем тестовый API.
        server.terminate()

        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()


if __name__ == "__main__":
    raise SystemExit(main())
