"""ORM-модели.

Шаг 6: модели в стиле SQLAlchemy 2.0 — через Mapped и mapped_column.
Связь «один пользователь — много задач» оформлена через relationship
с параметром back_populates. Поля — по таблице сущностей из раздела 2 задания.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    # Первичный ключ.
    id: Mapped[int] = mapped_column(primary_key=True)
    # Уникальный email — в БД создаётся ограничение UNIQUE.
    email: Mapped[str] = mapped_column(unique=True)
    # Тип колонки выводится из аннотации Mapped[str], NOT NULL — по умолчанию.
    name: Mapped[str]
    # Время создания проставляет сама БД (DEFAULT now()).
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Список задач пользователя; парная сторона связи — Task.owner.
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"

    # Первичный ключ.
    id: Mapped[int] = mapped_column(primary_key=True)
    # Заголовок до 200 символов; минимум 1 символ проверяется в Pydantic-схеме.
    title: Mapped[str] = mapped_column(String(200))
    # Optional делает колонку NULL — описание необязательно.
    description: Mapped[Optional[str]]
    # Признак выполнения, по умолчанию False.
    done: Mapped[bool] = mapped_column(default=False)
    # Время создания проставляет БД.
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    # Внешний ключ на пользователя-владельца.
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Владелец задачи; парная сторона связи — User.tasks.
    owner: Mapped["User"] = relationship(back_populates="tasks")
