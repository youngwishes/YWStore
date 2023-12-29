# youngwisheShop
Дипломная работа

Дамп базы данных:

mkdir ./dumps/ && docker exec ywstore-postgres /usr/bin/pg_dump -h localhost -U YWStore YWStore > ./dumps/ywstore.sql
