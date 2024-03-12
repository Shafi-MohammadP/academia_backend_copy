from django.db import models
from users.models import CustomUser, TutorProfile
from course.models import Course
# Create your models here.


class AdminNotifications(models.Model):
    NOTIFICATION_TYPE = (
        ('register', 'register'),
        ('course', 'course'),
        ('video', 'video'),
    )
    name = models.CharField(max_length=100)
    is_opened = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE, default='register')
    created_time = models.DateTimeField(auto_now_add=True)
    key = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Notifications(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):

        return self.text
