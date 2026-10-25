"""Фикстуры для автотестов.

Практическая работа № 3, шаг 3:
- тесты ходят в отдельную базу tasks_test, а не в рабочую tasks;
- перед каждым тестом все строки удаляются — тест видит пустые таблицы;
- зависимость get_session подменяется через app.dependency_overrides.
"""

import os

# Адрес тестовой базы. Переменная окружения задаётся до импорта приложения:
# get_settings() читает DATABASE_URL при первом обращении (в app.db).
TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://app:app@localhost:5432/tasks_test")
os.environ["DATABASE_URL"] = TEST_DB_URL

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import delete  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import NullPool  # noqa: E402

from app.db import Base, get_session  # noqa: E402
from app.main import app  # noqa: E402

# NullPool: соединение не переиспользуется между тестами — так у каждого теста
# свежее подключение и нет конфликтов event loop.
test_engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


# Схема создаётся один раз на весь прогон и удаляется в конце.
@pytest.fixture(scope="session", autouse=True)
async def prepare_schema():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Перед каждым тестом удаляем все строки. Порядок обратный зависимостям:
# сначала tasks (ссылаются на users), потом users.
@pytest.fixture(autouse=True)
async def clean_tables():
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(delete(table))
    yield


# Тестовая версия get_session — та же схема «открыть, отдать, закрыть»,
# но сессия создаётся на тестовом движке.
async def get_test_session():
    async with TestSession() as session:
        yield session


# Клиент вызывает ASGI-приложение напрямую, без запуска uvicorn.
@pytest.fixture
async def api():
    app.dependency_overrides[get_session] = get_test_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    # Снимаем подмену, чтобы не оставлять глобальное состояние после теста.
    app.dependency_overrides.pop(get_session, None)


# Помощник: создать пользователя и вернуть JSON ответа.
@pytest.fixture
def make_user(api):
    async def _make_user(email="owner@test.io", name="Owner"):
        resp = await api.post("/users", json={"email": email, "name": name})
        assert resp.status_code == 201, resp.text
        return resp.json()

    return _make_user


# Помощник: создать задачу у указанного владельца.
@pytest.fixture
def make_task(api):
    async def _make_task(owner_id, title="Задача", **extra):
        resp = await api.post("/tasks", json={"title": title, "owner_id": owner_id, **extra})
        assert resp.status_code == 201, resp.text
        return resp.json()

    return _make_task
