# Python Final Diplom

## Описание проекта
Backend приложение для интернет-магазина, построенное на Django и Django REST Framework.

## Покрытие тестами
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

## Установка и запуск
1. Клонировать репозиторий
2. Создать виртуальное окружение: `python -m venv .venv`
3. Активировать: `source .venv/bin/activate`
4. Установить зависимости: `pip install -r requirements.txt`
5. Настроить `.env` файл
6. Запустить миграции: `python manage.py migrate`
7. Запустить сервер: `python manage.py runserver`

## Настройка GitHub Actions

Для работы GitHub Actions необходимо:

1. **Создать Gist** для бейджа покрытия:
   - Перейти на https://gist.github.com/
   - Создать новый Gist с файлом `coverage.json`
   - Скопировать Gist ID из URL

2. **Добавить секреты в репозиторий**:
   - Перейти в Settings → Secrets and variables → Actions
   - Добавить `GIST_SECRET` с Personal Access Token

3. **Обновить workflow файл**:
   - В `.github/workflows/badge.yml` заменить `your-gist-id-here` на реальный Gist ID
