import uuid

from django.conf import settings
from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import ROLES, User


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=ROLES, default='user')

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role')
        model = User

    def create(self, validated_data):
        email = validated_data['email']
        confirmation_code = str(uuid.uuid3(uuid.NAMESPACE_X500, email))
        return User.objects.create(
            **validated_data,
            confirmation_code=confirmation_code
        )

    def validate_username(self, name):
        if name == settings.USER_ME:
            raise serializers.ValidationError(
                'Имя "me" не может быть использовано!'
            )
        elif name is None or name == "":
            raise serializers.ValidationError(
                'Поле "name" обязательно для заполнения!'
            )
        return name

    def validate_email(self, email):
        if email is None or email == "":
            raise serializers.ValidationError(
                'Поле "email" обязательно для заполнения!'
            )
        return email


class MeSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)

    def validate_username(self, name):
        if name == settings.USER_ME:
            raise serializers.ValidationError(
                'Имя "me" не может быть использовано!'
            )
        return name

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if (
            User.objects.filter(username=username).exists()
            and User.objects.get(username=username).email != email
        ):
            raise serializers.ValidationError('Это имя уже существует!')
        if (
            User.objects.filter(email=email).exists()
            and User.objects.get(email=email).username != username
        ):
            raise serializers.ValidationError('Этот email уже существует!')
        return data


class AuthSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=255)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        if username is None:
            raise serializers.ValidationError(
                'Требуется ввести имя'
            )
        if confirmation_code is None:
            raise serializers.ValidationError(
                'Требуется ввести код подтверждения'
            )
        return data


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
