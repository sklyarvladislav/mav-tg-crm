FROM alpine:3.20 AS base-image 
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PROJECT_PATH=/app
WORKDIR $PROJECT_PATH

RUN apk update && apk add python3~=3.12 git

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable 

FROM base-image AS development-image

WORKDIR $PROJECT_PATH

COPY --chown=user:user ../src $PROJECT_PATH/src 

CMD ["/bin/uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--reload-include", "*.py, *.toml"]
