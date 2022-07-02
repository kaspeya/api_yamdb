from rest_framework import viewsets, status, filters, mixins
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import exceptions
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from reviews.models import (
    Category,
    Genre,
    Title,
    Review
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializerRead,
    TitleSerializerWrite,
    ReviewSerializer,
    CommentSerializer,
    UserSerializer,
    MyTokenObtainPairSerializer,
    SignUpSerializer
)
from .filters import TitleFilter
from .permissions import (
    IsAdmin,
    IsOwner,
    IsAdminOrReadOnly,
    ReadAnyoneChangeIfIsOwnerAdminModerator)


User = get_user_model()


def send_custom_email(user):
    user_token = default_token_generator.make_token(user)
    return send_mail(
        subject='Добро пожаловать на сервис YaMDB',
        message=f'Используйте код {user_token} для авторизации',
        from_email='nikolay.solop@yandex.ru',
        recipient_list=[user.email],
        fail_silently=False
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    if request.method == 'POST':
        username = request.data.get('username')
        user = User.objects.filter(username=username)
        if user.exists():
            send_custom_email(user.get())
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

        serializer = SignUpSerializer(data=request.data, many=False)
        if serializer.is_valid():
            user = serializer.save()
            send_custom_email(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get_object(self):
        pk = self.kwargs.get('username')
        method = self.request.method
        if pk == 'me' and method not in ('GET', 'PATCH'):
            raise exceptions.MethodNotAllowed(method)
        if pk == "me" and method in ('GET', 'PATCH'):
            return self.request.user
        return super(UserViewSet, self).get_object()

    def get_permissions(self):
        if self.kwargs.get('username') == 'me':
            self.permission_classes = [IsOwner]
        else:
            self.permission_classes = [IsAdmin]
        return super(UserViewSet, self).get_permissions()


class CategoryViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializerRead
        return TitleSerializerWrite


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReadAnyoneChangeIfIsOwnerAdminModerator,)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ReadAnyoneChangeIfIsOwnerAdminModerator,)

    def get_queryset(self, *args, **kwargs):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
