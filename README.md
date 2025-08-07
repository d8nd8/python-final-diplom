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
- [Полезные ссылки](#полезные-ссылки)

## Функции

- Регистрация, аутентификация пользователей
- CRUD операций с каталогом товаров
- Импорт прайсов поставщиков
- Управление корзиной и оформлением заказов
- Отправка email с подтверждением заказа
- Администрирование статусов заказов

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
```

## API документация

- Swagger: `http://localhost:8000/api/swagger/`
- OpenAPI схема: `http://localhost:8000/api/schema/`
