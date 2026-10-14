
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/ ./requirements/

RUN pip install --no-cache-dir -r requirements/prod.txt

RUN groupadd --system shopcart && \
    useradd --system --gid shopcart --home-dir /app --shell /usr/sbin/nologin shopcart

COPY --chown=shopcart:shopcart . .
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint

RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint && \
    chmod 755 /usr/local/bin/docker-entrypoint && \
    mkdir -p staticfiles media logs && \
    chown shopcart:shopcart staticfiles media logs

ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput --upload-unhashed-files && exec uvicorn shopcart.asgi:application --host 0.0.0.0 --port ${PORT:-8000}"]
