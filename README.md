# Hotel Booking Service

Сервис для управления номерами отеля и бронированиями.

## Запуск

1. Установите Poetry (если не установлен): https://python-poetry.org/docs/
2. Установите зависимости:
    ```bash
    poetry install
    ```
3. Примените миграции:
    ```bash
    poetry run python manage.py migrate
    ```
4. Запустите сервер:
    ```bash
    poetry run python manage.py runserver localhost:8000
    ```

## Описание API

### Номера отелей (Rooms)

**Создать номер**
`POST /rooms/create`
```json
{
  "description": "Описание номера",
  "price": 3200
}
```
Ответ:
```json
{ "room_id": 1 }
```

**Удалить номер**
`DELETE /rooms/delete/<room_id>`
```json
{ "success": true }
```

**Получить список номеров**
`GET /rooms/list?sort_by=price|created_at&order=asc|desc`
Ответ:
```json
[
  {"id": 1, "description": "Люкс", "price": 3000, "created_at": "2024-07-01T12:34:00Z"}, ...
]
```

### Бронирования (Bookings)

**Создать бронь**
`POST /bookings/create`
```json
{
  "room_id": 1,
  "date_start": "2024-12-01",
  "date_end": "2024-12-05"
}
```
Ответ:
```json
{ "booking_id": 100 }
```

**Удалить бронь**
`DELETE /bookings/delete/<booking_id>`
```json
{ "success": true }
```

**Список броней номера**
`GET /bookings/list?room_id=1`
Ответ:
```json
[
  {"id": 100, "room": 1, "date_start": "2024-12-01", "date_end": "2024-12-05"}, ...
]
```

## Ошибки
Все ошибки возвращаются с ключом `error`:
```json
{"error": "Room already booked for these dates"}
```

## Примечания и вопросы
- Сервис не требует авторизации.
- Валидация работы с датами: запрещены пересечения бронирований.

## Линтинг через Ruff

Запуск проверки и авто-правок:
```bash
poetry run ruff check .
poetry run ruff format .
```

Конфигурация находится в файле `.ruff.toml`.

## Тесты (pytest)

Установка и запуск:
```bash
poetry install
poetry run pytest
```

Тесты лежат в каталоге `tests/` и используют `pytest-django`.

## Запуск в Docker

Сборка и запуск:
```bash
docker compose up --build
```

Сервис будет доступен на `http://localhost:8000`.

Данные SQLite сохраняются через volume, монтируемый в `./db.sqlite3`.

Запуск тестов внутри контейнера:
```bash
docker compose exec web poetry run pytest
```
