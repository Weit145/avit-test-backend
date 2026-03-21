FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Установка Poetry
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false

# Установка зависимостей
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

# Копируем код
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]