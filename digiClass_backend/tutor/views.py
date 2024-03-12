from django.shortcuts import render
from rest_framework.views import APIView
from users.models import CustomUser, TutorProfile
from .models import Certificate
from .serializer import ApplicationFormSerializer, CertificateSerializer, CertificateTeacherSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.serializer import tutorProfileSerializer
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from course.models import Course, VideosCourse, CoursePurchase
from course.serializer import IndividualCourseSerializer, CourseVideoSerializer, CourseSerializer, PurchaseCourseSerializer
from rest_framework import generics
from django.shortcuts import get_object_or_404
# Create your views here.

# Profile Views


class CertificateConfirmation(APIView):
    def get(self, *args, **kwargs):
        tutor_id = kwargs.get('pk')
        tutor_instance = get_object_or_404(TutorProfile, id=tutor_id)
        if tutor_instance.is_certificate == True:
            data = {
                "message": True
            }
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": False
            }
            return Response(data=data, status=status.HTTP_200_OK)


class TutorProfileShow(APIView):

    def get(self, request, user_id):
        try:
            tutorProfile = TutorProfile.objects.get(user=user_id)
        except TutorProfile.DoesNotExist:
            data = {
                "message": "Tutor not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)

        serializer = tutorProfileSerializer(tutorProfile)
        extracted_id = serializer.data.get('id', None)
        data = {
            "data": extracted_id,
            "status": status.HTTP_200_OK
        }
        return Response(data=data)


class TeacherCertificate(RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationFormSerializer
    queryset = Certificate.objects.all()
    # def

    def retrieve(self, request, *args, **kwargs):
        tutor_id = kwargs.get('tutor_id')

        if not TutorProfile.objects.filter(pk=tutor_id).exists():
            data = {
                "message": "Tutor not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)
        try:
            certificate_instance = Certificate.objects.get(tutor=tutor_id)
            serializer = self.get_serializer(certificate_instance)
            data = {
                "data": serializer.data,
                "status": status.HTTP_200_OK
            }
            return Response(data=data)
        except Certificate.DoesNotExist:
            data = {
                "message": "Certificate not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)

    def update(self, request, *args, **kwargs):
        tutor_id = kwargs.get('tutor_id')
        if not TutorProfile.objects.filter(pk=tutor_id).exists():
            data = {
                "message": "Tutor not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)
        try:
            certificate_instance = Certificate.objects.get(tutor=tutor_id)
            serializer = self.get_serializer(
                certificate_instance, data=request.data, partial=True)
            if serializer.is_valid():
                tutor_instance = serializer.save()
                tutor_instance.tutor.is_certificate = True
                tutor_instance.tutor.save()
                data = {
                    "message": "Certificate updated successfully",
                    "status": status.HTTP_200_OK
                }
                return Response(data=data)
        except Certificate.DoesNotExist:
            data = {
                "message": "Certificate not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)


class TeacherFormSubmission(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        tutor_id = kwargs.get('tutor_id')

        if not TutorProfile.objects.filter(pk=tutor_id).exists():
            data = {
                "message": "Tutor not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)

        if Certificate.objects.filter(tutor=tutor_id).exists():
            data = {
                "message": "Already Submitted",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)
        serializer = ApplicationFormSerializer(data=request.data)

        if serializer.is_valid():
            teacher_form_instance = serializer.save()
            teacher_form_instance.tutor.is_certificate = True
            teacher_form_instance.tutor.save()

            data = {
                "message": "Application Submitted Successfully",
                "status": status.HTTP_200_OK
            }
            return Response(data=data)
        else:
            data = {
                "message": serializer.errors,
                "status": 400
            }
            return Response(data=data)


class CertificateView(APIView):
    def get(self, request, tutor_id):

        try:
            certificate = Certificate.objects.get(tutor=tutor_id)

            serializer = CertificateTeacherSerializer(certificate)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Certificate.DoesNotExist:
            data = {
                "message": "Certificate Not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)


class TutorProfileEdit(APIView):
    def patch(self, request, *args, **kwargs):
        tutor_id = kwargs.get('pk')

        try:
            tutor = TutorProfile.objects.get(pk=tutor_id)
        except:
            return Response({"message": "Teacher Not Found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = tutorProfileSerializer(
            instance=tutor, data=request.data, partial=True)

        if serializer.is_valid():
            if 'username' in request.data:
                user_instance = tutor.user
                user_instance.username = request.data['username']
                user_instance.save()
            serializer.save()
            data = {
                "teacherData": serializer.data,
                "message": "Profile Updated Successfully",
                "status": status.HTTP_200_OK
            }

            return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Course views


class TutorCoursesView(APIView):
    def get(self, request, *args, **kwargs):
        tutor_id = kwargs.get('pk')
        courses = Course.objects.filter(tutor_id=tutor_id, is_available=True)
        serializer = CourseSerializer(courses, many=True)
        if serializer:
            return Response(serializer.data)
        return Response({"message": "something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseVideoView(RetrieveUpdateDestroyAPIView):
    serializer_class = CourseVideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        course_id = kwargs.get('pk')
        queryset = VideosCourse.objects.filter(
            course=course_id, is_available=True, is_approved=True).order_by('-is_free_of_charge')
        return queryset

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.role == 'tutor':

            course_videos = self.get_queryset(*args, **kwargs)
            serializer = self.get_serializer(course_videos, many=True)
            data = {
                "data": serializer.data,
                "status": status.HTTP_200_OK
            }
            return Response(data=data)
        else:
            data = {
                "message": "You are not authorized person",
                "status": status.HTTP_401_UNAUTHORIZED
            }
            return Response(data=data)

    def update(self, request, *args, **kwargs):
        video_id = kwargs.get('pk')
        try:

            instance = VideosCourse.objects.get(id=video_id)
            serializer = self.get_serializer(instance=instance,
                                             data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                data = {
                    "message": "Video updated successfully",
                    "status": status.HTTP_200_OK
                }
                return Response(data=data)
            else:
                data = {
                    "message": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST
                }
                return Response(data=data)
        except VideosCourse.DoesNotExist:
            data = {
                "message": "Video not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)


class CourseVideoRetrieval(generics.ListAPIView):
    serializer_class = CourseVideoSerializer

    def get_queryset(self):
        course_id = self.kwargs.get('pk')
        queryset = VideosCourse.objects.filter(course=course_id)
        return queryset


class PurchasedStudentDetails(generics.ListAPIView):
    serializer_class = PurchaseCourseSerializer

    def get_queryset(self):
        tutor_id = self.kwargs.get('pk')
        queryset = CoursePurchase.objects.filter(tutor=tutor_id)
        return queryset
