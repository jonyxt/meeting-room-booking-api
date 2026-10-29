# Booking Service — сервис бронирования переговорных комнат

Backend-приложение на **FastAPI** для управления переговорными комнатами и бронированиями. В проекте реализованы регистрация сотрудников, JWT-аутентификация, разграничение прав, проверка доступности слотов, защита от конкурентных операций и отмена брони без удаления истории.

Проект создан как тестовое задание и развивается в качестве демонстрационного проекта Python Backend Developer. Основное внимание уделяется понятной архитектуре, безопасности API, тестированию и воспроизводимому запуску через Docker Compose.

## Возможности

- Регистрация пользователей с ролью `employee` и вход по JWT Bearer-токену.
- Создание первого администратора отдельной интерактивной CLI-командой; публичная регистрация не выдаёт роль `admin`.
- Управление пользователями и ролями, включая запрет понижения последнего администратора.
- Контроль доступа к профилям и бронированиям.
- Просмотр переговорных комнат и свободных временных слотов на дату.
- Создание и отмена бронирований с сохранением истории.
- Защита от двойного бронирования частичным уникальным индексом PostgreSQL.
- Защита конкурентной отмены через `SELECT ... FOR UPDATE`.
- Миграции схемы базы данных через Alembic.
- Повторяемая инициализация стандартных комнат и временных слотов.
- Отдельные liveness/readiness endpoints с проверкой доступности PostgreSQL.
- Изолированный запуск unit- и integration-тестов через отдельный Docker Compose-файл.

## Технологии

| Компонент | Технология |
| --- | --- |
| Язык | Python 3.13 в Docker; локально поддерживается версия, совместимая с `pyproject.toml` |
| HTTP API | FastAPI, Uvicorn |
| СУБД | PostgreSQL 16 |
| ORM и драйвер | SQLAlchemy 2 (async), asyncpg |
| Миграции | Alembic |
| Конфигурация | Pydantic Settings, переменные окружения, `.env` |
| Аутентификация | PyJWT, bcrypt |
| Тесты | pytest, pytest-asyncio, httpx, `unittest.mock` |
| Зависимости | Poetry |
| Контейнеризация | Docker, Docker Compose (multi-stage Dockerfile) |

## Архитектура и структура проекта

HTTP-обработка и бизнес-операции разделены по слоям **Router → Service → Repository**. Роутеры отвечают за HTTP-контракт, сервисы — за бизнес-правила, репозитории — за запросы к данным. Проверки состояния инфраструктуры вынесены в отдельные router и service.

```text
Shift_Test_Task/
├── app/
│   ├── app.py                      # Создание FastAPI, подключение роутеров
│   ├── auth.py                     # JWT, пароли, права доступа
│   ├── bootstrap_admin.py          # CLI: первый администратор
│   ├── config.py                   # Pydantic Settings
│   ├── database.py                 # Async SQLAlchemy engine и фабрика сессий
│   ├── dependencies.py             # Зависимости FastAPI
│   ├── lifespan.py                 # Завершение работы engine
│   ├── models.py                   # ORM-модели
│   ├── schemas.py                  # Pydantic-схемы API
│   ├── seed_data.py                # CLI: начальные комнаты и слоты
│   ├── routers/                   # auth, users, rooms, bookings, health
│   ├── services/                  # Сервисы, включая health_service.py
│   └── repositories/              # Запросы к БД
├── alembic/
│   ├── versions/                  # Миграции
│   └── env.py
├── scripts/
│   └── run_tests.py               # Миграции, тестовый API, запуск pytest
├── tests/
│   ├── conftest.py                 # Общие фикстуры, защита тестовой БД
│   ├── unit/                      # Изолированные unit-тесты
│   └── integration/               # Тесты работающего HTTP API
├── .dockerignore
├── .env.example
├── .env.prod.example
├── .gitignore
├── alembic.ini
├── Dockerfile                    # Стадии production и test
├── docker-compose.yml            # db, migrate, seed, app
├── docker-compose.test.yml       # test_db, tests
├── poetry.lock
├── pyproject.toml
└── README.md
```

## Быстрый старт через Docker Compose

**Требуется:** Git и Docker Desktop с Docker Compose (Windows/macOS) либо Docker Engine с Compose (Linux). Для контейнерного запуска не требуется устанавливать PostgreSQL и Poetry на компьютер.

### 1. Клонирование

```powershell
git clone https://github.com/jonyxt/Shift_Test_Task.git
cd Shift_Test_Task
```

### 2. Настройка переменных окружения

Создайте `.env` из шаблона:

```powershell
Copy-Item .env.example .env
```

На Linux/macOS:

```bash
cp .env.example .env
```

Пример параметров для локальной разработки:

```dotenv
APP_ENV=dev

POSTGRES_USER=postgres
POSTGRES_PASSWORD=REPLACE_WITH_STRONG_DB_PASSWORD
POSTGRES_DB=booking_db
POSTGRES_HOST=localhost
POSTGRES_PORT=3223

JWT_SECRET=REPLACE_WITH_A_RANDOM_SECRET_AT_LEAST_32_BYTES
JWT_ALGORITHM=HS256
JWT_EXP_DELTA_SECONDS=3600
```

Замените `POSTGRES_PASSWORD` и `JWT_SECRET` на собственные значения. Секрет JWT должен содержать не менее **32 байт UTF-8**. Сгенерировать случайный секрет можно командой:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Не публикуйте `.env`, реальные пароли и ключи в Git.

`POSTGRES_HOST=localhost` и `POSTGRES_PORT=3223` предназначены для запуска Python непосредственно на компьютере. В Docker Compose PostgreSQL доступна контейнерам по адресу `db:5432`; тестовая БД — по `test_db:5432`. Compose переопределяет соответствующие значения для своих сервисов.

| `APP_ENV` | Назначение |
| --- | --- |
| `dev` | Локальная разработка и основной Compose |
| `test` | Изолированные тесты с `test_db` |
| `prod` | Режим с дополнительной проверкой секретов и конфигурации |

Файл `.env.prod.example` — **пример конфигурации для будущего production-развёртывания**, а не готовая команда запуска production. В текущем основном `docker-compose.yml` для приложения закреплён `APP_ENV: dev`; сам по себе Docker-образ с target `production` не означает полноценное production-окружение.

### 3. Сборка и запуск приложения

```powershell
docker compose up -d --build --wait app
```

Сервисы основного `docker-compose.yml`:

| Сервис | Назначение |
| --- | --- |
| `db` | PostgreSQL с постоянным томом данных |
| `migrate` | Применяет `alembic upgrade head` |
| `seed` | Создаёт недостающие стандартные комнаты и слоты |
| `app` | Запускает FastAPI |

Последовательность запуска: **PostgreSQL → миграции → начальные данные → FastAPI**. Приложение больше **не зависит от прохождения pytest при старте**. Тестирование выполняется отдельно до публикации или развёртывания новой версии.

Многостадийный `Dockerfile` разделяет `production` и `test`: рабочий образ не включает каталог `tests/` и зависимости группы `dev`. Приложение запускается от непривилегированного системного пользователя `appuser` (UID 10001).

Основной Compose публикует порты FastAPI и PostgreSQL только на `127.0.0.1` компьютера, а не на всех сетевых интерфейсах.

### 4. Проверка запуска

```powershell
docker compose ps -a
docker compose logs migrate
docker compose logs seed
docker compose logs app
```

После успешного запуска ожидаются: `db` — `healthy`, `migrate` и `seed` — завершены с кодом `0`, `app` — `healthy`.

Локально доступны:

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI: http://127.0.0.1:8000/openapi.json
- Liveness: http://127.0.0.1:8000/health/live
- Readiness: http://127.0.0.1:8000/health/ready

### 5. Создание первого администратора

После запуска приложения выполните:

```powershell
docker compose exec app python -m app.bootstrap_admin
```

CLI интерактивно запросит имя, email и пароль. Пароль вводится без отображения и хранится в базе как bcrypt-хеш. Если администратор уже существует, команда не создаст ещё одного первого администратора.

Публичный `POST /register` всегда создаёт пользователя с ролью `employee`. Администратор тестового окружения не попадает в рабочую БД.

## Health Checks

Маршруты доступны **без JWT** и не раскрывают внутренние ошибки PostgreSQL в HTTP-ответах.

| Метод | Маршрут | Проверка | Результат |
| --- | --- | --- | --- |
| `GET` | `/health/live` | Отвечает ли процесс FastAPI | `200` при доступности API |
| `GET` | `/health/ready` | Выполняется ли `SELECT 1` в PostgreSQL | `200` или `503` |

**Liveness** не зависит от БД:

```json
{"status": "alive"}
```

**Readiness**, при доступной базе данных:

```json
{"status": "ready"}
```

Если соединение или запрос к PostgreSQL завершается ошибкой либо превышает таймаут (2 секунды), возвращается HTTP `503`:

```json
{"detail": "Service is not ready"}
```

Проверка выполняется с существующим SQLAlchemy engine, без отдельного пула соединений. HTTP-ответ не содержит SQL, адреса БД, пароля или traceback.

Docker healthcheck сервиса `app` обращается к **`/health/ready`** с параметрами `interval: 10s`, `timeout: 5s`, `retries: 3`, `start_period: 20s`. Статус `unhealthy` сам по себе не означает автоматического перезапуска контейнера в Docker Compose.

## Тестирование

Тестовая инфраструктура отделена от рабочего запуска и описана в **`docker-compose.test.yml`**. В ней используются `test_db` (отдельная PostgreSQL) и `tests` (образ со средствами тестирования).

### Полный набор тестов в Docker

Из корня проекта:

```powershell
docker compose -p booking-tests -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from tests tests
```

Параметр `-p booking-tests` задаёт отдельное имя Compose-проекта, чтобы тестовые контейнеры и сеть не смешивались с рабочим Compose-проектом.

Скрипт `scripts/run_tests.py` последовательно:

1. Применяет миграции Alembic к **тестовой** БД.
2. Запускает временный Uvicorn на `127.0.0.1:8000` внутри тестового контейнера.
3. Ожидает HTTP `200` от `/health/ready`.
4. Запускает `pytest` и возвращает его код завершения.
5. Завершает тестовый API после выполнения тестов.

Просмотр результатов:

```powershell
docker compose -p booking-tests -f docker-compose.test.yml logs tests
```

Удаление контейнеров и сети тестового проекта после завершения:

```powershell
docker compose -p booking-tests -f docker-compose.test.yml down
```

> **Защита тестовой БД:** очистка таблиц разрешена только при `ALLOW_TEST_DB_RESET=1`, `POSTGRES_DB=test_db` и `POSTGRES_HOST=test_db`. Тесты не должны очищать основную БД `booking_db`.

### Unit-тесты локально

В PyCharm или PowerShell, с установленным Poetry:

```powershell
poetry install
poetry run pytest -q tests/unit
```

Unit-тесты Health Checks используют моки и не требуют запущенной PostgreSQL. Integration-тесты выполняются через HTTP и требуют поднятого тестового API и тестовой БД.

**Статус проверки:** до инфраструктурных изменений успешно проходили **190 тестов**. Новые изменения Docker/конфигурации и Health Checks пока не проходили итоговый полный прогон; результат будет подтверждён после финального тестирования этапа 5.

## Миграции Alembic

Структура БД управляется миграциями; FastAPI не создаёт таблицы автоматически через `Base.metadata.create_all()`.

Начальная миграция — `c75bfc27cc29_initial_schema.py`. Она создаёт таблицы `users`, `rooms`, `time_windows`, `bookings`, связи и ограничения, ENUM роли пользователя, частичный уникальный индекс активных бронирований.

Обычно сервис `migrate` запускается при старте через Docker Compose. При необходимости команды можно выполнить вручную, когда PostgreSQL уже работает:

```powershell
# Применить миграции
docker compose run --rm --no-deps migrate alembic upgrade head

# Текущая ревизия
docker compose run --rm --no-deps migrate alembic current

# Проверить расхождение моделей и схемы
docker compose run --rm --no-deps migrate alembic check
```

Создание новой миграции при локальной разработке:

```powershell
poetry run alembic revision --autogenerate -m "describe schema change"
poetry run alembic upgrade head
```

Проверяйте автосгенерированные миграции вручную: особенно ENUM, индексы, ограничения и удаление столбцов. Новые файлы миграций добавляются в Git вместе с моделями.

**Важно:** `alembic downgrade base` на рабочей БД удалит объекты начальной схемы и данные приложения. Перед опасными миграциями нужны резервная копия и план восстановления; `alembic stamp` не заменяет реальную миграцию.

## Начальные данные

Сервис `seed` вызывает `app.seed_data`, создающий недостающие комнаты:

| Комната | Описание |
| --- | --- |
| Большой конференц зал | До 25 человек |
| Средний конференц зал | До 15 человек |
| Малый конференц зал | До 8 человек |

Для каждой комнаты добавляются интервалы `09:00–12:00`, `13:00–16:00`, `16:00–19:00` — всего **3 комнаты и 9 временных слотов** на пустой БД.

Повторный запуск не должен дублировать существующие данные. Для защиты параллельного выполнения используется PostgreSQL advisory lock. При работающей БД команду можно выполнить отдельно:

```powershell
docker compose run --rm --no-deps seed
```

Первый администратор через `seed` **не создаётся**.

## Локальная разработка в PyCharm / Poetry

Для запуска FastAPI вне контейнера нужны Python с версией, совместимой с `pyproject.toml` (в проекте локально используется Python 3.14), Poetry и доступная PostgreSQL.

1. Создайте `.env` из `.env.example` и укажите настройки подключения к БД на компьютере (например, `localhost:3223`).
2. Установите зависимости и поднимите PostgreSQL:

   ```powershell
   poetry install
   docker compose up -d db
   ```

3. Примените миграции и начальные данные:

   ```powershell
   poetry run alembic upgrade head
   poetry run python -m app.seed_data
   ```

4. Запустите приложение:

   ```powershell
   poetry run uvicorn app.app:app --reload
   ```

Запуск Uvicorn сам по себе не применяет миграции и не запускает pytest.

## API

Для защищённых маршрутов требуется заголовок:

```http
Authorization: Bearer <access_token>
```

### Регистрация и вход

| Метод | Маршрут | Назначение |
| --- | --- | --- |
| `POST` | `/register` | Регистрация сотрудника |
| `POST` | `/login` | Выдача JWT |

Пример регистрации:

```json
{
  "username": "employee_user",
  "email": "employee@example.com",
  "password": "password123",
  "phone": null
}
```

Пример входа:

```json
{"username": "employee_user", "password": "password123"}
```

При успешном входе сервер возвращает `access_token` и `token_type: "bearer"`.

### Пользователи

| Метод | Маршрут | Доступ |
| --- | --- | --- |
| `GET` | `/users/self` | Собственный профиль |
| `GET` | `/users` | Администратор |
| `GET` | `/users/{user_id}` | Администратор |
| `PATCH` | `/users/{user_id}` | Собственный профиль; администратор может менять другие профили и роли |

Роль администратора нельзя назначить себе через профиль; проверка прав опирается на актуальное состояние пользователя в БД, а не только на содержимое JWT.

### Переговорные комнаты

| Метод | Маршрут | Назначение |
| --- | --- | --- |
| `GET` | `/rooms` | Список комнат |
| `GET` | `/rooms/{room_id}` | Информация о комнате |
| `GET` | `/rooms/available/{date}` | Свободные слоты на дату |

Пример: `GET /rooms/available/2030-01-15`.

### Бронирования

| Метод | Маршрут | Назначение |
| --- | --- | --- |
| `POST` | `/bookings` | Создание бронирования |
| `GET` | `/bookings` | Свои бронирования |
| `GET` | `/bookings/{booking_id}` | Своя бронь или любая для администратора |
| `GET` | `/bookings/all` | Все бронирования; администратор |
| `PATCH` | `/bookings/cancel/{booking_id}` | Отмена своей или любой брони администратором |

Пример создания бронирования:

```json
{
  "room_id": 1,
  "time_window_id": 1,
  "date": "2030-01-15"
}
```

`time_window_id` должен принадлежать указанной комнате. Доступные ID возвращает `/rooms/available/{date}`. Администратору доступна фильтрация `GET /bookings/all?date=2030-01-15`.

При отмене брони поле `is_active` становится `false`, а запись сохраняется. Освобождённый слот можно забронировать снова.

Типовые HTTP-коды ошибок: `400` — бизнес-ограничение; `401` — нет или недействителен токен; `403` — нет прав; `404` — объект отсутствует; `409` — конфликт; `422` — ошибка валидации. Для неготового приложения `/health/ready` возвращает `503`.

## Управление Docker Compose и данными

```powershell
# Состояние рабочих контейнеров
docker compose ps -a

# Логи API
docker compose logs app

# Остановить контейнеры, не удаляя их
docker compose stop

# Остановить и удалить контейнеры и сеть, сохранив том PostgreSQL
docker compose down
```

PostgreSQL использует именованный том `postgres_data`; команда `docker compose down` сохраняет данные. **Не используйте `docker compose down -v`**, если нужно сохранить пользователей и бронирования: флаг `-v` удаляет тома Compose-проекта.

## Безопасность и ограничения

- Docker Compose для локальной разработки ограничивает опубликованные порты интерфейсом `127.0.0.1`; это **не полноценный production-деплой**.
- Существует пример `.env.prod.example` и проверка production-секретов, но ещё нужны HTTPS/reverse proxy, резервное копирование, управление секретами, контроль доступа и безопасный процесс обновления.
- Сборка рабочего образа отделена от тестовой; наличие target `production` не гарантирует готовность всей инфраструктуры к публичному запуску.
- Health Checks определяют состояние процесса и PostgreSQL, но не проверяют наличие всех таблиц, статус миграций или корректность бизнес-операций.
- Реализованный Docker healthcheck не подменяет внешние метрики, алерты и централизованный мониторинг.
- Тесты запускаются отдельно; CI/CD с GitHub Actions и автоматический rollback не следует считать реализованными, пока они не будут добавлены и проверены.
- Начальные комнаты — демонстрационные данные. При добавлении редактирования комнат нужно учитывать логику `seed`.
- Перед применением потенциально разрушительных миграций к БД необходима резервная копия.

---

**Репозиторий:** https://github.com/jonyxt/Shift_Test_Task
