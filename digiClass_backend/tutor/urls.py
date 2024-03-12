from django.urls import include, path
from .views import *
urlpatterns = [
    path('TutorProfileShow/<int:user_id>/', TutorProfileShow.as_view()),
    path('application_form/<int:tutor_id>/',
         TeacherFormSubmission.as_view()),
    path('profileEdit/<int:pk>/', TutorProfileEdit.as_view()),
    path('certificateView/<int:tutor_id>/', CertificateView.as_view()),
    path('TutorCoursesView/<int:pk>/', TutorCoursesView.as_view()),
    path('tutorCertificate/<int:tutor_id>/', TeacherCertificate.as_view()),
    path('course_video/<int:pk>/', CourseVideoView.as_view()),
    path('course_video_retrieval/<int:pk>/', CourseVideoRetrieval.as_view()),
    path('certificate_confirmation/<int:pk>/',
         CertificateConfirmation.as_view()),
    path('purchased_student/<int:pk>/', PurchasedStudentDetails.as_view())


]
