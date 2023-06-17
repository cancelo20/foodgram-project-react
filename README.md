!(https://phonoteka.org/uploads/posts/2023-03/1679337078_phonoteka-org-p-rik-ogurchik-oboi-instagram-21.jpg)

# Проект «Продуктовый помощник» - Foodgram
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологический стек
[![Django-app workflow](https://github.com/cancelo20/foodgram-project-react/actions/workflows/foodgram-backend.yml/badge.svg?branch=master)](https://github.com/cancelo20/foodgram-project-react/actions/workflows/foodgram-backend.yml)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/-JWT-464646?style=flat&color=008080)](https://jwt.io/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=008080)](https://cloud.yandex.ru/)

## Базовые модели проекта
Более подробно с базовыми моделями можно ознакомиться в спецификации API.
http://myfoodgramproject.ddns.net/api/docs/

## Главная страница
Содержимое главной страницы — список первых шести рецептов, отсортированных по дате публикации (от новых к старым).  Остальные рецепты доступны на следующих страницах: внизу страницы есть пагинация.

## Страница рецепта
На странице — полное описание рецепта. Для авторизованных пользователей — возможность добавить рецепт в избранное и в список покупок, возможность подписаться на автора рецепта.

## Страница пользователя
На странице — имя пользователя, все рецепты, опубликованные пользователем и возможность подписаться на пользователя.

## Подписка на авторов
Подписка на публикации доступна только авторизованному пользователю. Страница подписок доступна только владельцу.
Сценарий поведения пользователя:
1. Пользователь переходит на страницу другого пользователя или на страницу рецепта и подписывается на публикации автора кликом по кнопке «Подписаться на автора».
2. Пользователь переходит на страницу «Мои подписки» и просматривает список рецептов, опубликованных теми авторами, на которых он подписался. Сортировка записей — по дате публикации (от новых к старым).
3. При необходимости пользователь может отказаться от подписки на автора: переходит на страницу автора или на страницу его рецепта и нажимает «Отписаться от автора».

## Список избранного
Работа со списком избранного доступна только авторизованному пользователю. Список избранного может просматривать только его владелец.
Сценарий поведения пользователя:
1. Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в избранное».
2. Пользователь переходит на страницу «Список избранного» и просматривает персональный список избранных рецептов.
3. При необходимости пользователь может удалить рецепт из избранного.

## Список покупок
Работа со списком покупок доступна авторизованным пользователям. Список покупок может просматривать только его владелец.
Сценарий поведения пользователя:
Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в покупки».
Пользователь переходит на страницу Список покупок, там доступны все добавленные в список рецепты. Пользователь нажимает кнопку Скачать список и получает файл с суммированным перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в «Списке покупок».
При необходимости пользователь может удалить рецепт из списка покупок.
Список покупок скачивается в формате *.txt* .

## Фильтрация по тегам
При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводится по нескольким тегам в комбинации «или»: если выбраны несколько тегов — в результате должны быть показаны рецепты, которые отмечены хотя бы одним из этих тегов.
При фильтрации на странице пользователя должны фильтроваться только рецепты выбранного пользователя. Такой же принцип должен соблюдаться при фильтрации списка избранного.

## Уровни доступа пользователей:
+ Гость (неавторизованный пользователь)
+ Авторизованный пользователь
+ Администратор

### Что могут делать неавторизованные пользователи
+ Создать аккаунт.
+ Просматривать рецепты на главной.
+ Просматривать отдельные страницы рецептов.
+ Просматривать страницы пользователей.
+ Фильтровать рецепты по тегам.

### Что могут делать авторизованные пользователи
+ Входить в систему под своим логином и паролем.
+ Выходить из системы (разлогиниваться).
+ Менять свой пароль.
+ Создавать/редактировать/удалять собственные рецепты
+ Просматривать рецепты на главной.
+ Просматривать страницы пользователей.
+ Просматривать отдельные страницы рецептов.
+ Фильтровать рецепты по тегам.
+ Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
+ Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
+ Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

### Что может делать администратор
+ Администратор обладает всеми правами авторизованного пользователя.
+ Плюс к этому он может:
+ изменять пароль любого пользователя,
+ создавать/блокировать/удалять аккаунты пользователей,
+ редактировать/удалять любые рецепты,
+ добавлять/удалять/редактировать ингредиенты.
+ добавлять/удалять/редактировать теги.

## Как развернуть проект на сревере:
Обновите индекс пакетов APT:
```
sudo apt update
sudo apt upgrade -y
```
Скопируйте подготовленные файлы docker-compose.yml и nginx.conf из вашего проекта на сервер:
```
scp docker-compose.yaml <username>@<host>/home/<username>/docker-compose.yaml
scp default.conf <username>@<host>/home/<username>/nginx.conf
```
Установите Docker и Docker-compose:
```
sudo apt install docker.io
```
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
На сервере создайте файл .env
```
touch .env
```
Откройте env-файл и заполните его
```
nano .env
```
```
SECRET_KEY=<SECRET_KEY>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
На сервере соберите docker-compose, соберите статические файлы статики, примените миграции:
```
sudo docker-compose up -d --build
sudo docker-compose exec backend python manage.py collectstatic --no-input
sudo docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate --noinput
```
Создайте суперпользователя(админа):
```
docker-compose exec backend python manage.py createsuperuser
```

Автор backend-проекта:
[cancelo20](https://github.com/cancelo20/)
