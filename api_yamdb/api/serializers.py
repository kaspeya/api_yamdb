from django.db.models import Avg
from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment
)

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        r'^[\w.@+-]',
        max_length=150,
        required=True,
        validators=(
            UniqueValidator(
                queryset=User.objects.all()),))
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=(
            UniqueValidator(
                queryset=User.objects.all()
            ),
        )
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                "'Me' can't be username"
            )
        return value

    class Meta:
        fields = ('username', 'email')
        model = User


class UserSerializer(SignUpSerializer):
    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role')
        model = User

    def validate_role(self, value):
        username = self.context['request'].user.username
        current_role = get_object_or_404(User, username=username).role
        if current_role == 'user' and current_role != value:
            return current_role
        return value


class MyTokenObtainSerializer(TokenObtainSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields["confirmation_code"] = serializers.CharField()
        del self.fields['password']

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'confirmation_code': attrs['confirmation_code'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass
        self.user = User.objects.filter(username=attrs['username']).get()

        if not self.user:
            raise exceptions.NotFound('User not found')
        return {}


class MyTokenObtainPairSerializer(MyTokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        user = get_object_or_404(User, username=attrs[self.username_field])
        token = attrs['confirmation_code']
        code_is_valid = default_token_generator.check_token(user, token)
        if code_is_valid:
            data = super().validate(attrs)
            refresh = self.get_token(self.user)
            data['access'] = str(refresh.access_token)
            user.save()
            return data
        raise exceptions.ValidationError('Invalid code')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializerRead(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'category',
            'genre')
        model = Title

    def get_rating(self, obj):
        score = obj.reviews.all().aggregate(Avg('score')).get(
            'score__avg')
        if score:
            return int(score)
        return None


class TitleSerializerWrite(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug')
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True)

    class Meta:
        fields = ('name', 'year', 'description', 'category', 'genre')
        model = Title

    def to_representation(self, instance):
        serializer = TitleSerializerRead(instance)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Review.objects.all(),
        default=None
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('id', 'author'),
                message="Review must be unique for author"
            )
        ]

    def validate(self, data):
        if self.context['request'].method not in ('POST',):
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError('Review already exists')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
