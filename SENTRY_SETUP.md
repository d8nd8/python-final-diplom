# Настройка Sentry для мониторинга ошибок

## Что такое Sentry?

Sentry - это платформа для мониторинга ошибок и производительности приложений в реальном времени. Она позволяет:

- Отслеживать ошибки и исключения
- Мониторить производительность приложения
- Получать уведомления о проблемах
- Анализировать стек-трейсы ошибок
- Группировать похожие ошибки

## Установка

Sentry SDK уже добавлен в `requirements.txt`:

```bash
pip install "sentry-sdk[django]==1.45.0"
```

## Настройка

### 1. Создание проекта в Sentry

1. Зайдите на [sentry.io](https://sentry.io)
2. Создайте аккаунт или войдите в существующий
3. Создайте новый проект для Django
4. Скопируйте DSN (Data Source Name)

### 2. Обновление настроек

В файле `orders/settings.py` замените placeholder DSN на ваш реальный:

```python
sentry_sdk.init(
    dsn="https://YOUR_ACTUAL_DSN_HERE@your-instance.ingest.sentry.io/YOUR_PROJECT_ID",
    # ... остальные настройки
)
```

### 3. Переменные окружения (рекомендуется)

Создайте файл `.env` и добавьте:

```env
SENTRY_DSN=https://your-actual-dsn-here@your-instance.ingest.sentry.io/your-project-id
SENTRY_ENVIRONMENT=development
```

Затем обновите `settings.py`:

```python
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN', 'https://your-sentry-dsn-here@your-instance.ingest.sentry.io/your-project-id'),
    environment=os.getenv('SENTRY_ENVIRONMENT', 'development'),
    # ... остальные настройки
)
```

## Тестирование

### API Endpoint для тестирования

Создан специальный endpoint для тестирования Sentry:

```
GET /api/test/sentry/
POST /api/test/sentry/
```

### Параметры GET запроса

- `error_type=exception` - вызывает обычное исключение
- `error_type=validation` - вызывает ошибку валидации
- `error_type=custom` - кастомная ошибка с дополнительным контекстом
- `error_type=performance` - тест производительности

### Примеры тестирования

```bash
# Простое исключение
curl "http://localhost:8000/api/test/sentry/?error_type=exception"

# Ошибка валидации
curl "http://localhost:8000/api/test/sentry/?error_type=validation"

# Кастомная ошибка
curl "http://localhost:8000/api/test/sentry/?error_type=custom"

# Тест производительности
curl "http://localhost:8000/api/test/sentry/?error_type=performance"
```

### POST запрос

```bash
# Успешный запрос
curl -X POST "http://localhost:8000/api/test/sentry/" \
  -H "Content-Type: application/json" \
  -d '{"test_field": "value"}'

# Запрос с ошибкой
curl -X POST "http://localhost:8000/api/test/sentry/" \
  -H "Content-Type: application/json" \
  -d '{"test_field": "value", "trigger_error": true}'
```

## Возможности Sentry

### 1. Мониторинг ошибок

- Автоматический сбор исключений
- Группировка похожих ошибок
- Детальные стек-трейсы
- Контекст ошибки (заголовки, параметры, пользователь)

### 2. Мониторинг производительности

- Трассировка запросов
- Измерение времени выполнения
- Анализ медленных запросов
- Профилирование кода

### 3. Кастомные события

```python
import sentry_sdk

# Отправка сообщения
sentry_sdk.capture_message("Важное событие", level="info")

# Отправка исключения
try:
    # код
except Exception as e:
    sentry_sdk.capture_exception(e)

# Кастомные данные
with sentry_sdk.push_scope() as scope:
    scope.set_tag("user_action", "purchase")
    scope.set_extra("order_id", 12345)
    # код
```

### 4. Контекст пользователя

```python
sentry_sdk.set_user({
    "id": user.id,
    "username": user.username,
    "email": user.email
})
```

## Docker интеграция

Для Docker окружения добавьте переменные окружения в `docker-compose.yml`:

```yaml
environment:
  - SENTRY_DSN=${SENTRY_DSN}
  - SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT}
```

## Мониторинг в продакшене

1. Установите `environment="production"`
2. Отключите `debug=False`
3. Настройте фильтрацию чувствительных данных
4. Настройте алерты и уведомления

## Преимущества для резюме

Знание Sentry показывает:

- Понимание важности мониторинга в продакшене
- Опыт с современными инструментами DevOps
- Умение настраивать системы логирования и отслеживания ошибок
- Знание лучших практик для коммерческих проектов

## Полезные ссылки

- [Документация Sentry](https://docs.sentry.io/)
- [Django интеграция](https://docs.sentry.io/platforms/python/django/)
- [API Reference](https://docs.sentry.io/platforms/python/)
- [Best Practices](https://docs.sentry.io/platforms/python/guides/django/best-practices/)
