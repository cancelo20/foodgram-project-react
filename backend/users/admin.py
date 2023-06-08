from django.contrib import admin

from .models import CustomUser, Subscribers


admin.site.register(CustomUser)
admin.site.register(Subscribers)
