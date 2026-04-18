FROM python:3.12-slim

# Установка системных зависимостей, если понадобятся (например, для компиляции некоторых пакетов)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Настройка PYTHONPATH
ENV PYTHONPATH=/app

# Создание директории для статических файлов и БД (если она в корне)
RUN mkdir -p static/uploads

# Открытие порта
EXPOSE 8000

# Запуск миграций и приложения
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
