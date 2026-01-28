from django.contrib.auth import authenticate
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from backend.models import Publication, Like, Comment
from backend.permissions import IsOwnerOrReadOnly
from backend.sirializers import UserRegistrationSerializer, PublicationCreateSerializer, PublicationSerializer, \
    CommentSerializer

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Создаем токен для пользователя
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'message': 'Пользователь успешно зарегистрирован'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            token = Token.objects.get_or_create(user=user)[0]
            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": username,
                "message": f"Welcome {username}"
            }, status=HTTP_200_OK)
        else:
            return Response({"error": "invalid login or password"}, status=HTTP_400_BAD_REQUEST)

class PublicationViewSet(ModelViewSet):
    permission_classes = []

    queryset = Publication.objects.all().prefetch_related('photos')

    def create(self, request, *args, **kwargs):
        # Вызываю родительский create
        response = super().create(request, *args, **kwargs)

        response.data = {
            "message": "Publication is create",
            "publication": response.data,
            'user_id': request.user.id,
            'username': request.user.username
        }

        return response

    def get_serializer_class(self):
        if self.action == 'create':
            return PublicationCreateSerializer
        return PublicationSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        elif self.action == 'like':
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        publication = self.get_object()
        user = request.user

        if Like.objects.filter(id_user=user, id_publication=publication).exists():
            return Response({'error': 'Уже лайкнуто'}, status=400)

        Like.objects.create(id_user=user, id_publication=publication)
        return Response({'status': 'лайк поставлен'})

class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Только комментарии к конкретному посту
        publication_id = self.kwargs['publication_pk']
        return Comment.objects.filter(id_publication_id=publication_id)

    def perform_create(self, serializer):
        publication = get_object_or_404(Publication, pk=self.kwargs['publication_pk'])
        serializer.save(id_user=self.request.user, id_publication=publication)

