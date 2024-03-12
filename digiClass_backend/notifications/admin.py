from django.contrib import admin
from .models import AdminNotifications, Notifications
# Register your models here.
admin.site.register(AdminNotifications)
admin.site.register(Notifications)
