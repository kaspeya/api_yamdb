import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitleFilter
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          ReadAnyoneChangeIfIsOwnerAdminModerator)
from .serializers import (AuthSerializer, CategorySerializer,
                          CommentSerializer, GenreSerializer, MeSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleSerializerRead, TitleSerializerWrite,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=('get', 'patch'),
        detail=False,
        url_path=settings.USER_ME,
        permission_classes=(IsAuthenticated,),
        serializer_class=MeSerializer
    )
    def set_profile(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def sign_up(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    confirmation_code = str(uuid.uuid3(uuid.NAMESPACE_X500, email))
    try:
        user, created = User.objects.get_or_create(
            **serializer.validated_data,
            confirmation_code=confirmation_code
        )
    except IntegrityError:
        return Response(
            'Такой логин или email уже существуют',
            status=status.HTTP_400_BAD_REQUEST
        )
    send_mail(
        subject=settings.DEFAULT_EMAIL_SUBJECT,
        message=user.confirmation_code,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=(email,))
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_token(request):
    serializer = AuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if confirmation_code != user.confirmation_code:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user)
    return Response({'token': str(refresh.access_token)},
                    status=status.HTTP_200_OK)


class ListCreateDestroyViewSet(
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'list':
            return (AllowAny(),)
        return (IsAdmin(),)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).all().order_by('id')
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializerRead
        return TitleSerializerWrite

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return (IsAdmin(),)


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
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        try:
            review = title.reviews.get(id=self.kwargs.get('review_id'))
        except TypeError:
            raise TypeError('У произведения нет такого отзыва')
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        if str(review.title.id) != self.kwargs.get('title_id'):
            raise ValueError('Некорректный title')
        serializer.save(author=self.request.user, review=review)
