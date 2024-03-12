from users.models import CustomUser
from notifications.models import Notifications
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
import json
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


from django.core.mail import send_mail
from django.db.models import Q
from .models import Certificate


channel_layer = get_channel_layer()


@receiver(post_save, sender=Certificate)
def send_certificate_uploaded_notification(sender, instance, created, *args, **kwargs):

    
    if created:
        notification_text = f"New Teacher {instance.tutor.user.username} uploaded Certificate"
        admin_user = CustomUser.objects.filter(is_superuser=True).first()
        Notifications.objects.create(user=admin_user, text=notification_text)
        print(notification_text, "<<<<<<<<<<<<<<<<<<<<<<<<<<,------------------------")
        async_to_sync(channel_layer.group_send)(
            "admin_group", {
                "type": "create_notification",
                "message": notification_text
            }
        )


# @receiver(post_save, sender =Certificate)
# def send_certificat