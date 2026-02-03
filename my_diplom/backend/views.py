from django.contrib.auth import authenticate
from django.shortcuts import render, reverse
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from backend.models import Comment, Like, Publication
from backend.permissions import IsOwnerOrReadOnly
from backend.sirializers import (CommentSerializer,
                                 PublicationCreateSerializer,
                                 PublicationSerializer,
                                 UserRegistrationSerializer)


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
    permission_classes = [AllowAny]

    def post(self, request):
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
    permission_classes = []

    queryset = Publication.objects.all().prefetch_related("photos")

    def create(self, request, *args, **kwargs):
        create_serializer = PublicationCreateSerializer(
            data=request.data, context={"request": request}
        )
        create_serializer.is_valid(raise_exception=True)
        publication = create_serializer.save()

        result_serializer = PublicationSerializer(publication)

        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "create":
            return PublicationCreateSerializer
        return PublicationSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        elif self.action == "like":
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        publication = self.get_object()
        user = request.user

        if Like.objects.filter(id_user=user, id_publication=publication).exists():
            return Response({"error": "Уже лайкнуто"}, status=400)

        Like.objects.create(id_user=user, id_publication=publication)
        return Response({"status": "лайк поставлен"})


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Только комментарии к конкретному посту
        publication_id = self.kwargs["publication_pk"]
        return Comment.objects.filter(id_publication_id=publication_id)

    def perform_create(self, serializer):
        publication = get_object_or_404(Publication, pk=self.kwargs["publication_pk"])
        serializer.save(id_user=self.request.user, id_publication=publication)

def home_view(request):
    template_name = "greeting.html"
    pages = {
        "Главная страница": reverse("home"),
    }

    # context и параметры render менять не нужно
    # подбробнее о них мы поговорим на следующих лекциях
    context = {"pages": pages}
    return render(request, template_name, context)
