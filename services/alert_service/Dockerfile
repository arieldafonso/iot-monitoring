FROM python:3.11-slim

WORKDIR /app

COPY services/alert_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY services/alert_service/alert_service ./alert_service

ENV PYTHONPATH=/app

CMD ["python", "-m", "alert_service.main"]
