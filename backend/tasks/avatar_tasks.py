import os
from celery import shared_task
from PIL import Image
from django.core.files import File
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True)
def process_avatar(self, user_id, image_path):
    """
    Асинхронная обработка аватарки пользователя
    """
    try:
        # Получаем пользователя
        user = User.objects.get(id=user_id)
        
        # Открываем изображение
        with Image.open(image_path) as img:
            # Конвертируем в RGB если нужно
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Создаем разные размеры
            sizes = {
                'small': (100, 100),
                'medium': (200, 200),
                'large': (400, 400)
            }
            
            processed_images = {}
            
            for size_name, dimensions in sizes.items():
                # Изменяем размер с сохранением пропорций
                resized_img = img.copy()
                resized_img.thumbnail(dimensions, Image.Resampling.LANCZOS)
                
                # Создаем путь для сохранения
                filename = f"avatar_{user_id}_{size_name}.jpg"
                save_path = os.path.join(settings.MEDIA_ROOT, 'avatars', 'processed', filename)
                
                # Создаем папку если не существует
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                # Сохраняем изображение
                resized_img.save(save_path, 'JPEG', quality=85, optimize=True)
                processed_images[size_name] = save_path
                
                logger.info(f"Обработана аватарка {size_name} для пользователя {user_id}")
            
            # Обновляем пользователя с новыми аватарками
            user.avatar = File(open(processed_images['medium'], 'rb'))
            user.save(update_fields=['avatar'])
            
            # Очищаем временные файлы
            for path in processed_images.values():
                if os.path.exists(path):
                    os.remove(path)
            
            # Удаляем оригинальный файл
            if os.path.exists(image_path):
                os.remove(image_path)
            
            logger.info(f"Аватарка успешно обработана для пользователя {user_id}")
            return {
                'status': 'success',
                'user_id': user_id,
                'message': 'Аватарка успешно обработана'
            }
            
    except User.DoesNotExist:
        logger.error(f"Пользователь с ID {user_id} не найден")
        return {
            'status': 'error',
            'user_id': user_id,
            'message': 'Пользователь не найден'
        }
    except Exception as e:
        logger.error(f"Ошибка при обработке аватарки для пользователя {user_id}: {str(e)}")
        return {
            'status': 'error',
            'user_id': user_id,
            'message': f'Ошибка обработки: {str(e)}'
        }


@shared_task(bind=True)
def cleanup_old_avatars(self, user_id):
    """
    Очистка старых аватарок пользователя
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Удаляем старую аватарку если есть
        if user.avatar:
            old_avatar_path = user.avatar.path
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)
                logger.info(f"Удалена старая аватарка для пользователя {user_id}")
        
        return {
            'status': 'success',
            'user_id': user_id,
            'message': 'Старые аватарки очищены'
        }
        
    except User.DoesNotExist:
        logger.error(f"Пользователь с ID {user_id} не найден")
        return {
            'status': 'error',
            'user_id': user_id,
            'message': 'Пользователь не найден'
        }
    except Exception as e:
        logger.error(f"Ошибка при очистке аватарок для пользователя {user_id}: {str(e)}")
        return {
            'status': 'error',
            'user_id': user_id,
            'message': f'Ошибка очистки: {str(e)}'
        }
