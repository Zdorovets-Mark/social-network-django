import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from backend.models import Comment, Photo, Publication

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Подготавливает и проверяет данные для регистрации пользователя. Наследуется от ModelSerializer.
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        """
        Метаинформация о сериализаторе

        Attributes:
            model: Указывает из какой модели будем брать данные
            fields: Поля, которые будут возвращены
        """
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        """
        Метод, который создает пользователя

        Args:
            validated_data: Проверенные данные после валидации

        Returns:
            Созданный экземпляр модели User
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class CommentSerializer(serializers.ModelSerializer):
    """
        Подготавливает и проверяет данные для создания комментария. Наследуется от ModelSerializer.
    """
    author = serializers.ReadOnlyField(source="id_user.username")
    id_user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """
        Метаинформация о комментарии

        Attributes:
            model: Модель из которой будут браться данные
            fields: Поля которые будут проверены и возвращены
        """
        model = Comment
        fields = ("id", "id_user", "author", "text", "time_created")


class PhotoSerializer(serializers.ModelSerializer):
    """
    Подготавливает и проверяет данные для добавления фотографий. Наследуется от ModelSerializer.
    """
    class Meta:
        """
        Метаинформация о фотографии

        Attributes:
            model: Модель из которой будут доставаться данные
            fields: Поля которые будут провалидированы и возвращены
        """
        model = Photo
        fields = ("id", "image", "caption", "time_created")


class PublicationSerializer(serializers.ModelSerializer):
    """
    Подготавливает и проверяет данные для публикации. Наследуется от ModelSerializer.
    """
    creator = serializers.ReadOnlyField(source="id_user.username")
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    def get_likes_count(self, obj):
        """
        Возвращает количество лайков у объекта(публикации)

        Args:
            obj: передаваемый объект

        Returns:
            Количество лайков под публикацией

        Raises:
            Пока не обрабатываются
        """
        return obj.likes.count()

    class Meta:
        """
        Метаинформация о публикации

        Attributes:
            model: Модель из которой будут доставаться данные
            fields: Поля которые будут провалидированы и возвращены
        """
        model = Publication
        fields = (
            "id",
            "text",
            "photos",
            "creator",
            "time_created",
            "comments",
            "likes_count",
        )


class PublicationCreateSerializer(serializers.ModelSerializer):
    """
    Подготавливает и проверяет данные для создания публикации, для добавления фотографий. Наследуется от ModelSerializer.
    """
    photos = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
        min_length=1,
        max_length=10,
    )

    class Meta:
        """
        Метаинформация о публикации

        Attributes:
            model: Модель из которой будут доставаться данные
            fields: Поля которые будут проверены и возвращены
        """
        model = Publication
        fields = ("text", "photos")

    def validate_photos(self, value):
        """
        Выполняет проверку фотографий

        Args:
            value: фотография

        Returns:
            Возвращает фотографию

        Raises:
            Проверка фотографии по размеру и формату
        """
        for image in value:
            if image.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    f"Файл {image.name} слишком большой. Максимальный размер: 5MB"
                )

            valid_extensions = [".jpg", ".jpeg", ".png", ".gif"]
            extension = os.path.splitext(image.name)[1].lower()
            if extension not in valid_extensions:
                raise serializers.ValidationError(
                    f"Неподдерживаемый формат файла {image.name}. "
                    f"Поддерживаемые форматы: {', '.join(valid_extensions)}"
                )
        return value

    def create(self, validated_data):
        """
        Создание публикации

        Args:
           validated_data: Обработанные данные

        Returns:
             Возвращает публикацию
        """
        photos = validated_data.pop("photos", [])

        # Создаю публикацию
        publication = Publication.objects.create(
            id_user=self.context["request"].user, text=validated_data.get("text")
        )

        # Создаю записи для каждого фото
        for photo_file in photos:
            Photo.objects.create(
                id_user=self.context["request"].user,
                id_publication=publication,
                image=photo_file,
                caption="",
            )

        return publication