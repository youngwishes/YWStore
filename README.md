# YWStore
Дипломная работа

## Локальный запуск 🚀

- Создать в корне репозитория .env
- Скопировать настройки из .env.example
- Запросить дамп БД
- Создать в корне репозитория директорию dumps:
```
mkdir dumps
```
- Положить дамп в эту директорию
- Запустить контейнеры:
```
docker compose up -d --build
```

## Полезные команды
- Дамп базы данных (предварительно подняты все контейнеры):
```
docker exec ywstore-postgres /usr/bin/pg_dump -h localhost -U YWStore YWStore > ywstore.sql
```

## Архитектура приложения
![Архитектура](https://i.ibb.co/QN355zP/Screenshot-from-2024-01-01-23-16-54.png)
