FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y iputils-ping && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY services/ping_monitor/ping_monitor ./ping_monitor

ENV PYTHONPATH=/app

CMD ["python", "-m", "ping_monitor.main"]
