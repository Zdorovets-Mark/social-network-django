from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from backend.models import Comment, Like, Publication
from backend.permissions import IsOwnerOrReadOnly
from backend.serializers import (CommentSerializer,
                                 PublicationCreateSerializer,
                                 PublicationSerializer,
                                 UserRegistrationSerializer)


class UserRegistrationView(APIView):
    """
    Координирует событие "регистрация пользователя". Работает при запросе типа POST.
    Используется для реализации функционала APIView
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Переопределение метода POST.
        Вызывает сериализатор для проверки данных, потом возвращает ответ об успешном создании или ошибке

        Args:
            request: Сам запрос

        Returns:
            HTTP ответ об успехе или неуспехе

        Raises:
            Не обрабатываются
        """
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Создаем токен для пользователя
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "token": token.key,
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "message": "Пользователь успешно зарегистрирован",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    Координирует событие "Вход пользователя (аутентификация)". Работает при запросе типа POST.
    Используется для реализации функционала APIView
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Переопределение метода POST.
        Вызывает authenticate для проверки данных, потом возвращает ответ об успешном входе или ошибке входа

        Args:
            request: Сам запрос

        Returns:
            HTTP ответ об успехе или неуспехе входа

        Raises:
            Не обрабатываются
        """
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            token = Token.objects.get_or_create(user=user)[0]
            return Response(
                {
                    "token": token.key,
                    "user_id": user.id,
                    "username": username,
                    "message": f"Welcome {username}",
                },
                status=HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "invalid login or password"}, status=HTTP_400_BAD_REQUEST
            )


class PublicationViewSet(ModelViewSet):
    """
    Координирует работу с публикацией: создание, обновление, определение доступа, подсчет лайков.
    Обрабатывает все HTTP-методы.
    Используется для реализации функционала ModelViewSet
    """
    permission_classes = []

    queryset = Publication.objects.all().prefetch_related("photos")

    def create(self, request, *args, **kwargs):
        """
        Создание публикации

        Args:
            request: Сам запрос

        Returns:
            HTTP ответ об успехе или неуспехе создания

        Raises:
            Не обрабатываются
        """
        create_serializer = PublicationCreateSerializer(
            data=request.data, context={"request": request}
        )
        create_serializer.is_valid(raise_exception=True)
        publication = create_serializer.save()

        result_serializer = PublicationSerializer(publication)

        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        """
        Определение с каким сериализатором будем работать

        Returns:
            Объект сериализатора

        Raises:
            Не обрабатываются
        """
        if self.action == "create":
            return PublicationCreateSerializer
        return PublicationSerializer

    def get_permissions(self):
        """
        Определение прав доступа

        Returns:
            Предназначаемые права доступа для функционала определенной операции

        Raises:
            Не обрабатываются
        """
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        elif self.action == "like":
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """
        Операция "поставить like"

        Args:
            request: Сам запрос
            pk: идентификатор публикации

        Returns:
            Возвращает HTTP ответ о том, что лайк поставлен или что лайк убран

        Raises:
            Не обрабатываются
        """
        publication = self.get_object()
        user = request.user

        like = Like.objects.filter(id_user=user, id_publication=publication).first()
        if like:
            like.delete()
            return Response({"status": "лайк убран"}, status=status.HTTP_200_OK)
        else:
            Like.objects.create(id_user=user, id_publication=publication)
            return Response({"status": "лайк поставлен"}, status=status.HTTP_201_CREATED)


class CommentViewSet(ModelViewSet):
    """
    ViewSet для работы с комментариями к публикациям.

    Предоставляет стандартные CRUD операции для модели Comment.
    Обрабатывает все HTTP-методы (GET, POST, PUT, PATCH, DELETE).
    Доступ к комментариям осуществляется в контексте конкретной публикации,
    идентификатор которой передаётся в URL как параметр 'publication_pk'.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Возвращает queryset комментариев, относящихся к текущей публикации.

        Извлекает `publication_pk` из параметров URL (self.kwargs) и фильтрует
        все комментарии по полю `id_publication_id`. Используется для отображения
        списка комментариев конкретного поста.

        Returns:
            QuerySet: Комментарии, принадлежащие публикации с id = publication_pk.
        """
        publication_id = self.kwargs["publication_pk"]
        return Comment.objects.filter(id_publication_id=publication_id)

    def perform_create(self, serializer):
        """
        Сохраняет новый комментарий, связывая его с текущим пользователем и публикацией.

        При создании комментария автоматически заполняет поля:
        - `id_user` = текущий аутентифицированный пользователь (request.user)
        - `id_publication` = публикация, полученная по `publication_pk` из URL.

        Args:
            serializer: Сериализатор с валидированными данными для создания комментария.

        Raises:
            Http404: Если публикация с указанным `publication_pk` не найдена.
        """
        publication = get_object_or_404(Publication, pk=self.kwargs["publication_pk"])
        serializer.save(id_user=self.request.user, id_publication=publication)


def home_view(request):
    """
    Для создания html главной страницы

    Args:
        request: Выполняемый запрос

    Returns:
        Возвращает html страницу

    """
    context = {
        'title': 'Добро пожаловать!',
        'message': 'Для просмотра постов войдите или зарегистрируйтесь'
    }
    return render(request, 'greeting.html', context)

def login_view(request):
    """
    Для создания html страницы для входа

    Args:
        request: Выполняемый запрос

    Returns:
        Возвращает html страницу

    """
    return render(request, 'login.html')

def register_view(request):
    """
    Для создания html страницы регистрации

    Args:
        request: Выполняемый запрос

    Returns:
        Возвращает html страницу

    """
    return  render(request, 'register.html')