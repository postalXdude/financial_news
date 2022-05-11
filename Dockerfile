# syntax=docker/Dockerfile:1

FROM python:3.8-alpine

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "manage.py", "runserver"]

EXPOSE 8000
