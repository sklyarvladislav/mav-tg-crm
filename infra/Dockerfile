FROM alpine:3.20 AS base-image 
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PROJECT_PATH=/app
WORKDIR $PROJECT_PATH

RUN apk update && apk add --no-cache python3~=3.12 git

# Устанавливаем зависимости (без проекта, только lockfile)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable 

FROM base-image AS development-image

WORKDIR $PROJECT_PATH

# Копируем src в контейнер
COPY --chown=user:user ../src $PROJECT_PATH/src 
COPY --chown=user:user ../alembic.ini $PROJECT_PATH/alembic.ini
# Команда по умолчанию (будет переопределяться в docker-compose)
CMD ["/bin/sh"]
