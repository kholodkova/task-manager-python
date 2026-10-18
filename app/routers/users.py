"""Эндпоинты пользователей.

Шаг 8: роутер на APIRouter, сессия только через Depends(get_session),
ошибки через HTTPException с кодами из таблицы задания:
  POST /users      — 201, 409 (email занят), 422
  GET  /users/{id} — 200, 404
Код 422 FastAPI возвращает сам, если тело запроса не прошло валидацию схемы.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


# Создать пользователя.
@router.post("", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    user = User(email=payload.email, name=payload.name)
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        # БД отклонила вставку из-за UNIQUE на email — email уже занят.
        await session.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    # Перечитываем объект, чтобы получить id и created_at, проставленные БД.
    await session.refresh(user)
    return user


# Получить пользователя по id; 404, если такого нет.
@router.get("/{id}", response_model=UserRead)
async def read_user(id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
