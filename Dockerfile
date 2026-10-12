
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/ ./requirements/

RUN pip install --no-cache-dir -r requirements/prod.txt

COPY . .

RUN SECRET_KEY="build-only-not-for-production" \
    python manage.py collectstatic --noinput --settings=shopcart.settings.prod
    
EXPOSE 8000

CMD ["sh", "-c", "uvicorn shopcart.asgi:application --host 0.0.0.0 --port ${PORT:-8000}"]
