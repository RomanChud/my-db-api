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

CMD ["gunicorn", "app.route:app", "-b", "0.0.0.0:5000", "--timeout", "120"]
