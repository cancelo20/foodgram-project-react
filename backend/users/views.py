from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ListSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from django.shortcuts import get_object_or_404

from recipes.permissions import IsAdminOrUser

from .models import Subscribers, CustomUser as User
from .serializers import (
    UserSetPasswordSerializer,
    UserSubscribeSerializer,
    UserSerializer,)


class UserViewSet(ModelViewSet):
    """Класс управления информацией о пользователях."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('post', 'get', 'delete')

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        permission_classes=(IsAdminOrUser, IsAuthenticated)
    )
    def get_self_user_info(self, request):
        """Информация пользователя о самом себе."""

        user = get_object_or_404(User, username=self.request.user)
        serializer = self.get_serializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        permission_classes=(IsAdminOrUser),
        serializer_class=UserSetPasswordSerializer
    )
    def set_password(self, request):
        """Функция смены пароля."""

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):

            if self.request.user.check_password(serializer.data.get('current_password')):
                self.request.user.set_password(serializer.data.get('new_password'))
                self.request.user.save()
                return Response(
                    {'detail': request.data.get('new_password')},
                    status=status.HTTP_205_RESET_CONTENT
                )

            return Response({'detail': 'Неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Учетные данные не были предоставлены.'},
            status=status.HTTP_401_UNAUTHORIZED)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions'
    )
    def get_subscriptions(self, request):
        """Список подписок пользователя."""

        user = request.user
        followed_list = User.objects.filter(followed__user=user)
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'limit'
        authors = paginator.paginate_queryset(
            followed_list,
            request=request
        )
        serializer = ListSerializer(
            child=UserSubscribeSerializer(),
            context=self.get_serializer_context()
        )
        return paginator.get_paginated_response(
            serializer.to_representation(authors)
        )

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Подписаться на пользователя по id."""
        followed = get_object_or_404(User, id=id)
        follower = request.user
        serializer = UserSubscribeSerializer(
                context=self.get_serializer_context()
            )

        if follower == followed:
            return Response({'detail': 'Нельзя подписаться на себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Subscribers.objects.filter(author=followed, user=follower).exists():
            return Response({'detail': 'Вы уже подписаны!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscribers.objects.create(
            user=follower,
            author=followed
        )

        return Response(
            serializer.to_representation(
                instance=followed
            ),
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        """Отписаться от пользователя по id."""

        followed = get_object_or_404(User, id=id)
        follower = request.user

        try:
            Subscribers.objects.filter(
                user=follower, author=followed).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
