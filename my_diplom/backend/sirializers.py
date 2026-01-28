from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from backend.models import Publication, Comment, Photo

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ("id_user", "text", "time_created")

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'image', 'caption', 'time_created')

class PublicationSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='id_user.username')
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    def get_likes_count(self, obj):
        return obj.likes.count()

    class Meta:
        model = Publication
        fields = ('id', 'text', 'photos', 'creator', 'time_created', 'comments', 'likes_count')

class PublicationCreateSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Publication
        fields = ('text', 'photos')

    def create(self, validated_data):
        photos = validated_data.pop('photos', [])

        # Создаю публикацию
        publication = Publication.objects.create(
            id_user=self.context['request'].user,
            text=validated_data.get('text')
        )

        # Создаю записи для каждого фото
        for photo_file in photos:
            Photo.objects.create(
                id_user=self.context['request'].user,
                id_publication=publication,
                image=photo_file,
                caption=""
            )

        return publication