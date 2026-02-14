import os

from django.apps import AppConfig
from django.conf import settings


class BackendConfig(AppConfig):
    """
    Конфигурация приложения backend.

    Отвечает за настройку приложения при запуске Django, включая
    создание необходимых директорий и регистрацию сигналов.

    Attributes:
        default_auto_field (str): Тип поля для автоматических первичных ключей.
        name (str): Имя приложения (должно соответствовать структуре проекта).
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend"

    def ready(self):
        """
        Выполняет инициализацию приложения при запуске Django.

        Метод вызывается один раз при старте сервера.
        В данном случае:
        1. Создаёт директорию MEDIA_ROOT, если она не существует
        2. Логирует результат операции в консоль

        Args:
            self: Экземпляр конфигурации приложения.

        Returns:
            None

        Note:
            - Проверка `RUN_MAIN` и `DJANGO_AUTORELOAD` предотвращает двойное
              выполнение при использовании авто-перезагрузки в разработке.
        """
        if os.environ.get('RUN_MAIN') or not os.environ.get('DJANGO_AUTORELOAD'):
            media_root = settings.MEDIA_ROOT
            if not os.path.exists(media_root):
                os.makedirs(media_root, exist_ok=True)
                print(f"Создана папка MEDIA_ROOT: {media_root}")
