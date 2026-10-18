"""Настройки приложения.

Шаг 4: строка подключения к БД не записана в коде — она читается из переменной
окружения DATABASE_URL с помощью pydantic-settings.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Значение берётся из переменной окружения DATABASE_URL, а если её нет —
    # из файла .env в корне проекта (образец — .env.example из структуры шага 1).
    model_config = SettingsConfigDict(env_file=".env")

    # Значения по умолчанию нет: без DATABASE_URL приложение не запустится
    # и сообщит об ошибке валидации.
    DATABASE_URL: str


# Настройки создаются один раз при первом вызове, дальше возвращается тот же объект.
@lru_cache
def get_settings() -> Settings:
    return Settings()
