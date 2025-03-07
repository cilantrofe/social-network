# Тестовые запросы
### 0. Запуск и подключение к БД
```bash
sudo docker-compose up --build
```

```bash
sudo docker exec -it users_db psql -U user -d users_db
```
### 1. Регистрация нового пользователя в системе через логин, пароль и элктронную почту
```bash
curl -X POST "http://localhost:8080/register/" \
     -H "Content-Type: application/json" \
     -d '{
           "username": "testuser",
           "email": "test@example.com",
           "password": "12345678",
           "first_name": "John",
           "last_name": "Doe",
           "birth_date": "2000-01-01",
           "phone": "1234567890"
         }'

```

### 2. Получение данных/логиниться
Получаем токен
```bash
curl -X POST "http://localhost:8080/login/" \
     -H "Content-Type: application/json" \
     -d '{
           "username": "testuser",
           "password": "12345678"
         }'

```

Получаем данные по токену
```bash
curl -v -L -X GET "http://localhost:8080/profile/"      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0MTI4ODY2OX0.gV8mxMHYQaFGHgPob29CH3nI2OkXcOPoLZP6jeJurR8"
```

### 3. Обновление данных 
```bash
curl -X PUT "http://localhost:8000/profile/" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0MTI5Mjg4N30.nNY8p72xvABH1I_L8GFPEsUCSgcW3jP_pnW6ojokh5Y" -H "Content-Type: application/json" -d '{
  "first_name": "Johnny",
  "last_name": "Doe",
  "birth_date": "1990-01-01",
  "phone": "0987654321"
}'
```