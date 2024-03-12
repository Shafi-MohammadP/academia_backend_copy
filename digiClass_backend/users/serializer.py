from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# from rest_framework.validators import UniqueValidator
# from django.contrib.auth.hashers import make_password
from rest_framework.serializers import ModelSerializer

from rest_framework import serializers
from .models import CustomUser
from rest_framework.response import Response


class SignUpSerializer(ModelSerializer):
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = CustomUser
        fields = "__all__"

    def create(self, validated_data):
        email = validated_data["email"]

        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "Email already exists"})

        password = validated_data["password"]
        password2 = validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError(
                {"password": "Passwords do not match"})
        try:

            role = validated_data["role"]
        except KeyError:
            print("Error,'role' Field is mising")
            data = {
                "Text": "Role not added",
                "status": 400
            }
            return Response(data=data)

        user = CustomUser.objects.create(
            username=validated_data["username"],
            email=email,
            role=role  # Assuming 'role' is a field in your CustomUser model
        )

        user.set_password(password)
        user.is_active = False
        user.save()
        return user


class userGoogleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class myTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['is_admin'] = user.is_superuser
        token['role'] = user.role
        token['is_active'] = user.is_active
        token['is_google'] = user.is_google
        return token


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", 'email',
                  "role", "is_active"]


class studentProfileSerializer(serializers.ModelSerializer):
    student_details = CustomUserSerializer(source='user', read_only=True)

    class Meta:
        model = StudentProfile
        fields = '__all__'


class tutorProfileSerializer(serializers.ModelSerializer):
    tutor_details = CustomUserSerializer(source='user', read_only=True)

    class Meta:
        model = TutorProfile
        fields = "__all__"
