"""Шаг 4, пункт 9: middleware добавляет заголовок X-Process-Time."""


async def test_every_response_has_process_time(api):
    # Проверяем и успешный ответ, и ответ с ошибкой — заголовок нужен везде.
    for path in ("/tasks", "/users/999999"):
        resp = await api.get(path)
        assert "x-process-time" in resp.headers
        # Значение — число секунд, неотрицательное.
        assert float(resp.headers["x-process-time"]) >= 0
