"""Точка входа приложения.

Шаг 1: создание приложения и подключение роутеров.
Шаг 10: middleware (Starlette) — заголовок X-Process-Time и лог запросов.
Запуск (шаг 11): uvicorn app.main:app --reload
"""

import logging
import time

from fastapi import FastAPI, Request

from app.routers import tasks, users

# Логгер uvicorn уже настроен сервером и выводит сообщения уровня INFO в консоль.
logger = logging.getLogger("uvicorn.error")

app = FastAPI()


# Декоратор @app.middleware("http") регистрирует функцию как middleware Starlette:
# она вызывается на каждый HTTP-запрос до и после обработчика.
@app.middleware("http")
async def process_time_middleware(request: Request, call_next):
    started = time.time()
    # Передаём запрос дальше — роутеру и обработчику эндпоинта.
    response = await call_next(request)
    duration = time.time() - started
    # Время обработки в секундах добавляется в заголовок ответа.
    response.headers["X-Process-Time"] = str(duration)
    # В лог пишутся метод, путь, статус и время обработки.
    logger.info(
        f"{request.method} {request.url.path} {response.status_code} {duration:.4f}s"
    )
    return response


# Подключение роутеров пользователей и задач (шаг 8).
app.include_router(users.router)
app.include_router(tasks.router)
