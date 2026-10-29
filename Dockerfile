
# syntax=docker/dockerfile:1

# ==========================================
# 1. Общая стадия установки зависимостей
# ==========================================
FROM python:3.13-slim AS dependencies

WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install "poetry==2.5.1"

COPY pyproject.toml poetry.lock ./


# ==========================================
# 2. Production-зависимости
# ==========================================
FROM dependencies AS production-deps

RUN poetry install --only main --no-root --no-ansi


# ==========================================
# 3. Test-зависимости
# ==========================================
FROM dependencies AS test-deps

RUN poetry install --with dev --no-root --no-ansi


# ==========================================
# 4. Общая runtime-стадия
# ==========================================
FROM python:3.13-slim AS runtime

WORKDIR /app

# Непривилегированный пользователь приложения
RUN groupadd --system --gid 10001 appuser \
    && useradd --system \
        --uid 10001 \
        --gid appuser \
        --home-dir /tmp \
        --no-create-home \
        --shell /usr/sbin/nologin \
        appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic


# ==========================================
# 5. Образ для тестирования
# ==========================================
FROM runtime AS test

COPY --from=test-deps /app/.venv /app/.venv
COPY tests ./tests
COPY scripts ./scripts


# ==========================================
# 6. Production-образ
# ==========================================
FROM runtime AS production

COPY --from=production-deps /app/.venv /app/.venv

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]