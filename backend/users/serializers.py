import re

from django.core.exceptions import ValidationError

from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializers import RecipeSerializer

from .models import Subscribers, CustomUser as User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователейю"""

    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Такой пользователь уже существует',
            )
        ],
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Такая почта уже существует',
            )
        ],
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'is_subscribed': {'read_only': True}
        }

    def validate(self, attrs):
        username = attrs.get('username')
        reg = re.compile(r'^[\w.@+-]+')

        if not reg.match(username):
            raise ValidationError('Доступные символы: A-Z, a-z, 0-9, -, _.')

        if username.lower() == 'me':
            raise ValidationError('Использовано служебное имя')

        return super().validate(attrs)

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, data):
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            return False

        return Subscribers.objects.filter(
            author=data, user=request.user
        ).exists()


class UserSetPasswordSerializer(serializers.ModelSerializer):
    """Сериализация смены пароля."""

    current_password = serializers.CharField(
        source='user.password',
        style={'input_type': 'password'},
        max_length=150,
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        max_length=150,
    )

    class Meta:
        model = User
        fields = ('current_password', 'new_password')


class UserSubscribeSerializer(UserSerializer):
    """Сериализация подписок."""

    email = serializers.EmailField(
        read_only=True,
    )
    id = serializers.CharField(
        read_only=True,
    )
    username = serializers.CharField(
        read_only=True,
    )
    first_name = serializers.CharField(
        read_only=True,
    )
    last_name = serializers.CharField(
        read_only=True,
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'recipes',
        )

    def get_recipes_count(self, data):
        return Recipe.objects.filter(author=data).count()

    def get_recipes(self, data):
        queryset = Recipe.objects.filter(author=data)
        serializer = RecipeSerializer(queryset, many=True)
        return serializer.data
