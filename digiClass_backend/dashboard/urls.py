from django.urls import path
from .views import *
from .views import CourseApproval

urlpatterns = [
    #     path('categoryOperations/<int:id>/',
    #          CourseCategoryOperation.as_view()),
    path('categoryCreating/', CategoryCreation.as_view()),
    path('categoryUpdate/<int:pk>/', CategoryUpdateAndRetrieve.as_view()),
    path('categoriesList/', CategoryList.as_view()),
    path('certificateApproval/<int:certificate_id>/',
         CertificateApproval.as_view()),
    path('certificateList/', CertificateList.as_view()),
    path('certificateView/', CertificateView.as_view()),
    path('courseList/', CourseList.as_view()),
    path('courseApproval/<int:pk>/', CourseApproval.as_view()),
    path('categoryAdding/', CategoryAdding.as_view()),
    path('categoryUpdateAndDeletion/<int:pk>/',
         CategoryUpdatingAndDeletion.as_view()),
    path('userBlockAndUnblock/<int:pk>/', UserBlockAndUnblock.as_view()),
    path('videoList/', CourseVideoView.as_view()),
    path('videoApproval/<int:pk>/', VideoApproval.as_view())


]
