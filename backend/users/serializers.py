import re

from django.shortcuts import get_object_or_404

from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializers import GetRecipeSerializer

from .models import Subscribers, CustomUser as User
from .mixins import IsSubscribedMixin


class UserSerializer(
        serializers.ModelSerializer,
        IsSubscribedMixin
):
    """Сериализатор модели пользователейю"""

    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Такой пользователь уже существует',
            )
        ],
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Такая почта уже существует',
            )
        ],
    )

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


class UserSetPasswordSerializer(serializers.ModelSerializer):
    """Сериализация смены пароля."""

    new_password = serializers.CharField(
        max_length=150
    )
    current_password = serializers.CharField(
        source='user.password',
        max_length=150,
    )

    class Meta:
        model = User
        fields = ('new_password', 'current_password')

    def validate(self, data):
        request = self.context.get('request_data')
        current_password = request.get('current_password')
        new_password = request.get('new_password')
        user = self.context.get('request').user

        if current_password is None or new_password is None:
            raise ValidationError('Данные не предоставлены!')

        if not user.check_password(current_password):
            raise ValidationError('Неверный пароль!')

        return super().validate(data)

    def create(self, validated_data):
        user = self.context.get('request').user
        user.set_password(
            validated_data.get('new_password')
        )
        user.save()

        return validated_data.get('new_password')


class GetSubscritionsSerializer(
    serializers.ModelSerializer,
    IsSubscribedMixin
):

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
        extra_kwargs = {
            'id': {'read_only': True},
            'is_subscribed': {'read_only': True},
            'recipes_count': {'read_only': True},
            'recipes': {'read_only': True},
        }

    def get_recipes_count(self, data):
        return Recipe.objects.filter(author=data).count()

    def get_recipes(self, data):
        queryset = Recipe.objects.filter(author=data)
        serializer = GetRecipeSerializer(queryset, many=True)
        return serializer.data


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Сериализация подписок."""

    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('id',)

    def validate(self, data):
        id = data.get('id')
        followed = get_object_or_404(User, id=id)
        follower = self.context.get('request').user

        if follower == followed:
            raise ValidationError('Нельзя подписаться на себя!')

        if Subscribers.objects.filter(author=followed, user=follower).exists():
            raise ValidationError('Вы уже подписаны!')

        return data

    def create(self, validated_data):
        id = validated_data.get('id')
        followed = get_object_or_404(User, id=id)
        follower = self.context.get('request').user

        subscribe = Subscribers.objects.create(user=follower, author=followed)
        subscribe.save()

        return subscribe
