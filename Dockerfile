FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    default-jre \
    lua5.1 \
    lua5.2 \
    lua5.3 \
    lua5.4 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
