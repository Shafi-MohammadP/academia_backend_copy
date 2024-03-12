from django.urls import path
from .import views
urlpatterns = [
    path('notification/', views.NotificationList.as_view()),
    path('notification_read/<int:pk>/', views.NotificationReadView.as_view())
]
