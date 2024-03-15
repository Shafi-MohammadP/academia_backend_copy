from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone
from .models import *
from course.models import Course
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from notifications.models import Notifications
from users.models import CustomUser

additional_data = None
channel_layer = get_channel_layer()


@receiver(post_save, sender=Course)
def send_course_created_notification(sender, instance, created, *args, **kwargs):

    if created:
        notification_text = f'New Course {instance.course_name} Created by {instance.tutor_id.user.username}'
        admin_user = CustomUser.objects.filter(is_superuser=True).first()
        Notifications.objects.create(
            user=admin_user, text=notification_text, course=instance)
        print(notification_text, "------------------------------>>>>>>")
        async_to_sync(channel_layer.group_send)(
            "admin_group",
            {
                'type': 'create_notification',
                'message': notification_text
            }
        )


@receiver(post_save, sender=Course)
def send_course_approval_notification(sender, instance, *args, **kwargs):
    global additional_data
    if kwargs.get('update_fields') and 'is_available' in kwargs['update_fields']:
        user = CustomUser.objects.get(email=instance.tutor_id.user)
        print(user.id, "--------------------------------->>>>")
        if instance.is_available:
            notification_text_for_tutor = f"New Course {instance.course_name}  available now"
            notification_text_for_student = f"New Course {instance.course_name} available now"
        else:
            notification_text_for_tutor = f"Course {instance.course_name}  is now unavailable."
            notification_text_for_student = f"Course {instance.course_name} is now unavailable"

        print(user, "user----------------------------------->>>>")
        Notifications.objects.create(
            user=user, text=notification_text_for_tutor, course=instance)

        async_to_sync(channel_layer.group_send)(
            "tutor_group",
            {
                "type": "create_tutor_notification",
                "message": notification_text_for_tutor,

            }
        )
        async_to_sync(channel_layer.group_send)(
            "student_group",
            {
                "type": "create_student_notification",
                "message": notification_text_for_student,

            }
        )


@receiver(post_save, sender=VideosCourse)
def send_video_added_notification(sender, instance, created, *args, **kwargs):
    if created:
        notification_text = f'New Video Uploaded by {instance.course.tutor_id.user.username}'
        admin_user = CustomUser.objects.filter(is_superuser=True).first()
        Notifications.objects.create(user=admin_user, text=notification_text)
        print(
            f"Signal Notification from  {instance}--------------------------------------->>>>")
        async_to_sync(channel_layer.group_send)(
            "admin_group",
            {
                "type": "create_notification",
                "message": notification_text
            }
        )


@receiver(post_save, sender=VideoComment)
def send_comment_added_notification(sender, instance, created, *args, **kwargs):
    if created:
        notification_text = f"{instance.video.id}"
        print(notification_text, "text---------------->>")
        async_to_sync(channel_layer.group_send)(
            "user_group",
            {
                "type": "create_comment_update",
                "message": f"{instance.video.id}"
            }
        )
