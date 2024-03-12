from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'courseSearch', CourseSearching)
urlpatterns = [
    path('courseAdding/<int:tutor_id>/', CourseAdding.as_view()),
    path('videoAdding/<int:course_id>/', CourseVideoAdding.as_view()),
    # path('createCourse/<int:pk>/', CreateCourse.as_view()),
    path('courseList/', CourseList.as_view()),
    path('courseDetailview/<int:pk>/', CourseDetailView.as_view()),
    path('courseCategoryBase/<int:pk>/', CourseCategoryBaseRetrieval.as_view()),
    path('updateCourse/<int:tutor_id>/<int:pk>/', updateCourse.as_view()),
    path('categoryList/', CategoryList.as_view()),
    path('', include(router.urls)),
    path('purchase_course/', PurchaseCourseApi.as_view()),
    path('stripe_payment/', StripePaymentApi.as_view()),
    path('course_like/', AddLikesToCourse.as_view()),
    path('course_video_like/', AddLikeToCourseVideos.as_view()),
    path("course_like_list/<int:userId>/", ListCourseLikes.as_view()),
    path("video_like_list/<int:userId>/", ListVideoLikeApi.as_view()),
    path('course_review/', CourseReviewAdding.as_view()),
    path('user_course_review_list/<int:pk>/', UserCourseReviewList.as_view()),
    path('course_review_list/<int:pk>/', CourseReviewList.as_view()),
    path('review_edit/<int:pk>/', CorseReviewEdit.as_view()),
    path('video_report/', VideoReporting.as_view()),
    path('video_report_list/<int:pk>/', ListVideoReport.as_view()),
    path('video_comment/', VideoCommentApi.as_view()),
    path('purchase_student_list/<int:pk>/', PurchasedStudentList.as_view()),
    path("video_comment_list/<pk>/", VideoCommentListing.as_view()),
    path('video_comment_user_listing/<int:pk>/',
         VideoCommentUserListing.as_view())

]
