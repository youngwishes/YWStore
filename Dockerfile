FROM python:3.10

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/usr/src/app

COPY poetry.lock pyproject.toml ./

RUN pip install poetry && poetry config virtualenvs.create false && poetry install

COPY . .
