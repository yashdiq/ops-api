FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY .env.production .env

COPY uv.lock pyproject.toml ./

RUN pip install uv && uv sync

COPY . .

EXPOSE 8000

CMD ["uv", "run", "daphne", "config.asgi:application", "-b", "0.0.0.0", "-p", "8000"]
