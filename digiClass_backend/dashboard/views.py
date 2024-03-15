
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from notifications.models import AdminNotifications
from notifications.serializer import AdminNotificationSerializer
from rest_framework import status
from rest_framework.response import Response
from users.models import CustomUser, TutorProfile
from rest_framework.generics import get_object_or_404
from course.models import CourseCategory, Course, VideosCourse
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from tutor.models import Certificate
from tutor.serializer import CertificateSerializer
from rest_framework import serializers
from course.serializer import *
from rest_framework.permissions import IsAuthenticated
from users.serializer import CustomUserSerializer
from .serializer import CountSerializer
# Create your views here.

"""
Creation of Category
"""


class CategoryCreation(CreateAPIView):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            user = self.request.user
            admin = CustomUser.objects.filter(id=user.pk, role='admin')
            if not admin.exists():
                data = {
                    "message": "You are not authorized to add categories.",
                    "status": status.HTTP_403_FORBIDDEN
                }
                return Response(data=data)

            category_name = request.data.get('name')

            if CourseCategory.objects.filter(name=category_name).exists():
                data = {
                    "message": f"{category_name} already exists",
                    "status": status.HTTP_406_NOT_ACCEPTABLE
                }
                return Response(data=data)

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                data = {
                    "message": "Category added successfully",
                    "status": status.HTTP_200_OK
                }
            else:
                data = {
                    "message": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST
                }
            return Response(data=data)
        except CustomUser.DoesNotExist:
            data = {
                "message": "User not found",
                "status": status.HTTP_401_UNAUTHORIZED
            }
            return Response(data=data)

    def perform_create(self, serializer):
        serializer.save()


class CourseCategoryOperation(APIView):
    def post(self, request, *args, **kwargs):
        admin = kwargs.get("id")

        try:
            admin_details = CustomUser.objects.get(id=admin, role='admin')
            pass
        except:
            return Response({"message": "You are not admin", "status": status.HTTP_401_UNAUTHORIZED})
        category_name = request.data.get('name')

        if CourseCategory.objects.filter(name=category_name).exists():
            return Response({"message": f"Category with name {category_name} is already exist", "status": status.HTTP_406_NOT_ACCEPTABLE})
        serializer = CourseCategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "Category Added Successfully",
                "status": status.HTTP_202_ACCEPTED
            }
            return Response(data=data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryUpdateAndRetrieve(RetrieveUpdateDestroyAPIView):
    queryset = CourseCategory.objects.filter(is_available=True)
    serializer_class = CourseCategorySerializer

    def perform_destroy(self, instance):
        # Soft delete by setting is_available to False
        instance.is_available = False
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Category Deleted successfully", "data": instance.id})


class CertificateApproval(RetrieveUpdateAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        certificate_id = self.kwargs.get('certificate_id')
        try:
            return Certificate.objects.get(id=certificate_id)
        except Certificate.DoesNotExist:
            return None

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance:
            data = {
                "message": "Certificate not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        instance.is_approved = not instance.is_approved
        instance.save()
        serializer = self.get_serializer(instance)
        data = {
            "message": "Successfully changed",
            "status": status.HTTP_200_OK
        }
        return Response(data=data)


class CourseList(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseApproval(RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = IndividualCourseSerializer

    def get_object(self):
        course_id = self.kwargs.get('pk')
        return Course.objects.get(id=course_id)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_available = not instance.is_available
        instance.save(update_fields=['is_available'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryAdding(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user

        # Check if the user has the 'admin' role
        if not user.role == 'admin':
            return Response({"message": "You are not an admin", "status": status.HTTP_401_UNAUTHORIZED})

        category_name = request.data.get('name')

        if CourseCategory.objects.filter(name=category_name).exists():
            return Response({"message": f"Category with name {category_name} already exists", "status": status.HTTP_406_NOT_ACCEPTABLE})

        serializer = CourseCategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "Category Added Successfully",
                "status": status.HTTP_202_ACCEPTED
            }
            return Response(data=data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryUpdatingAndDeletion(RetrieveUpdateDestroyAPIView):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.request.user
        if not user.role == 'admin':
            data = {
                "message": "You are not admin",
                "status": status.HTTP_401_UNAUTHORIZED
            }
            return Response(data=data)
        category_name = request.data.get("name")
        if CourseCategory.objects.filter(name=category_name).exists():
            data = {
                "message": "Category with this name already exist",
            }
            return Response(data=data, status=status.HTTP_409_CONFLICT)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = {
            "message": "Category Updated Successfully",
            "status": status.HTTP_200_OK
        }
        return Response(data=data)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user

        if not user.role == 'admin':
            data = {
                "message": "You are not admin",
                "status": status.HTTP_401_UNAUTHORIZED
            }
            return Response(data=data)
        instance = self.get_object()
        instance.is_available = not instance.is_available
        instance.save()
        data = {
            "message": "Category Availability Updated Successfully",
            "status": status.HTTP_200_OK
        }
        return Response(data=data)


class UserBlockAndUnblock(RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        user = self.request.user

        if not user.role == 'admin':
            data = {
                "message": "You are not admin",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save()
        data = {
            "message": "User Details updated Successfully",
            "status": status.HTTP_200_OK
        }
        return Response(data=data)


class VideoApproval(RetrieveUpdateDestroyAPIView):
    queryset = VideosCourse.objects.all()
    serializer_class = CourseVideoSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        video_id = kwargs.get('pk')
        try:
            video_instance = VideosCourse.objects.get(id=video_id)
            video_instance.is_approved = not video_instance.is_approved
            video_instance.save()
            data = {
                "message": f'Video Blocked Successfully {video_instance.video_title}',
                'status': status.HTTP_200_OK
            }
            return Response(data=data)
        except VideosCourse.DoesNotExist:
            data = {
                "message": "video not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)


class CategoryList(ListAPIView):
    queryset = CourseCategory.objects.filter(is_available=True)
    serializer_class = CourseCategorySerializer


class CertificateList(ListAPIView):
    queryset = AdminNotifications.objects.filter(
        is_opened=False, notification_type="register")
    serializer_class = AdminNotificationSerializer


class CertificateView(ListAPIView):
    queryset = Certificate.objects.filter()
    serializer_class = CertificateSerializer


class CourseVideoView(ListAPIView):
    queryset = VideosCourse.objects.all()
    serializer_class = VideoWithCourseDetails


class AllCount(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        student_count = StudentProfile.objects.all().count()
        tutor_count = TutorProfile.objects.all().count()
        course_count = Course.objects.filter(is_available=True).count()
        certificate_count = Certificate.objects.filter(
            is_approved=True).count()

        data = {
            'student_count': student_count,
            'tutor_count': tutor_count,
            'course_count': course_count,
            'certificate_count': certificate_count,
        }

        serializer = CountSerializer(data)
        return Response(serializer.data)


class MonthlyCoursesSoldView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        monthly_courses_sold = CoursePurchase.objects \
            .annotate(month=TruncMonth('created_at')) \
            .values('month') \
            .annotate(course_details=Count('id')) \
            .order_by('month')

        data = list(monthly_courses_sold)

        # Fetch course details for each month
        for entry in data:
            courses = CoursePurchase.objects.filter(
                created_at__month=entry['month'].month)
            entry['courses'] = [{"course_price": course.course.price}
                                for course in courses]
        total_amount_data = []

        for entry in data:
            courses = entry.get('courses', [])
            total_amount = sum(float(course.get('course_price', 0))
                               for course in courses)

            total_amount_data.append({
                'month': entry['month'],
                'total_amount': total_amount,
            })
        print(total_amount_data, "------------------------------->>>>")
        data = {
            "data": total_amount
        }
        return JsonResponse(total_amount_data, safe=False)
