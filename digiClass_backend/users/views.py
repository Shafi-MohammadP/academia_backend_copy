
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
import random
from django.shortcuts import render
from urllib.parse import quote
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
# import requests
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter
# from connectin.settings import STATIC_URL
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
# from .serializers import User_Sign_Up, myTokenObtainPairSerializer
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from rest_framework.generics import GenericAPIView, ListAPIView
from django.http import HttpResponseRedirect
from decouple import config
from .serializer import *
from .models import *
from rest_framework import status
from django.contrib.auth import authenticate
# Create your views here.
frontend_url = config('frontend_urls')


class Common_signup(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        email = request.data['email']
        if CustomUser.objects.filter(email=email).exists():

            data = {"Text": "Email already existed", "status": 400}
            return Response(data=data)

        if serializer.is_valid():
            user = serializer.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate Your Account'
            message = render_to_string('user/Account_activation.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': default_token_generator.make_token(user)
            })
            if email and '@' in email:
                send_mail(
                    mail_subject,
                    message,
                    'AcademiaLearning@gmail.com',
                    [email],
                    fail_silently=False,
                    html_message=message
                )
                return Response({
                    'Text': "We've sended a verification link to you email address",
                    'data': serializer.data,
                    'status': status.HTTP_200_OK
                })
            else:
                data = {
                    "Text": "Invalid Email Adress",
                    "data": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST
                }
                return Response(data=data)
        else:
            data = {
                "Text": "Error Occurred",
                "data": serializer.errors,
                "status": status.HTTP_400_BAD_REQUEST
            }
            return Response(data=data)


@api_view(['GET'])
def ActivateAccountView(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()

        user = CustomUser._default_manager.get(id=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        if user.role == 'student':
            student_data = {'user': user.id}
            student_serializer = studentProfileSerializer(data=student_data)
            if student_serializer.is_valid():
                student_serializer.save()

            else:
                user.delete()

                return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif user.role == 'tutor':
            tutor_data = {'user': user.id}
            tutor_serializer = tutorProfileSerializer(data=tutor_data)
            if tutor_serializer.is_valid():
                tutor_serializer.save()

            else:
                user.delete()

                return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        print(user, "user activated successfully")
        message = "Congrats, You have been successfully registered"
        redirect_url = f'{frontend_url}Login/?message={message}'

    else:
        print("Something Failed")
        message = 'Invalid activation link'
        redirect_url = f'{frontend_url}Login/' + '?message=' + message

    return HttpResponseRedirect(redirect_url)


class GooglLogin(APIView):
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get("username")
        password = request.data.get("password")

        existing_user = CustomUser.objects.filter(email=email).first()

        if existing_user:
            existing_user.is_google = True
            existing_user.save()
            token = create_jwt_token(existing_user)
            data = {
                'status': 200,
                'token': token,
                'Text': "Login Successful"
            }
            return Response(data=data, status=status.HTTP_201_CREATED)

        serializer = userGoogleSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):

            user, created = CustomUser.objects.get_or_create(
                email=email, defaults={'username': username})

            if created:

                user.is_active = True
                user.username = username
                user.is_google = True
                user.role = 'student'
                user.save()

            if user is not None:

                student_data = {'user': user.id}
                student_serializer = studentProfileSerializer(
                    data=student_data)
                if student_serializer.is_valid():
                    student_serializer.save()
                    token = create_jwt_token(user)

                    data = {
                        "Text": "Login Successful",
                        'status': 200,
                        'token': token,
                        'user': serializer.data,

                    }

                    return Response(data=data, status=status.HTTP_201_CREATED)
                else:
                    user.delete()
                    data = {
                        "Text": "Google Login Failed",
                        "status": status.HTTP_400_BAD_REQUEST,
                        "error": student_serializer.errors
                    }

                    return Response(data=data)
        else:

            data = {
                "Text": serializer.errors,
                "status": 400
            }
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user_instance = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User doesn't exist with this email"}, status=status.HTTP_400_BAD_REQUEST)
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        try:
            user_instance.otp = otp
            user_instance.save()
            email_subject = "Reset Password"
            email_message = f"OTP for Resetting the password {otp}"
            email = EmailMessage(email_subject, email_message,
                                 to=[user_instance.email])
            email.send(fail_silently=False)
            return Response({"message": "We've Sent an OTP to you email address"}, status=status.HTTP_200_OK)
        except Exception as e:

            return Response({"error": "Error when Sending mail"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp = request.data.get('otp')
        user_instance = get_object_or_404(CustomUser, email=email)
        entered_otp = ''.join(otp)
        if user_instance.otp == entered_otp:
            # Generate token
            refresh = RefreshToken.for_user(user_instance)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response({"message": "otp verified successfully", "token": token}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You entered wrong otp"}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)


class PasswordChange(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        # Extract password and confirmPassword from request data
        password = request.data.get('password')
        password2 = request.data.get('confirmPassword')
        user_id = request.user.id  # Extract user ID from the authenticated token
        print(request.user, "----------------------->>")
        # Retrieve user instance based on the user ID from the token
        try:
            user_instance = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the passwords match
        if password == password2:
            # Set the new password
            user_instance.set_password(password)
            user_instance.otp = None
            user_instance.save()
            user_serializer = CustomUserSerializer(user_instance)
            return Response({"message": "Password changed successfully", "user": user_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)


def create_jwt_token(user):
    refresh = RefreshToken.for_user(user)

    refresh['email'] = user.email
    refresh['id'] = user.id
    refresh['username'] = user.username
    refresh['role'] = user.role
    refresh['is_admin'] = user.is_superuser
    refresh['is_active'] = user.is_active
    refresh['is_google'] = user.is_google

    access = str(refresh.access_token)
    refresh = str(refresh)

    return {
        "access": access,
        "refresh": refresh,
    }


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = myTokenObtainPairSerializer


class studentProfileView(APIView):
    def get(self, request, user_id):
        student_profile = get_object_or_404(StudentProfile, user=user_id)
        serializer = studentProfileSerializer(student_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class tutorProfileView(APIView):
    def get(self, request, user_id):
        tutor_profile = get_object_or_404(TutorProfile, user=user_id)
        serializer = tutorProfileSerializer(tutor_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPagination(PageNumberPagination):
    page_size = 3


class studentListing(ListAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = studentProfileSerializer
    pagination_class = UserPagination


class tutorListing(ListAPIView):
    queryset = TutorProfile.objects.all()
    serializer_class = tutorProfileSerializer
    pagination_class = UserPagination


class NewTutoraLisiting(ListAPIView):
    queryset = TutorProfile.objects.all()
    serializer_class = tutorProfileSerializer
