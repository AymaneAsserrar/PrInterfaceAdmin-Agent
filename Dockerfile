FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ACCESS_LOG_PATH=/app/logs/access.log \
    ERROR_LOG_PATH=/app/logs/error.log

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev

WORKDIR /app

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && \
    chmod 777 /app/logs && \
    touch /app/logs/access.log /app/logs/error.log && \
    chmod 666 /app/logs/access.log /app/logs/error.log

VOLUME ["/app/logs"]
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
EXPOSE 8000
CMD ["python", "src/main.py"]