# Практическая работа № 3, шаг 5: многоэтапная сборка.
#   wheels  — собирает wheel-файлы всех зависимостей;
#   test    — образ для автотестов (код + dev-зависимости), используется в compose;
#   runtime — финальный образ приложения: только wheels и код, пользователь без root.

ARG PYTHON_IMAGE=python:3.13-slim

# ---------- Этап 1: сборка wheel-файлов ----------
FROM ${PYTHON_IMAGE} AS wheels
WORKDIR /build
COPY requirements.txt requirements-dev.txt ./
# Wheels приложения и dev-wheels складываются в разные папки:
# в финальный образ попадут только первые.
RUN pip wheel --no-cache-dir --wheel-dir /wheels/app -r requirements.txt \
 && pip wheel --no-cache-dir --wheel-dir /wheels/dev -r requirements-dev.txt

# ---------- Этап 2: образ для тестов ----------
FROM ${PYTHON_IMAGE} AS test
WORKDIR /src
COPY --from=wheels /wheels/dev /wheels
# --no-index: ставим только из готовых wheels, без обращения к PyPI.
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl && rm -rf /wheels
COPY . .
CMD ["python", "-m", "pytest", "-v", "-p", "no:cacheprovider"]

# ---------- Этап 3: финальный образ ----------
FROM ${PYTHON_IMAGE} AS runtime

# Не создавать .pyc, сразу выводить логи (без буферизации).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Непривилегированный пользователь с фиксированным UID.
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

WORKDIR /home/appuser/service
COPY --from=wheels /wheels/app /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl && rm -rf /wheels

# Код и миграции принадлежат appuser.
COPY --chown=appuser:appuser alembic.ini ./
COPY --chown=appuser:appuser migrations ./migrations
COPY --chown=appuser:appuser app ./app

# С этой строки процессы контейнера работают без прав root.
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
