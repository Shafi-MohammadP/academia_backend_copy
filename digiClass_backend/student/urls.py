from django.urls import path
from .views import *
urlpatterns = [
    path('profileEdit/<int:pk>/', StudentProfileEdit.as_view()),
    path('StudentProfileShow/<int:student_id>/',
         StudentProfileShow.as_view()),
    path('courseDetailView/<int:pk>/', CourseDetailView.as_view()),
    path('courseDetailsBeforePurchase/<int:course_id>/',
         CourseDetailsBeforePurchase.as_view()),
    path('freeCourseView/', FreeCourseView.as_view()),
    path('purchasedCourse/<int:pk>/', PurchasedCourseRetrieval.as_view()),
    path('purchased_course_details/<int:pk>/',
         PurchasedCourseDetails.as_view()),
]
