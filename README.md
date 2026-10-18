# Менеджер задач — FastAPI + PostgreSQL + SQLAlchemy + Pydantic

Практическая работа № 2: REST API для хранения пользователей и их задач.

Стек: FastAPI, Starlette (middleware), SQLAlchemy 2.0 (async, asyncpg), Pydantic v2, pydantic-settings, Alembic, PostgreSQL 16 в Docker.

## Требования

- Python 3.11+
- Docker и Docker Compose
- Git

## Запуск

1. Клонировать репозиторий и перейти в папку проекта:

   ```bash
   git clone https://github.com/kholodkova/task-manager-python.git
   cd task-manager-python
   ```

2. Создать файл с переменными окружения из образца:

   ```bash
   cp .env.example .env
   ```

3. Запустить PostgreSQL и проверить доступность:

   ```bash
   docker compose up -d db
   docker compose exec db psql -U app -d tasks -c "select 1"
   ```

4. Создать виртуальное окружение и установить зависимости:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

5. Применить миграции (таблицы создаются только миграцией Alembic, `create_all` не используется):

   ```bash
   alembic upgrade head
   ```

6. Запустить сервис:

   ```bash
   uvicorn app.main:app --reload
   ```

7. Открыть Swagger UI: http://localhost:8000/docs

Остановка: `Ctrl+C` для сервиса, `docker compose stop` для базы. Данные сохраняются в томе `pgdata`.

## Структура проекта

```
app/
├── __init__.py
├── main.py          # создание приложения, middleware, подключение роутеров
├── config.py        # настройки (pydantic-settings), DATABASE_URL
├── db.py            # асинхронный движок, фабрика сессий, Base, get_session
├── models.py        # ORM-модели User и Task (SQLAlchemy 2.0)
├── schemas.py       # Pydantic-схемы Create / Read / Update
└── routers/
    ├── users.py     # /users
    └── tasks.py     # /tasks
migrations/          # Alembic (async), первая миграция в versions/
alembic.ini
docker-compose.yml   # PostgreSQL 16
requirements.txt
.env.example         # образец DATABASE_URL
```

## Эндпоинты

| Метод | Путь | Описание | Коды ответа |
|---|---|---|---|
| POST | /users | создать пользователя | 201, 409 (email занят), 422 |
| GET | /users/{id} | получить пользователя | 200, 404 |
| POST | /tasks | создать задачу | 201, 404 (нет владельца), 422 |
| GET | /tasks | список задач; фильтры `done`, `owner_id`; пагинация `limit` (1–100), `offset` | 200 |
| GET | /tasks/{id} | получить задачу | 200, 404 |
| PATCH | /tasks/{id} | частично обновить задачу | 200, 404, 422 |
| DELETE | /tasks/{id} | удалить задачу | 204, 404 |

Каждый ответ содержит заголовок `X-Process-Time` — время обработки запроса в секундах; метод, путь, статус и время пишутся в лог сервиса.

## Скриншоты

### Swagger UI

| Запрос | Скриншот |
|---|---|
| POST /users → 201 | ![](docs/screenshots/01-post-users-201.png) |
| GET /users/{id} → 200 | ![](docs/screenshots/02-get-user-200.png) |
| POST /tasks → 201 | ![](docs/screenshots/03-post-tasks-201.png) |
| GET /tasks → 200 | ![](docs/screenshots/04-get-tasks-200.png) |
| PATCH /tasks/{id} → 200 | ![](docs/screenshots/05-patch-task-200.png) |
| DELETE /tasks/{id} → 204 | ![](docs/screenshots/06-delete-task-204.png) |
| GET /tasks/{id} → 404 | ![](docs/screenshots/07-get-task-404.png) |

### Таблицы в БД (`\dt` в psql)

```bash
docker compose exec db psql -U app -d tasks -c '\dt'
```

![](docs/screenshots/08-dt.png)

## Ответы на контрольные вопросы

**1. Чем FastAPI отличается от Starlette и какие компоненты Starlette он использует?**

Я понимаю это так: Starlette даёт базовые вещи для работы веб-приложения, например маршруты, запросы, ответы и middleware. FastAPI построен на основе Starlette и добавляет проверку данных через Pydantic, зависимости через `Depends` и автоматическую документацию Swagger. В этом проекте механизм Starlette используется в middleware, которое добавляет заголовок `X-Process-Time`.

**2. Зачем разделять схемы Create, Read и Update?**

Отдельные схемы нужны, потому что при создании, чтении и изменении нужен разный набор полей. Например, при создании задачи клиент передаёт `title` и `owner_id`, а `id` и `created_at` создаёт само приложение. При обновлении все поля необязательны, потому что можно изменить только одно поле.

**3. Что делает `from_attributes=True`?**

`from_attributes=True` разрешает Pydantic брать данные из атрибутов объекта. Из базы получаем объект SQLAlchemy, например `Task`. С этой настройкой Pydantic может сам прочитать его `id`, `title` и другие поля. Без неё пришлось бы вручную создавать словарь с данными.

**4. Почему сессия передаётся через Depends, а не создаётся глобально?**

Сессию лучше создавать отдельно для каждого запроса. Если сделать одну глобальную сессию, одновременные запросы могут мешать друг другу. Через `Depends(get_session)` каждый обработчик получает свою сессию, а после ответа она закрывается.

**5. Чем `exclude_unset=True` отличается от `exclude_none=True`?**

`exclude_unset=True` убирает поля, которые клиент вообще не передал. `exclude_none=True` убирает все поля со значением `None`, даже если клиент передал их специально. Например, `{"description": null}` с `exclude_unset=True` очистит описание. С `exclude_none=True` такое поле было бы пропущено.

**6. Почему в production таблицы не создают через `create_all`?**

`create_all` умеет создавать отсутствующие таблицы, но не хранит историю изменений. В production база уже содержит данные, поэтому важно изменять её постепенно и понимать, какие изменения уже применены. Для этого нужен Alembic: каждое изменение схемы хранится в отдельной миграции, которую можно применить или откатить.

## Зависимости вне списка из задания

- `sqlalchemy[asyncio]` вместо `sqlalchemy` — ставит пакет greenlet, без которого асинхронный режим SQLAlchemy не импортируется.
- `email-validator` — без него не работает тип `EmailStr`, который требуется в шаге 7.
