from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from course.models import CourseCategory


class CountSerializer(serializers.Serializer):
    student_count = serializers.IntegerField()
    tutor_count = serializers.IntegerField()
    course_count = serializers.IntegerField()
    certificate_count = serializers.IntegerField()
