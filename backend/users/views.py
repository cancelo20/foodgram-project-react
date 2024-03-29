from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from django.shortcuts import get_object_or_404

from .permissions import IsAdminOrUser, UserPermissions

from .models import Subscribers, CustomUser as User
from .serializers import (
    GetSubscritionsSerializer,
    UserSetPasswordSerializer,
    UserSubscribeSerializer,
    UserSerializer,
)


class UserViewSet(ModelViewSet):
    """Класс управления информацией о пользователях."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    http_method_names = ('post', 'get', 'delete')

    def get_permissions(self):
        if self.action in ['subscribe', 'unsubscribe', 'get_subscriptions']:
            permission_classes = (IsAuthenticated,)
        elif self.action in ['get_self_user_info', 'set_password']:
            permission_classes = (IsAdminOrUser,)
        else:
            permission_classes = (UserPermissions,)

        return [permission() for permission in permission_classes]

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
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
        serializer_class=UserSetPasswordSerializer
    )
    def set_password(self, request):
        """Функция смены пароля."""

        serializer = UserSetPasswordSerializer(
            data=request.data,
            context={
                'request': request,
                'request_data': request.data
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': request.data.get('new_password')},
            status=status.HTTP_205_RESET_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions'
    )
    def get_subscriptions(self, request):
        """Список подписок пользователя."""

        users = User.objects.filter(followed__user=request.user)
        page = self.paginate_queryset(users)

        serializer = GetSubscritionsSerializer(
            page, many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        serializer_class=UserSubscribeSerializer,
    )
    def subscribe(self, request, id):
        """Подписаться на пользователя по id."""

        followed = get_object_or_404(User, id=id)
        context = {'request': request}
        serializer = UserSubscribeSerializer(
            context=context,
            data={'id': id}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            GetSubscritionsSerializer(
                context=context
            ).to_representation(instance=followed),
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
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                GetSubscritionsSerializer(
                ).to_representation(instance=followed),
                status=status.HTTP_204_NO_CONTENT
            )
