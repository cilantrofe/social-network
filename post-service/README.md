# Post Service

## Зоны ответственности

- **Управление постами**: Создание, обновление и удаление постов.
- **Управление комментариями**: Создание и управление комментариями к постам.
- **Хранение данных постов**: Управление информацией о постах и комментариях.

## Границы сервиса

- Взаимодействует с `api-gateway` для обработки запросов, связанных с постами, комментариями, лайками.
- Отправляет события постов (например, создание, удаление) в брокер сообщений, также подписывается для асинхронной интеграции.
- Хранит данные постов и комментариев в **Cassandra**.
