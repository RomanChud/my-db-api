FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8f28-dafb585edee3/msodbcsql18_18.3.2.1-1_amd64.deb \
    && apt-get install -y ./msodbcsql18_18.3.2.1-1_amd64.deb \
    && apt-get install -y unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm msodbcsql18_18.3.2.1-1_amd64.deb

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app.route:app", "-b", "0.0.0.0:5000", "--timeout", "120"]
