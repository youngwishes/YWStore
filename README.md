# YWStore - Online Clothing Store 👕

<img src="https://github.com/youngwishes/fastapi-kafka/assets/92817776/19c422d7-806d-4fe4-9773-bd789c2f4e78" width="50" height="50"/>
<img src="https://github.com/youngwishes/fastapi-kafka/assets/92817776/e27bcc09-b947-4b27-88b4-94c6922eecfb" width="50" height="50"/>
<img src="https://github.com/youngwishes/fastapi-kafka/assets/92817776/a9d9c54f-124d-425e-8691-ef11bf131d46" width="50" height="50"/>
<img src="https://github.com/youngwishes/fastapi-kafka/assets/92817776/a824c8aa-89cb-4d22-9706-c2a5affb98a0" width="50" height="50"/>

## Project status - IN WORK ⚙️
Current version exists:

- **User** - register, login, logout.
- **Company** - CRUD-operations. YWStore allows register clothing specialized companyies on platform for the purpose of selling clothes.
- **Employee** - CRUD-operations. Company can add on platform special **users** with roles.
- **Roles**. Any company employee has a role that allows user make some special actions: moderataion, technical support or company administration.  
- **Login/Logout**

## Start locally 🚀

- Create **.env** file
- Copy enviroment variables to **.env** from **.env.example**

```
docker compose up -d --build
```

## Usefull commands
- Create **DB dump** (need project in work state) 💾:
```
docker exec ywstore-postgres /usr/bin/pg_dump -h localhost -U YWStore YWStore > ywstore.sql
```

- **Testing** (need project in work state). Current version has more than **110 tests**🌱:
```
docker exec ywstore-web pytest -W ignore
```
## High Level Architecture 
![Архитектура](https://i.ibb.co/QN355zP/Screenshot-from-2024-01-01-23-16-54.png)
