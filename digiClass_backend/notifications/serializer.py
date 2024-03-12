from rest_framework import serializers
from .models import AdminNotifications, Notifications
from users.serializer import TutorProfile
from course.serializer import CourseSerializer


class AdminNotificationSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = AdminNotifications
        fields = "__all__"


class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"
