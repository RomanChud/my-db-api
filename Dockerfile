FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Используйте gunicorn для запуска
CMD ["gunicorn", "run:route_run", "-b", "0.0.0.0:5000"]
