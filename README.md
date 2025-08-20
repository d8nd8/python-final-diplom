# Дипломный проект профессии «Python-разработчик: расширенный курс»

Это Django REST Framework приложение для автоматизации закупок в розничной сети.

## Содержание

- [Функции](#функции)
- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
  - [Клонирование репозитория](#клонирование-репозитория)
  - [Настройка окружения](#настройка-окружения)
  - [Локальный запуск](#локальный-запуск)
  - [Запуск через Docker](#запуск-через-docker)
- [Переменные окружения](#переменные-окружения)
- [API документация](#api-документация)
- [Тестирование](#тестирование)
- [GitHub Actions](#github-actions)
- [Полезные ссылки](#полезные-ссылки)

## Функции

- Регистрация, аутентификация пользователей
- CRUD операций с каталогом товаров
- Импорт прайсов поставщиков
- Управление корзиной и оформлением заказов
- Отправка email с подтверждением заказа
- Администрирование статусов заказов
- **OAuth2 авторизация через VK и GitHub**
- **Асинхронная загрузка аватарок пользователей (Celery)**
- **Мониторинг ошибок и производительности (Sentry)**

## Требования

- Python 3.10+
- pip
- virtualenv (рекомендуется)
- Docker (для контейнеризации)
- docker-compose

## Быстрый старт

### Клонирование репозитория

```bash
git clone https://github.com/yourusername/python-final-diplom.git
cd python-final-diplom
```

### Настройка окружения

1. Создать и активировать виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   .\.venv\Scripts\activate   # Windows
   ```

2. Установить зависимости:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Скопировать файл `.env.sample` или создать `.env` на основе шаблона и заполнить переменные (см. ниже).

### Локальный запуск

1. Применить миграции:
   ```bash
   python manage.py migrate
   ```

2. Собрать статические файлы:
   ```bash
   python manage.py collectstatic --no-input
   ```

3. Запустить сервер разработки:
   ```bash
   python manage.py runserver
   ```

4. Перейти в браузере по адресу: `http://localhost:8000`.

### Запуск через Docker

1. Собрать и запустить контейнеры:
   ```bash
   docker-compose up --build -d
   ```

2. Проверить логи и статус:
   ```bash
   docker-compose ps
   docker-compose logs web
   ```

3. Применить миграции (если требуется):
   ```bash
   docker-compose exec web python manage.py migrate --no-input
   ```

4. Приложение доступно на `http://localhost:8000`.

#### Docker сервисы
- **web** - Django приложение
- **redis** - Redis для Celery брокера
- **celery** - Celery worker для асинхронных задач
- **celery-beat** - Celery beat для периодических задач

## Переменные окружения

Пример `.env`:

```dotenv
DB_ENGINE=django.db.backends.postgresql
DB_NAME=netologydb
DB_USER=diplomuser
DB_PASSWORD=diplom1
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Social Authentication
GITHUB_OAUTH2_KEY=your_github_oauth_key
GITHUB_OAUTH2_SECRET=your_github_oauth_secret
VK_OAUTH2_KEY=your_vk_oauth_key
VK_OAUTH2_SECRET=your_vk_oauth_secret

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Sentry (опционально)
SENTRY_DSN=your_sentry_dsn_here
SENTRY_ENVIRONMENT=development
```

### Настройка Sentry

Для мониторинга ошибок и производительности:

1. Создать проект на [sentry.io](https://sentry.io)
2. Получить DSN из настроек проекта
3. Добавить в `.env`: `SENTRY_DSN=your_dsn_here`

**Готово!** Sentry автоматически начнет отслеживать ошибки и производительность.

> **Примечание:** Код Sentry уже готов к работе. Если DSN не указан, приложение будет работать без мониторинга, но все функции останутся доступными.

## API документация

- Swagger: `http://localhost:8000/api/swagger/`
- OpenAPI схема: `http://localhost:8000/api/schema/`

### Новые API endpoints

#### Социальная авторизация
- `GET /api/social-auth/providers/` - список доступных провайдеров
- `GET /api/social-auth/status/` - статус авторизации пользователя
- `GET /api/social-auth/callback/` - callback для OAuth2

#### Управление аватарками
- `POST /api/profile/avatar/upload/` - загрузка аватарки (асинхронно)
- `GET /api/profile/avatar/status/` - статус обработки аватарки

#### Тестирование Sentry
- `GET /api/test/sentry/?error_type=...` - тест различных типов ошибок
- `POST /api/test/sentry/` - тест отправки ошибок через POST

## Тестирование

### Покрытие тестами
Текущее покрытие модуля `backend/views.py` составляет **52%**, что превышает минимальную цель в 30-40%.

[![Coverage](https://img.shields.io/badge/coverage-52%25-green)](https://github.com/yourusername/python-final-diplom)

### Запуск тестов
```bash
# Активация виртуального окружения
source .venv/bin/activate

# Запуск тестов
python manage.py test backend.test_views

# Запуск тестов с coverage
coverage run --source=backend manage.py test backend.test_views
coverage report
coverage html  # Создает HTML отчет в папке htmlcov/
```

### Структура тестов
- `TestRegisterView` - тесты для регистрации пользователей
- `TestLoginView` - тесты для входа в систему
- `TestProductListView` - тесты для списка товаров
- `TestPartnerUpdateView` - тесты для обновления товаров партнера
- `TestViewsEdgeCases` - тесты для edge cases

Всего: **17 тестов** успешно проходят.

## GitHub Actions

Проект настроен с автоматическими GitHub Actions для отслеживания покрытия тестами:

### Coverage Report
- Автоматически запускается при создании Pull Request
- Публикует отчет о покрытии в комментариях PR
- Проверяет минимальное покрытие (50% для всех файлов, 60% для новых)

### Coverage Badge
- Автоматически обновляет бейдж покрытия в README
- Показывает текущий процент покрытия тестами

### Настройка GitHub Actions

Для работы GitHub Actions необходимо:

1. **Создать Gist** для бейджа покрытия:
   - Перейти на https://gist.github.com/
   - Создать новый Gist с файлом `coverage.json`
   - Скопировать Gist ID из URL

2. **Добавить секреты в репозиторий**:
   - Перейти в Settings → Secrets and variables → Actions
   - Добавить `GIST_SECRET` с Personal Access Token

3. **Обновить workflow файл**:
   - В `.github/workflows/badge.yml` заменить Gist ID на реальный

## Полезные ссылки

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Python Coverage](https://coverage.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)
