FROM python:3.12-slim

WORKDIR /app

COPY requirements/prod.txt .

RUN pip install --no-cache-dir -r prod.txt

COPY . .

EXPOSE 8000


CMD ["uvicorn", "shopcart.asgi:application", "--host", "0.0.0.0", "--port", "8000"]