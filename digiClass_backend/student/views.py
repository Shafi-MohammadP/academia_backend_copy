from django.shortcuts import render
from rest_framework.views import APIView
from users.models import StudentProfile
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework import generics
from users.serializer import studentProfileSerializer
from course.models import *
from course.serializer import *
# Create your views


class StudentProfileEdit(APIView):

    def patch(self, request, *args, **kwargs):
        student_id = kwargs.get('pk')
        try:
            student = StudentProfile.objects.get(pk=student_id)
        except StudentProfile.DoesNotExist:
            data = {
                "message": "Student not found"
            }
            return Response(data=data)

        serializer = studentProfileSerializer(
            instance=student, data=request.data, partial=False)

        if serializer.is_valid():
            if 'username' in request.data:
                user_instance = student.user
                user_instance.username = request.data['username']
                user_instance.save()
            serializer.save()

            data = {
                "userData": serializer.data,
                "message": "Profile Updated Successfully",
                "status": status.HTTP_200_OK,


            }
            return Response(data=data)
        else:
            data = {
                "message": serializer.errors,
                "status": status.HTTP_400_BAD_REQUEST
            }
            return Response(data=data)


class StudentProfileShow(APIView):
    def get(self, request, student_id):
        try:
            studentProfile = StudentProfile.objects.get(user=student_id)
        except StudentProfile.DoesNotExist:
            data = {
                "message": "Student not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        serializer = studentProfileSerializer(studentProfile)
        extract_id = serializer.data.get('id', None)
        data = {
            "data": extract_id,
            "status": status.HTTP_200_OK
        }
        return Response(data=data, status=status.HTTP_200_OK)


class CourseDetailView(RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = IndividualCourseSerializer


class FreeCourseView(generics.ListAPIView):
    queryset = VideosCourse.objects.filter(
        is_available=True, is_approved=True, is_free_of_charge=True)
    serializer_class = CourseWithFullDetails


class CourseDetailsBeforePurchase(generics.RetrieveAPIView):
    serializer_class = CourseVideoSerializer

    def get_queryset(self):
        return VideosCourse.objects.filter(
            is_available=True, is_approved=True)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        course_id = self.kwargs.get('course_id')
        if course_id:
            queryset = queryset.filter(course=course_id).order_by('id')
            instances = queryset.all()
            if not instances:
                return Response([], status=status.HTTP_200_OK)

            serializer = self.get_serializer(instances, many=True)
            return Response(serializer.data)


class PurchasedCourseRetrieval(generics.ListAPIView):
    serializer_class = PurchaseCourseSerializer

    def get_queryset(self):
        student_id = self.kwargs.get('pk')

        return CoursePurchase.objects.filter(student=student_id)


class PurchasedCourseDetails(generics.ListAPIView):
    serializer_class = PurchasedCourseDetailsSerializer

    def get_queryset(self):
        student_id = self.kwargs.get('pk')

        return CoursePurchase.objects.filter(student=student_id)
