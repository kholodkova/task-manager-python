"""Шаг 4: тесты эндпоинтов /users (обязательные пункты 1–3)."""

import pytest


class TestCreateUser:
    # Пункт 1: успешное создание — 201 и поля, которые проставил сервер.
    async def test_returns_201(self, api):
        resp = await api.post("/users", json={"email": "ivan@test.io", "name": "Иван"})

        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "ivan@test.io"
        assert data["name"] == "Иван"
        # id и created_at ставит база, клиент их не передаёт.
        assert "id" in data and "created_at" in data

    # Пункт 2: email уникален — повторная регистрация даёт 409.
    async def test_same_email_twice_returns_409(self, api, make_user):
        await make_user(email="dup@test.io")

        resp = await api.post("/users", json={"email": "dup@test.io", "name": "Другой"})

        assert resp.status_code == 409

    # Пункт 3: несколько вариантов некорректного email — каждый даёт 422.
    @pytest.mark.parametrize("bad_email", ["plainaddress", "no-domain@", "@no-user.io"])
    async def test_bad_email_returns_422(self, api, bad_email):
        resp = await api.post("/users", json={"email": bad_email, "name": "X"})

        assert resp.status_code == 422
