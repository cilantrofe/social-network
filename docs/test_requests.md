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
           "username": "testuser",
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
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NDc2ODYwODV9.Lk0Zmwc1gp5rLBTed9yfCW-CuL8uXveG_srsnqpskE4" \
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
curl -X PUT http://localhost:5000/posts/31a56f0c-cae4-4946-839d-2dfbc71fcaa0 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NDQ5OTE4MDV9.qZiuiDvJr3abx3KnzF5Ef06jULoX6LjOl4QsNkjab98" \
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
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NDc2ODYwODV9.Lk0Zmwc1gp5rLBTed9yfCW-CuL8uXveG_srsnqpskE4"
```
### 7. Удаление поста
```bash
curl -X DELETE http://localhost:5000/posts/31a56f0c-cae4-4946-839d-2dfbc71fcaa0 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NDQ5OTE4MDV9.qZiuiDvJr3abx3KnzF5Ef06jULoX6LjOl4QsNkjab98"
```
### 8. Получение поста по id
```bash
curl -X GET http://localhost:5000/posts/31a56f0c-cae4-4946-839d-2dfbc71fcaa0 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NDQ5OTE4MDV9.qZiuiDvJr3abx3KnzF5Ef06jULoX6LjOl4QsNkjab98"
```

### 9. Лайк поста по id
```bash
curl -X POST "http://localhost:5000/posts/c1cc31f7-a7c2-4f72-8355-366ad1acab8e/like" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0Nzc2NjQ2NH0.nK3_Vk6BCWRgAaeOa7EP3sQ1Ofo7nDh3EH2sqbBVFWQ"
```

### 10. Просмотр поста по id
```bash
curl -X POST "http://localhost:5000/posts/c1cc31f7-a7c2-4f72-8355-366ad1acab8e/view?entity_type=post" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0Nzc2NjQ2NH0.nK3_Vk6BCWRgAaeOa7EP3sQ1Ofo7nDh3EH2sqbBVFWQ"
```

### 11. Комментирование поста
```bash
curl -X POST "http://localhost:5000/posts/c1cc31f7-a7c2-4f72-8355-366ad1acab8e/comments" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0Nzc2NjQ2NH0.nK3_Vk6BCWRgAaeOa7EP3sQ1Ofo7nDh3EH2sqbBVFWQ" \
-H "Content-Type: application/json" \
-d '{"content": "Это тестовый комментарий"}'
```

### 12. Получение комментариев
```bash
curl "http://localhost:5000/posts/c1cc31f7-a7c2-4f72-8355-366ad1acab8e/comments?entity_type=post&page=1&per_page=10" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0Nzc2NjQ2NH0.nK3_Vk6BCWRgAaeOa7EP3sQ1Ofo7nDh3EH2sqbBVFWQ"
```
