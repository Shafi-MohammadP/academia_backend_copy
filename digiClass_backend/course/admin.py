from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CourseCategory)
admin.site.register(VideosCourse)
admin.site.register(Course)
admin.site.register(CoursePurchase)
admin.site.register(CourseLikes)
admin.site.register(CourseVideoLikes)
admin.site.register(CourseReview)
admin.site.register(VideoReport)
admin.site.register(VideoComment)
