"""Шаг 9: первая миграция, создана alembic revision --autogenerate.

Создаёт таблицы users и tasks. Применение: alembic upgrade head.

Создание таблиц пользователей и задач.

Идентификатор ревизии: 23d477a6e14b
Предыдущая ревизия:
Дата создания: 2026-10-13 17:42:32.349900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Идентификаторы ревизии, используемые Alembic.
revision: str = '23d477a6e14b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Применить изменения схемы."""
    # Команды сгенерированы Alembic автоматически.
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('done', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # Конец автоматически сгенерированных команд.


def downgrade() -> None:
    """Откатить изменения схемы."""
    # Команды сгенерированы Alembic автоматически.
    op.drop_table('tasks')
    op.drop_table('users')
    # Конец автоматически сгенерированных команд.
