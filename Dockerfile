FROM python:3.10-slim

COPY poetry.lock pyproject.toml ./

RUN pip install poetry && poetry config virtualenvs.create false && poetry install

COPY src ./src/

WORKDIR ./src/
