from django.db import models
from django.db.models import Model
from users.models import TutorProfile, StudentProfile, CustomUser
# Create your models here.
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver


class CommonFields(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    tutor_id = models.ForeignKey(TutorProfile, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=100, default=None)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.FileField(upload_to="course images/", blank=True, null=True)
    is_available = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)

    def get_average_rating(self):
        total_rating = sum(review.rating for review in self.reviews.all())
        number_of_reviews = self.reviews.count()

        if number_of_reviews > 0:
            average_rating = total_rating / number_of_reviews
            return round(average_rating, 1)
        else:
            return 0.0

    def __str__(self):
        return self.course_name


class CourseLikes(CommonFields):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.Case)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self) -> str:
        return f"{self.user.username} Liked {self.course.course_name}"


class VideosCourse(models.Model):
    course = models.ForeignKey(
        Course, related_name="course_video", on_delete=models.CASCADE)
    video_title = models.TextField()
    video_description = models.TextField()
    is_available = models.BooleanField(default=False)
    is_free_of_charge = models.BooleanField(default=False)
    thumbnail_image = models.FileField(upload_to='video_thumbnails/')
    video = models.FileField(upload_to='course_videos/')
    likes = models.IntegerField(default=True)
    is_approved = models.BooleanField(default=False)
    comment = models.IntegerField(default=0)

    def __str__(self):
        return self.video_title


class VideoReport(CommonFields):
    video = models.ForeignKey(
        VideosCourse, on_delete=models.CASCADE, related_name="video_report")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='user_report')
    text = models.TextField()

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self) -> str:
        return f"{self.user.username} reported {self.video.video_title}"


class CourseVideoLikes(CommonFields):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    video = models.ForeignKey(VideosCourse, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self) -> str:
        return f"{self.user.username} liked {self.video.video_title}"


class CoursePurchase(models.Model):
    student = models.ForeignKey(
        StudentProfile, related_name="student_purchase", on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, related_name="purchase_course", on_delete=models.CASCADE)
    tutor = models.ForeignKey(
        TutorProfile, related_name="tutor_purchase", on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return self.student.user.username


class CourseReview(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_reviews")
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    text = models.TextField()

    def __str__(self):
        return f"Review for {self.course.course_name} by {self.user.username}"


class VideoComment(CommonFields):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='user_video_comment')
    video = models.ForeignKey(
        VideosCourse, on_delete=models.CASCADE, related_name='video_comment')
    text = models.TextField()

    def __str__(self) -> str:
        return f"{self.user.username} commented on {self.video.video_title}"
