from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Certificate
from notifications.serializer import AdminNotificationSerializer
# from rest_framework.validators import UniqueValidator
# from django.contrib.auth.hashers import make_password
from rest_framework.serializers import ModelSerializer


from rest_framework import serializers
from .models import CustomUser
from rest_framework.response import Response
from users.serializer import CustomUserSerializer, tutorProfileSerializer


class ApplicationFormSerializer(ModelSerializer):
    tutor_details = CustomUserSerializer(source='tutor', read_only=True)

    class Meta:
        model = Certificate
        fields = "__all__"


class CertificateSerializer(serializers.ModelSerializer):
    notification_details = tutorProfileSerializer(
        source='tutor', read_only=True)

    class Meta:
        model = Certificate
        fields = '__all__'


class CertificateTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = "__all__"
