"""Эндпоинты задач.

Шаг 8: роутер на APIRouter, сессия только через Depends(get_session),
ошибки через HTTPException с кодами из таблицы задания:
  POST   /tasks      — 201, 404 (нет владельца), 422
  GET    /tasks      — 200; фильтры done, owner_id; пагинация limit (1–100), offset
  GET    /tasks/{id} — 200, 404
  PATCH  /tasks/{id} — 200, 404, 422
  DELETE /tasks/{id} — 204, 404
Код 422 FastAPI возвращает сам при ошибке валидации тела или параметров.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Task, User
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Создать задачу; 404, если пользователя-владельца нет.
@router.post("", response_model=TaskRead, status_code=201)
async def create_task(payload: TaskCreate, session: AsyncSession = Depends(get_session)):
    owner = await session.get(User, payload.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    task = Task(**payload.model_dump())
    session.add(task)
    await session.commit()
    # Перечитываем объект, чтобы получить id и created_at, проставленные БД.
    await session.refresh(task)
    return task


# Список задач с фильтрами и пагинацией.
@router.get("", response_model=list[TaskRead])
async def read_tasks(
    # Фильтры необязательны: если параметр не передан, условие не добавляется.
    done: Optional[bool] = None,
    owner_id: Optional[int] = None,
    # limit от 1 до 100 по заданию; значение вне диапазона даёт 422.
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Task)
    if done is not None:
        stmt = stmt.where(Task.done == done)
    if owner_id is not None:
        stmt = stmt.where(Task.owner_id == owner_id)
    result = await session.execute(stmt.offset(offset).limit(limit))
    return result.scalars().all()


# Получить задачу по id; 404, если такой нет.
@router.get("/{id}", response_model=TaskRead)
async def read_task(id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# Частично обновить задачу; 404, если такой нет.
@router.patch("/{id}", response_model=TaskRead)
async def update_task(
    id: int, payload: TaskUpdate, session: AsyncSession = Depends(get_session)
):
    task = await session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # exclude_unset=True — в словарь попадают только поля, переданные клиентом,
    # поэтому остальные поля задачи не меняются.
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    await session.commit()
    await session.refresh(task)
    return task


# Удалить задачу; при успехе 204 без тела ответа, 404, если такой нет.
@router.delete("/{id}", status_code=204)
async def delete_task(id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()
