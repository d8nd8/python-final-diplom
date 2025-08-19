# Настройка OAuth2 авторизации через VK и GitHub

## Что это дает:

Простая интеграция с социальными сетями для авторизации пользователей через API.

## 1. Установка зависимостей

В `requirements.txt` уже добавлены:
```
social-auth-app-django==5.4.0
requests-oauthlib==1.3.1
```

## 2. Переменные окружения

Создайте файл `.env` в корне проекта:

```bash
# VK OAuth2
VK_OAUTH2_KEY=your_vk_oauth2_key_here
VK_OAUTH2_SECRET=your_vk_oauth2_secret_here

# GitHub OAuth2
GITHUB_OAUTH2_KEY=your_github_oauth2_key_here
GITHUB_OAUTH2_SECRET=your_github_oauth2_secret_here
```

## 3. Получение OAuth2 ключей

### VK OAuth2
1. Перейдите в [VK Developers](https://vk.com/dev)
2. Создайте новое приложение
3. Получите Client ID и Client Secret
4. Добавьте redirect URI: `http://localhost:8000/api/oauth/vk/callback/`

### GitHub OAuth2
1. Перейдите в [GitHub Settings > Developer settings > OAuth Apps](https://github.com/settings/developers)
2. Создайте новое OAuth App
3. Homepage URL: `http://localhost:8000`
4. Authorization callback URL: `http://localhost:8000/api/oauth/github/callback/`

## 4. API Endpoints

После настройки у вас будут доступны:

- **GET** `/api/oauth/vk/` - получить URL для авторизации через VK
- **GET** `/api/oauth/github/` - получить URL для авторизации через GitHub

## 5. Как использовать

### Шаг 1: Получить URL для авторизации
```bash
GET /api/oauth/vk/
Response: {"auth_url": "https://oauth.vk.com/authorize?...", "provider": "vk"}
```

### Шаг 2: Перенаправить пользователя на полученный URL
Пользователь переходит по ссылке и авторизуется в соцсети

### Шаг 3: Обработать callback
Пользователь возвращается с кодом авторизации

## 6. Тестирование

1. Установите зависимости: `pip install -r requirements.txt`
2. Запустите сервер: `python manage.py runserver`
3. Проверьте endpoints:
   - `http://localhost:8000/api/oauth/vk/`
   - `http://localhost:8000/api/oauth/github/`

## 7. Дальнейшее развитие

Для полной интеграции нужно добавить:
- Обработку callback'ов
- Создание/обновление пользователей
- JWT токены для авторизованных пользователей
- Обработку ошибок авторизации
