from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from .models import AdminNotifications, Notifications
from .serializer import AdminNotificationSerializer, NotificationsSerializer
from rest_framework import status
from rest_framework.response import Response
# Create your views here.


# class CertificateDetails(ListAPIView):
#     queryset = AdminNotifications.objects.filter(is_opened=False)
#     serializer_class = AdminNotificationSerializer


class NotificationList(ListAPIView):
    queryset = Notifications.objects.filter(is_read=False)
    serializer_class = NotificationsSerializer


class NotificationReadView(RetrieveUpdateAPIView):
    queryset = Notifications.objects.filter(is_read=False)
    serializer_class = NotificationsSerializer

    def update(self, request, *args, **kwargs):
        notification_id = kwargs.get('pk')
        try:
            notification = Notifications.objects.get(pk=notification_id)
            notification.is_read = not notification.is_read
            notification.save()
            data = {
                "message": "Notification Read",
                "status": status.HTTP_200_OK
            }
            return Response(data=data)
        except Notifications.DoesNotExist:
            data = {
                "message": "Notification not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)
