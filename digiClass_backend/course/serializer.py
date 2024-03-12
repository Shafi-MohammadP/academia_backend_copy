from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from users.serializer import CustomUserSerializer, tutorProfileSerializer, studentProfileSerializer
from .models import *


class CourseCategorySerializer(ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    tutor_profile = tutorProfileSerializer(source='tutor_id', read_only=True)
    category_details = CourseCategorySerializer(
        source='category', read_only=True)
    video_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    def get_video_count(self, obj):
        return obj.course_video.count()

    def get_student_count(self, obj):
        return obj.purchase_course.count()

    def get_average_rating(self, obj):
        return obj.get_average_rating()

    class Meta:
        model = Course
        fields = '__all__'


class CommonCourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class CourseSearchSerializer (ModelSerializer):
    class Meta:
        model = Course
        fields = ["course_name", "description", "price"]


class IndividualCourseSerializer(ModelSerializer):
    category_details = CourseCategorySerializer(
        source="category", read_only=True)
    tutor_profile = tutorProfileSerializer(source='tutor_id', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class CourseWithFullDetails(ModelSerializer):
    course_details = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = VideosCourse
        fields = "__all__"


class CourseVideoSerializer(ModelSerializer):

    class Meta:
        model = VideosCourse
        fields = "__all__"


class VideoWithCourseDetails(ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = VideosCourse
        fields = "__all__"


class CourseWithAllCount(ModelSerializer):
    video_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    def get_video_count(self, obj):
        return obj.course_video.count()

    def get_student_count(self, obj):
        return obj.purchase_course.count()

    class Meta:
        model = Course
        fields = "__all__"


class CoursePurchaseSerializer(ModelSerializer):
    class Meta:
        model = CoursePurchase
        fields = "__all__"


class PurchaseCourseSerializer(ModelSerializer):
    student = studentProfileSerializer()
    course = CommonCourseSerializer()

    class Meta:
        model = CoursePurchase
        fields = "__all__"


class PurchaseListSerializer(ModelSerializer):
    class Meta:
        model = CoursePurchase
        fields = "__all__"


class PurchasedCourseDetailsSerializer(ModelSerializer):
    # tutor_details = tutorProfileSerializer(source="tutor", read_only = True)
    course_details = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = CoursePurchase
        fields = "__all__"


class LikeSerializer(ModelSerializer):

    class Meta:
        model = CourseLikes
        fields = "__all__"


class VideoLikeSerializer(ModelSerializer):
    class Meta:
        model = CourseVideoLikes
        fields = "__all__"


class CourseLikeListSerializer(ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = CourseLikes
        fields = "__all__"


class VideoLikeListSerializer(ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = CourseVideoLikes
        fields = "__all__"


class CourseReviewSerializer(ModelSerializer):
    class Meta:
        model = CourseReview
        fields = "__all__"


class CourseReviewListSerializer(ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = CourseReview
        fields = "__all__"


class VideoReportSerializer(ModelSerializer):
    class Meta:
        model = VideoReport
        fields = "__all__"


class VideoReportListSerializer(ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = VideoReport
        fields = "__all__"


class VideoCommentSerializer(ModelSerializer):
    class Meta:
        model = VideoComment
        fields = "__all__"


class VideoCommentListSerializer(serializers.ModelSerializer):
    student_profile_photo = serializers.SerializerMethodField()
    tutor_profile_photo = serializers.SerializerMethodField()
    user = CustomUserSerializer()

    def get_student_profile_photo(self, obj):
        try:
            student_profile = obj.user.student_user
            if student_profile and student_profile.profile_photo:
                return student_profile.profile_photo.url
        except StudentProfile.DoesNotExist:
            pass
        return None

    def get_tutor_profile_photo(self, obj):
        try:
            tutor_profile = obj.user.tutor_user
            if tutor_profile and tutor_profile.profile_photo:
                return tutor_profile.profile_photo.url
        except TutorProfile.DoesNotExist:
            pass
        return None

    class Meta:
        model = VideoComment
        fields = ["user", "student_profile_photo", "video",
                  "text", "created_at", "tutor_profile_photo"]
