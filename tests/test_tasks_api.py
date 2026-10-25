"""Шаг 4: тесты эндпоинтов /tasks (обязательные пункты 4–8)."""


# Пункт 4: задача создаётся у существующего пользователя.
async def test_create_task_returns_201(api, make_user):
    owner = await make_user()

    resp = await api.post("/tasks", json={"title": "Купить молоко", "owner_id": owner["id"]})

    assert resp.status_code == 201
    task = resp.json()
    assert task["title"] == "Купить молоко"
    assert task["owner_id"] == owner["id"]
    # done не передавали — должно примениться значение по умолчанию.
    assert task["done"] is False


# Пункт 5: владельца с таким id нет — 404.
async def test_create_task_for_missing_owner_returns_404(api):
    resp = await api.post("/tasks", json={"title": "Ничья задача", "owner_id": 424242})

    assert resp.status_code == 404


# Пункт 6: фильтр done и пагинация limit/offset.
async def test_done_filter_and_pagination(api, make_user, make_task):
    owner = await make_user()
    # 2 выполненные и 4 невыполненные задачи.
    for n in range(6):
        await make_task(owner["id"], title=f"t{n}", done=n < 2)

    finished = (await api.get("/tasks", params={"done": "true"})).json()
    assert len(finished) == 2
    assert all(t["done"] for t in finished)

    # Страницы по 3: первая полная, вторая — оставшиеся 3, третья пустая.
    page1 = (await api.get("/tasks", params={"limit": 3, "offset": 0})).json()
    page2 = (await api.get("/tasks", params={"limit": 3, "offset": 3})).json()
    page3 = (await api.get("/tasks", params={"limit": 3, "offset": 6})).json()
    assert len(page1) == 3 and len(page2) == 3 and page3 == []
    # Страницы не пересекаются.
    assert {t["id"] for t in page1}.isdisjoint({t["id"] for t in page2})

    # limit вне диапазона 1–100 отклоняется валидацией.
    assert (await api.get("/tasks", params={"limit": 0})).status_code == 422


# Пункт 7: PATCH меняет только присланные поля.
async def test_patch_updates_only_sent_fields(api, make_user, make_task):
    owner = await make_user()
    task = await make_task(owner["id"], title="Исходное", description="Описание")

    resp = await api.patch(f"/tasks/{task['id']}", json={"title": "Новое"})

    assert resp.status_code == 200
    updated = resp.json()
    assert updated["title"] == "Новое"
    # Поля, которых не было в запросе, сохранили прежние значения.
    assert updated["description"] == "Описание"
    assert updated["done"] is False


# Пункт 8: после удаления задача больше не находится.
async def test_deleted_task_is_not_found(api, make_user, make_task):
    owner = await make_user()
    task = await make_task(owner["id"])

    assert (await api.delete(f"/tasks/{task['id']}")).status_code == 204
    assert (await api.get(f"/tasks/{task['id']}")).status_code == 200  # BROKEN: шаг 8, ожидается 404
