from django.urls import path
from .import views

urlpatterns = [
    path('login/', views.MyTokenObtainPairView.as_view()),
    path('googlelogin/', views.GooglLogin.as_view()),
    path('activate/<uidb64>/<token>/',
         views.ActivateAccountView, name='activate'),
    path('signup/', views.Common_signup.as_view()),
    path('reset_password_otp_verify/', views.ResetPassword.as_view()),
    path('password_change/<int:pk>/', views.PasswordChange.as_view()),
    # Student
    path('studentProfile/<int:user_id>/', views.studentProfileView.as_view(),
         name='studentProfileView'),
    # Tutor
    path('tutorProfile/<int:user_id>/',
         views.tutorProfileView.as_view(), name='tutorProfile'),

    # Admin
    path('studentList/', views.studentListing.as_view()),
    path('tutorListing/', views.tutorListing.as_view(), name='tutorListing'),
    path('ppurl/', views.NewTutoraLisiting.as_view()),
    #     path('authentication/', views.Authentication.as_view(), name='Authentication'),


]
