"""Pydantic-схемы.

Шаг 7: для каждой сущности отдельные схемы *Create, *Read и *Update.
- В *Update все поля необязательны (PATCH передаёт только изменяемые поля).
- В *Read включено from_attributes=True — схема строится из ORM-объекта.
- Для email используется тип EmailStr (нужен пакет email-validator).
Общие поля вынесены в базовые классы UserBase и TaskBase.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# ---------- User ----------

# Общие поля пользователя для Create и Read.
class UserBase(BaseModel):
    email: EmailStr
    name: str


# Тело запроса POST /users.
class UserCreate(UserBase):
    pass


# Частичное обновление пользователя: все поля необязательны.
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None


# Ответ API с данными пользователя.
class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ---------- Task ----------

# Общие поля задачи для Create и Read.
class TaskBase(BaseModel):
    # Длина заголовка 1–200 символов по заданию; нарушение даёт 422.
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    done: bool = False


# Тело запроса POST /tasks: к общим полям добавляется владелец.
class TaskCreate(TaskBase):
    owner_id: int


# Тело запроса PATCH /tasks/{id}: все поля необязательны,
# ограничение длины title сохраняется.
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title", "done")
    @classmethod
    def reject_null_for_required_fields(cls, value):
        if value is None:
            raise ValueError("Field cannot be null")
        return value


# Ответ API с данными задачи.
class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    owner_id: int
