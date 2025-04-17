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
curl -X POST "http://localhost:5000/register/" \
     -H "Content-Type: application/json" \
     -d '{
           "username": "testuser2",
           "email": "test2@example.com",
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
curl -X POST "http://localhost:5000/login/" \
     -H "Content-Type: application/json" \
     -d '{
           "username": "testuser2",
           "password": "12345678"
         }'

```

Получаем данные по токену
```bash
curl -v -L GET "http://localhost:8080/profile/"      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0MTk2OTc2NX0.M-hDNjGh1a01riBEhFFWQjlieH-kaoAWZreS117N1cs"
```

### 3. Обновление данных 
```bash
curl -X PUT "http://localhost:8000/profile/" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0MTk2OTc2NX0.M-hDNjGh1a01riBEhFFWQjlieH-kaoAWZreS117N1cs" -H "Content-Type: application/json" -d '{
  "first_name": "Johnny",
  "last_name": "Doe",
  "birth_date": "1990-01-01",
  "phone": "0987654321"
}'
```

### 4.Создание поста
```bash
curl -X POST "http://localhost:5000/posts" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NDQ3NDEyMzB9.cJxXfsbOsW9KIq6vOwJ0z045Y7zyLVzHxCbQjBGtHss" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Hello world",
        "description": "This is my first post",
        "is_private": false,
        "tags": ["test", "grpc"]
      }'
```

### 5. Обновление поста
```bash
curl -X PUT http://localhost:5000/posts/e8245d32-3753-427a-be74-f5ba8e3e6744 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NDQ3NDEyMzB9.cJxXfsbOsW9KIq6vOwJ0z045Y7zyLVzHxCbQjBGtHss" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Обновлённый заголовок",
        "description": "Новый текст поста",
        "is_private": true,
        "tags": ["обновлено", "grpc"]
      }'
```
### 6.Метод получения пагинированного списка постов
```bash
curl -X GET "http://localhost:5000/posts?page=1&limit=5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NDQ3NDEyMzB9.cJxXfsbOsW9KIq6vOwJ0z045Y7zyLVzHxCbQjBGtHss"
```
### 7. Удаление поста
```bash
curl -X DELETE http://localhost:5000/posts/e8245d32-3753-427a-be74-f5ba8e3e6744 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NDQ3NDEyMzB9.cJxXfsbOsW9KIq6vOwJ0z045Y7zyLVzHxCbQjBGtHss"
```
### 8. Получение поста по id
```bash
curl -X GET http://localhost:5000/posts/e8245d32-3753-427a-be74-f5ba8e3e6744 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NDQ3NDEyMzB9.cJxXfsbOsW9KIq6vOwJ0z045Y7zyLVzHxCbQjBGtHss"
```