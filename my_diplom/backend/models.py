import os

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

User = get_user_model()
# Create your models here.

class Publication(models.Model):
    """
     Модель, представляющая публикацию (пост) в социальной сети.

    Каждая публикация связана с пользователем, содержит текст, уровень доступа
    и временную метку создания. Публикации могут быть видны разным группам людей
    в зависимости от настроек доступа.

    Attributes:
        id_user (ForeignKey): Пользователь, создавший публикацию.
            Связан с моделью User через отношение "один ко многим".
        text (TextField): Текст публикации. Может быть пустым или содержать
            многострочный текст. Максимальная длина определяется базой данных.
        accessibility (CharField): Уровень доступа к публикации.
            Определяет, кто может видеть эту публикацию.
            Выбирается из вариантов AccessLevel.choices.
        time_created (DateTimeField): Дата и время создания публикации.
            Устанавливается автоматически при создании и не изменяется.
    """
    class AccessLevel(models.TextChoices):
        """
        Уровни доступа к публикации.

        Options:
            PUBLIC: Публикация видна всем пользователям.
            FRIENDS: Публикация видна только друзьям пользователя.
            PRIVATE: Публикация видна только создателю.
        """
        PUBLIC = "public", "Public"
        FRIENDS = "friends", "Friends Only"
        PRIVATE = "private", "Private"

    id_user = models.ForeignKey(
        User, related_name="publications", on_delete=models.CASCADE
    )
    text = models.TextField(blank=True, null=True)
    accessibility = models.CharField(
        max_length=10, choices=AccessLevel.choices, default=AccessLevel.PUBLIC
    )
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Метаданные модели Publication.

        Attributes:
            ordering: Порядок сортировки по умолчанию.
                Публикации сортируются от новых к старым.
        """
        ordering = ["-time_created"]


class Comment(models.Model):
    """
    Модель, представляющая комментарий к публикации в социальной сети.

    Каждый комментарий связан с конкретной публикацией и пользователем,
    который его оставил. Комментарии могут быть пустыми (например, для
    реакции в виде эмодзи) или содержать текст.

    Attributes:
        id_user (ForeignKey): Пользователь, создавший комментарий.
            Связан с моделью User через отношение "один ко многим".
            При удалении пользователя удаляются все его комментарии.
        id_publication (ForeignKey): Публикация, к которой оставлен комментарий.
            Связан с моделью Publication через отношение "один ко многим".
            При удалении публикации удаляются все её комментарии (CASCADE).
        text (TextField): Текст комментария. Может быть пустым или содержать
            многострочный текст. Максимальная длина определяется базой данных.
        time_created (DateTimeField): Дата и время создания комментария.
            Устанавливается автоматически при создании и не изменяется.
    """
    id_user = models.ForeignKey(
        User, related_name="comments", on_delete=models.CASCADE
    )
    id_publication = models.ForeignKey(
        Publication, related_name="comments", on_delete=models.CASCADE
    )
    text = models.TextField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Метаданные модели Comment.

        Attributes:
            ordering: Порядок сортировки по умолчанию.
                Комментарии сортируются от старых к новым (хронологический порядок).
                Это обеспечивает естественное отображение в интерфейсе.
        """
        ordering = ["time_created"]


class Like(models.Model):
    """
    Модель, представляющая лайки к публикации в социальной сети.

    Каждый лайк связан с конкретной публикацией и пользователем,
    который его поставил. Система гарантирует, что пользователь может
    поставить только один лайк на одну публикацию.

    Attributes:
        id_user (ForeignKey): Пользователь, поставивший лайк.
            Связан с моделью User через отношение "многие к одному".
            При удалении пользователя удаляются все его лайки.
        id_publication (ForeignKey): Публикация, к которой поставили лайк.
            Связан с моделью Publication через отношение "один к одному".
            При удалении публикации удаляются все её лайки (CASCADE).
        time_created (DateTimeField): Дата и время создания лайка.
            Устанавливается автоматически при создании и не изменяется.
        """
    id_user = models.ForeignKey(
        User, related_name="likes", on_delete=models.CASCADE
    )
    id_publication = models.ForeignKey(
        Publication, related_name="likes", on_delete=models.CASCADE
    )
    time_created = models.DateTimeField(auto_now_add=True)

    # one user - one like
    class Meta:
        """
        Метаданные модели Like.

        Attributes:
            unique_together: Уникальность поставленного лайка.
                Один лайк - олин пользователь
        """
        unique_together = ("id_user", "id_publication")


class Photo(models.Model):
    """
    Модель, представляющая фотографии, который будут загружать пользователи к публикации.

    Фото может быть прикреплено к публикации (посту) или существовать отдельно.
    Каждое фото связано с пользователем, который его загрузил, и может иметь
    текстовое описание (подпись). Изображения хранятся в подкаталоге 'photos/'.

    Attributes:
        id_user (ForeignKey): Пользователь, прикрепивший фото.
            Связан с моделью User через отношение "многие к одному"
            (один пользователь может загрузить много фото).
            При удалении пользователя удаляются все его фото.
        id_publication (ForeignKey): Публикация, к которой прикреплено фото.
            Связан с моделью Publication через отношение "многие к одному"
            (одна публикация может иметь много фото).
            При удалении публикации удаляются все её фото (CASCADE).
        image (ImageField): Поле для загрузки изображения.
            Загружаемые файлы сохраняются в директории 'photos/' (относительно MEDIA_ROOT).
            Поддерживает все основные форматы изображений (JPEG, PNG, GIF).
        caption (CharField): Текстовая подпись к фото.
            Максимальная длина - 255 символов. Может быть пустой.
            Используется для описания, тегов или контекста фото.
        time_created (DateTimeField): Дата и время создания лайка.
            Устанавливается автоматически при создании и не изменяется.
    """
    id_user = models.ForeignKey(
        User, related_name="photos", on_delete=models.CASCADE
    )
    id_publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name="photos",
        blank=True,
        null=True,
    )
    image = models.ImageField(upload_to="photos/")
    caption = models.CharField(max_length=255, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Метаданные модели Photo.

        Attributes:
            ordering: Порядок сортировки по умолчанию.
                Фото сортируются от новых к старым.
        """
        ordering = ["-time_created"]


@receiver(post_delete, sender=Photo)
def delete_photo_file(sender, instance, **kwargs):
    """
    Удаляет файл изображения при удалении объекта Photo.

    Сигнал post_delete гарантирует, что файл будет удалён даже при
    массовом удалении (queryset.delete()) или каскадном удалении.

    Args:
        sender (Model): Класс модели, который отправил сигнал (Photo).
        instance (Photo): Удаляемый экземпляр модели Photo.
        **kwargs: Дополнительные аргументы сигнала.

    Returns:
        None: Функция ничего не возвращает.

    Raises:
        Ошибки пока не обрабатываются
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
