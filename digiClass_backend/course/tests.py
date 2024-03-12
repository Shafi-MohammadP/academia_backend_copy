from django.test import TestCase
from django.urls import path
from .views import CreateCourse
# Create your tests here.
urlpatterns = [
    path('courseCreation/<int:pk>/', CreateCourse.as_view())


]
