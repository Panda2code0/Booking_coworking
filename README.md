# Сервис бронирования переговорных комнат

Веб-сервис для автоматизации бронирования переговорных комнат в коворкинге.  
Сотрудники просматривают доступность комнат на выбранную дату, создают и отменяют свои бронирования.  
Администраторы управляют комнатами, временными слотами и могут отменять любые бронирования.

## Стек

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Pydantic v2
- JWT-аутентификация
- Poetry
- Alembic
- Docker / Docker Compose
- Pytest

## Требования

- Python 3.12+
- Poetry
- Docker и Docker Compose (для контейнерного запуска)
- PostgreSQL 16 (локально или через Docker)

## Быстрый старт (Docker Compose)

Самый простой способ — поднять приложение вместе с базой данных:

```bash
git clone <url-репозитория>
cd booking_coworking
cp .env.example .env
docker compose up --build
```

API будет доступен по адресу: **http://localhost:8000**  (до хостинга)
Swagger UI: **http://localhost:8000/docs**  (до хостинга)

При старте контейнера автоматически выполняются миграции Alembic.

## Локальный запуск

```bash
poetry install
cp .env.example .env
docker compose up -d postgres
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

## Запуск через Docker (только приложение)

Если PostgreSQL уже запущен отдельно:

```bash
docker build -t booking-coworking .
docker run --env-file .env -p 8000:8000 booking-coworking
```

Убедитесь, что в `.env` указан корректный `DB_HOST` (для Docker-сети — имя сервиса `postgres`).

## Переменные окружения

Скопируйте `.env.example` в `.env`:

| Переменная | Описание |
|---|---|
| `DB_HOST` | Хост PostgreSQL |
| `DB_PORT` | Порт PostgreSQL |
| `DB_NAME` | Имя базы данных |
| `DB_USER` | Пользователь БД |
| `DB_PASSWORD` | Пароль БД |
| `SECRET_KEY` | Секретный ключ для JWT |
| `ALGORITHM` | Алгоритм JWT (по умолчанию `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена в минутах |

## Миграции

```bash
# Применить миграции
poetry run alembic upgrade head

# Создать новую миграцию после изменения моделей
poetry run alembic revision --autogenerate -m "описание"
```

## Роли пользователей

| Роль | Возможности |
|---|---|
| **Сотрудник** (`employee`) | Просмотр комнат, слотов и доступности; создание и отмена **своих** бронирований |
| **Администратор** (`admin`) | Всё выше + CRUD комнат и слотов; просмотр всех бронирований; отмена **любой** брони |

> При регистрации через API создаётся пользователь с ролью `employee`.  
> Чтобы создать администратора, выполните SQL после регистрации:

```sql
UPDATE users SET role = 'admin' WHERE username = 'ваш_логин';
```

## API

### Аутентификация

| Метод | Endpoint | Доступ | Описание |
|---|---|---|---|
| `POST` | `/auth/register` | Публичный | Регистрация сотрудника |
| `POST` | `/auth/login` | Публичный | Получение JWT-токена |

### Комнаты

| Метод | Endpoint | Доступ | Описание |
|---|---|---|---|
| `GET` | `/rooms` | Авторизованный | Список всех комнат |
| `GET` | `/rooms/availability?date=YYYY-MM-DD` | Авторизованный | **Доступность всех комнат на дату** |
| `GET` | `/rooms/{id}` | Авторизованный | Комната по ID |
| `POST` | `/rooms` | Admin | Создать комнату |
| `PATCH` | `/rooms/{id}` | Admin | Обновить комнату |
| `DELETE` | `/rooms/{id}` | Admin | Удалить комнату |

### Временные слоты

| Метод | Endpoint | Доступ | Описание |
|---|---|---|---|
| `GET` | `/slots` | Авторизованный | Список всех слотов |
| `GET` | `/slots/{id}` | Авторизованный | Слот по ID |
| `POST` | `/slots` | Admin | Создать слот |
| `PATCH` | `/slots/{id}` | Admin | Обновить слот |
| `DELETE` | `/slots/{id}` | Admin | Удалить слот |

### Бронирования

| Метод | Endpoint | Доступ | Описание |
|---|---|---|---|
| `POST` | `/bookings` | Авторизованный | Создать бронирование |
| `GET` | `/bookings/me` | Авторизованный | Мои бронирования |
| `GET` | `/bookings` | Admin | Все бронирования |
| `DELETE` | `/bookings/{id}` | Владелец / Admin | Отменить бронирование |

## Примеры работы (curl)

### 1. Регистрация

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "ivan", "password": "secret123"}'
```

Ответ:
```json
{"id": 1, "username": "ivan", "role": "employee"}
```

### 2. Получение JWT-токена

```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=ivan&password=secret123"
```

Ответ:
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

Сохраните токен в переменную:

```bash
TOKEN="eyJ..."
```

### 3. Создание комнаты и слота (admin)

```bash
# Создать комнату
curl -X POST http://localhost:8000/rooms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Переговорная A", "capacity": 8}'

# Создать временной слот
curl -X POST http://localhost:8000/slots \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "start_time": "09:00:00", "end_time": "11:00:00"}'
```

### 4. Просмотр доступности на дату

```bash
curl "http://localhost:8000/rooms/availability?date=2026-08-15" \
  -H "Authorization: Bearer $TOKEN"
```

Ответ:
```json
[
  {
    "room_id": 1,
    "room_name": "Переговорная A",
    "capacity": 8,
    "date": "2026-08-15",
    "slots": [
      {
        "slot_id": 1,
        "start_time": "09:00:00",
        "end_time": "11:00:00",
        "is_available": true
      }
    ]
  }
]
```

### 5. Создание бронирования

```bash
curl -X POST http://localhost:8000/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "date": "2026-08-15", "time_slot_id": 1}'
```

### 6. Просмотр своих бронирований

```bash
curl http://localhost:8000/bookings/me \
  -H "Authorization: Bearer $TOKEN"
```

### 7. Отмена бронирования

```bash
curl -X DELETE http://localhost:8000/bookings/1 \
  -H "Authorization: Bearer $TOKEN"
```

## Аутентификация в Swagger UI

1. Зарегистрируйтесь через `POST /auth/register`
2. Получите токен через `POST /auth/login` (form: username + password)
3. Нажмите **Authorize** и введите: `Bearer <access_token>`

## Тесты

```bash
# Все тесты
poetry run pytest

# С отчётом о покрытии
poetry run pytest --cov=app
```

Тесты используют отдельную базу `meeting_booking_test` и запускаются асинхронно через `httpx.AsyncClient` с реальным PostgreSQL.

## Структура проекта

```
app/
  api/          # HTTP-обработчики (тонкий слой)
  core/         # Конфигурация, JWT, безопасность
  db/           # Подключение к БД, сессии
  models/       # SQLAlchemy-модели
  schemas/      # Pydantic-схемы
  services/     # Бизнес-логика
alembic/        # Миграции базы данных
tests/          # Pytest-тесты
```

## Бизнес-правила

- Один слот комнаты на одну дату может быть забронирован только один раз (защита от наложений встреч)
- Сотрудник не может просматривать или отменять чужие бронирования
- Администратор может отменить любое бронирование
- Слот должен принадлежать указанной комнате при создании брони
