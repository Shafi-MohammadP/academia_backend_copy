from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLES = (
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=False)
    role = models.CharField(max_length=10, choices=ROLES, default='student')
    is_blocked = models.BooleanField(default=False, blank=True, null=True)
    is_google = models.BooleanField(default=False, blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True, default=None)
    USERNAME_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class StudentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="student_user", null=True)
    bio = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    profile_photo = models.FileField(
        upload_to='student_profiles/', blank=True, null=True)
    mobile = PhoneNumberField(blank=True, null=True, default=None)

    def __str__(self):
        return self.user.email


class TutorProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="tutor_user")
    bio = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=100, default="")
    profile_photo = models.FileField(
        upload_to='tutor_profiles/', blank=True, null=True)
    mobile = PhoneNumberField(blank=True, null=True, default=None)
    is_certificate = models.BooleanField(default=False)
    wallet = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return self.user.email


class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_photo = models.FileField(
        upload_to='admin_profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.email
