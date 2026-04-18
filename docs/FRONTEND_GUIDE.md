# Руководство по интеграции фронтенда

Это руководство описывает процесс взаимодействия фронтенда с API Fit-Tracker.

## Аутентификация через Telegram

API использует данные [Telegram Mini App](https://core.telegram.org/bots/webapps#initializing-mini-apps) для аутентификации.

### Процесс входа

1.  Получите строку `initData` из Telegram WebApp API: `window.Telegram.WebApp.initData`.
2.  Отправьте POST запрос на `/auth/telegram`:

```json
{
  "initData": "query_id=...&user=...&auth_date=...&hash=..."
}
```

3.  В ответе вы получите JWT токены:

```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer"
}
```

4.  Используйте `access_token` в заголовке Authorization для всех защищенных запросов:
    `Authorization: Bearer <access_token>`

## Работа с API

### Базовый URL
По умолчанию: `http://localhost:8000`

### Пагинация
Многие списки (например, упражнения) используют пагинацию.
- Параметры запроса: `page` (по умолчанию 1), `size` (по умолчанию 50).
- Формат ответа:
  ```json
  {
    "items": [...],
    "total": 100,
    "page": 1,
    "size": 50,
    "pages": 2
  }
  ```

### Обработка ошибок
- `401 Unauthorized`: Токен недействителен или истек. Перенаправьте пользователя на страницу входа.
- `400 Bad Request`: Ошибка в данных запроса. Подробности в поле `detail`.
- `404 Not Found`: Ресурс не найден.

## Основные эндпоинты

- `GET /users/me`: Информация о текущем пользователе.
- `GET /exercises/`: Список доступных упражнений.
- `POST /workouts/start`: Начать новую тренировку.
- `POST /workouts/{session_id}/complete`: Завершить тренировку.

Полная документация Swagger доступна по адресу `/docs` при запущенном сервере.
