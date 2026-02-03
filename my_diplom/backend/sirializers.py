import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from backend.models import Comment, Photo, Publication

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="id_user.username")

    class Meta:
        model = Comment
        fields = ("id_user", "author", "text", "time_created")


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ("id", "image", "caption", "time_created")


class PublicationSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source="id_user.username")
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    def get_likes_count(self, obj):
        return obj.likes.count()

    class Meta:
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
    photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True,
        min_length=1,
        max_length=10,
    )

    class Meta:
        model = Publication
        fields = ("text", "photos")

    def validate_photos(self, value):
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
