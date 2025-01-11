FROM python:3.12-alpine


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev


WORKDIR /app

COPY requirements.txt /app/requirements.txt


RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000


CMD ["python", "src/main.py"]