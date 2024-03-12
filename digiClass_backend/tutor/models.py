from django.db import models
from users.models import CustomUser, TutorProfile
from phonenumber_field.modelfields import PhoneNumberField
from notifications.models import AdminNotifications
# Create your models here.


class Certificate(models.Model):
    tutor = models.ForeignKey(
        TutorProfile, on_delete=models.CASCADE, related_name="tutor_certificate")   
    certificate = models.FileField(
        upload_to='teacher_certificates/', blank=True, null=True)
    is_approved = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        if self.tutor:
            return self.tutor.user.username
