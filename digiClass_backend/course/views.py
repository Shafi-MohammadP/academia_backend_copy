from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
import stripe
from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import TutorProfile
from tutor.models import Certificate
from .models import Course, CourseCategory, VideosCourse
from .serializer import *
from rest_framework import status, viewsets, filters
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from users.models import CustomUser
from collections import defaultdict
from django.db.models import Count
from django.http import Http404
from decouple import config
from django.shortcuts import get_object_or_404
from course.permissions import IsReviewAuthor
from channels.layers import get_channel_layer
# Create your views here.
fronted_url = config('frontend_urls')


async def send_comment_update(videoId, message):
    channel_layer = get_channel_layer()
    group_name = f"video_{videoId}"
    await channel_layer.group_send(
        "users_group", {
            'type': "create_comment_update",
            'message': message
        }
    )


class CourseAdding(CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            tutor_id = kwargs.get('tutor_id')
            certificate = Certificate.objects.get(tutor=tutor_id)

            if not certificate.is_approved:
                data = {
                    "message": "Wait for Admin approval of your certificate",
                    "status": status.HTTP_401_UNAUTHORIZED
                }
                return Response(data=data)
            else:
                tutor = TutorProfile.objects.get(pk=tutor_id)
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    self.perform_create(serializer)
                    headers = self.get_success_headers(serializer.data)
                    data = {
                        "message": "Course added successfully",
                        "status": status.HTTP_200_OK
                    }
                else:
                    data = {
                        "message": serializer.errors,
                        "status": status.HTTP_400_BAD_REQUEST
                    }
                return Response(data=data)

        except Certificate.DoesNotExist:
            data = {
                "message": "Certificate not found",
                "status": status.HTTP_404_NOT_FOUND,
            }
            return Response(data=data)
        except TutorProfile.DoesNotExist:
            data = {
                "message": "Tutor not found",
                "status": status.HTTP_404_NOT_FOUND,
            }
            return Response(data=data)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        serializer.save()


class CourseVideoAdding(CreateAPIView):
    queryset = VideosCourse.objects.all()
    serializer_class = CourseVideoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = self.request.user
        course_id = request.data.get('course_id')
        print(course_id, "------------------------------->>>>")
        try:
            if user.role == 'tutor':
                course = Course.objects.get(id=course_id)
                non_file_data = {
                    'video_title': request.data.get('video_title'),
                    'video_description': request.data.get('video_description'),
                    'course': course.id,
                    'is_available': True,
                    'is_free_of_charge': request.data.get('is_free_of_charge', False)

                }

                data = non_file_data.copy()
                thumbnail_image = request.data.get('thumbnail_image')
                video = request.data.get('video')
                if thumbnail_image:
                    data['thumbnail_image'] = thumbnail_image

                if video:
                    data['video'] = video
                serializer = self.get_serializer(data=data)
                if serializer.is_valid():
                    self.perform_create(serializer)
                    response_data = {
                        "message": "Video uploaded Successfully",
                        "status": status.HTTP_201_CREATED
                    }
                    return Response(data=response_data)
                else:
                    error_data = {
                        'message': "Invalid video data",
                        "errors": serializer.errors,
                        "status": status.HTTP_400_BAD_REQUEST
                    }
                    return Response(data=error_data, status=status.HTTP_400_BAD_REQUEST)

            else:
                unauthorized_data = {
                    "message": "You are not authorized to upload videos",
                    "status": status.HTTP_401_UNAUTHORIZED
                }
                return Response(data=unauthorized_data, status=status.HTTP_401_UNAUTHORIZED)

        except Course.DoesNotExist:
            not_found_data = {
                "message": "Course Not Found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=not_found_data, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        serializer.save()


class updateCourse(RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = IndividualCourseSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        try:
            user = self.request.user
            if not user.role == 'tutor':
                data = {
                    "message": "You are not authorized to Edit Course",
                    "status": status.HTTP_403_FORBIDDEN
                }
                return Response(data=data)
            tutor_id = self.kwargs.get('tutor_id')
            course_id = self.kwargs.get('pk')
            course_details = Course.objects.get(
                pk=course_id, tutor_id=tutor_id)
            serializer = self.get_serializer(
                instance=course_details, data=request.data, partial=True)
            if serializer.is_valid():
                self.perform_update(serializer)
                data = {
                    "message": "Course Updated Successfully",
                    "status": status.HTTP_200_OK
                }
            else:
                data = {
                    "message": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST,
                }
            return Response(data=data)
        except Course.DoesNotExist:
            data = {
                "message": "Course not found",
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(data=data)

    def perform_update(self, serializer):
        serializer.save()


stripe.api_key = config('STRIP_API_KEY')


class StripePaymentApi(APIView):
    def post(self, request):
        try:
            data = request.data
            print(data, "====================>>>")
            userId = data.get('userId')
            courseId = data.get('courseId')
            course_price = data.get('course_price')
            tutor_id = data.get('tutor_id')
            success_url = f'{fronted_url}payment/success?userId={userId}&courseId={courseId}&tutorId={tutor_id}&xyzeconmy/'
            cancel_url = f'{fronted_url}payment/canceled=true'
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': data.get('currency', 'INR'),
                        'product_data': {
                            'name': data.get('course_name', 'sample'),
                        },
                        'unit_amount': course_price * 100
                    },
                    'quantity': data.get('quantity', 1),
                }],
                mode=data.get('mode', 'payment'),
                success_url=success_url,
                cancel_url=cancel_url,
            )

            return Response({"message": session}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PurchaseCourseApi(CreateAPIView):
    queryset = CoursePurchase.objects.all()
    serializer_class = CoursePurchaseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        student_id = request.data.get('student')
        course_id = request.data.get('course')
        tutor_id = request.data.get('tutor')
        print(request.data, "oooooooooooooooo")
        try:
            course_instance = Course.objects.get(
                id=course_id, is_available=True)
            student_instance = StudentProfile.objects.get(id=student_id)
            tutor_instance = TutorProfile.objects.get(id=tutor_id)
            tutor_instance.wallet += course_instance.price
            tutor_instance.save()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer, course_instance,
                                student_instance, tutor_instance)

            headers = self.get_success_headers(serializer.data)
            data = {
                # "message": f"{course_instance.course_name} Purchased Successfully",
                "message": "purchased successfully",
                "status": status.HTTP_201_CREATED
            }
            return Response(data=data, status=status.HTTP_201_CREATED, headers=headers)

        except Course.DoesNotExist:
            return Response({"error": "Course not available"}, status=status.HTTP_404_NOT_FOUND)

        except (StudentProfile.DoesNotExist, TutorProfile.DoesNotExist):
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer, course_instance, student_instance, tutor_instance):
        serializer.save(course=course_instance,
                        student=student_instance, tutor=tutor_instance)


class CourseDetailView(RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = IndividualCourseSerializer


class CourseList(ListAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.filter(is_available=True)


class CategoryList(ListAPIView):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer


class CourseSearching(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_available=True)
    serializer_class = CourseSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['course_name', 'price', 'description']


class CourseCategoryBaseRetrieval(ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        category_id = self.kwargs.get('pk')
        print(category_id, "----------------->>>")
        return Course.objects.filter(is_available=True, category=category_id)


class AddLikesToCourse(APIView):
    serializer_class = LikeSerializer

    def post(self, request):
        user_id = int(self.request.data.get("userId"))
        course_id = int(self.request.data.get("courseId"))
        user = get_object_or_404(CustomUser, id=user_id)
        course = get_object_or_404(Course, id=course_id)

        if not CourseLikes.objects.filter(user=user, course=course).exists():
            course.likes += 1
            course.save()
            like_add = CourseLikes(user=user, course=course)
            like_add.save()
            # data = {
            #     "message": "Like added",
            #     "status":status.HTTP_200_OK
            # }
            message = "Like added"
        else:
            remove_like = CourseLikes.objects.filter(
                user=user_id, course=course_id)
            course.likes = max(0, course.likes - 1)
            course.save()
            remove_like.delete()
            message = "Like removed"
        data = {
            "message": message,
            "status": status.HTTP_200_OK
        }
        return Response(data=data)


class AddLikeToCourseVideos(APIView):
    def post(self, request):
        user_id = int(request.data.get("userId"))
        video_id = int(request.data.get("videoId"))
        user = get_object_or_404(CustomUser, id=user_id)
        video = get_object_or_404(VideosCourse, id=video_id)

        if not CourseVideoLikes.objects.filter(user=user, video=video).exists():
            video.likes += 1
            video.save()
            like_add = CourseVideoLikes(user=user, video=video)
            like_add.save()
            serializer = VideoLikeSerializer(like_add)
            message = "Like Added"
            info = serializer.data
        else:
            remove_like = CourseVideoLikes.objects.filter(
                user=user_id, video=video_id)
            video.likes = max(0, video.likes - 1)
            video.save()
            remove_like.delete()
            message = "Like removed"
            info = None
        data = {
            "message": message,
            "info": info,
            "status": status.HTTP_200_OK
        }
        return Response(data=data)


class VideoReporting(APIView):

    def post(self, request):
        user_id = request.data.get('user')
        video_id = request.data.get('video')
        user = get_object_or_404(CustomUser, id=user_id)
        video = get_object_or_404(VideosCourse, id=video_id)
        if VideoReport.objects.filter(user=user_id, video=video_id).exists():
            return Response({"message": "Already Reported"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = VideoReportSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = {
                "message": "Video Reported Successfully"
            }
            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            data = {
                "message": serializer.errors
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # report_add  =  VideoReport(user = user, video = video, text = request.data.get('text'))


class ListCourseLikes(ListAPIView):
    serializer_class = CourseLikeListSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('userId')
        queryset = CourseLikes.objects.filter(user=user_id)
        return queryset


class ListVideoLikeApi(ListAPIView):
    serializer_class = VideoLikeListSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("userId")
        queryset = CourseVideoLikes.objects.filter(user=user_id)
        return queryset


class ListVideoReport(ListAPIView):
    serializer_class = VideoReportListSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        queryset = VideoReport.objects.filter(user=user_id)
        return queryset


class CourseReviewAdding(CreateAPIView):
    serializer_class = CourseReviewSerializer

    def create(self, request, *args, **kwargs):
        print(request.data, "------------------------->>>")
        user = request.user
        course_id = request.data.get('course')
        if not CourseReview.objects.filter(user=user.id, course=course_id).exists():
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                data = {
                    "message": "Review added successfully",
                    "status": status.HTTP_201_CREATED
                }
                return Response(data=data)
            else:
                data = {
                    "message": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST
                }
            return Response(data=data)
        else:
            data = {
                'message': "Your review already added",
                "status": status.HTTP_400_BAD_REQUEST
            }
            return Response(data=data)


class UserCourseReviewList(ListAPIView):
    serializer_class = CourseReviewListSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        queryset = CourseReview.objects.filter(user=user_id)
        return queryset


class CourseReviewList(ListAPIView):
    serializer_class = CourseReviewListSerializer

    def get_queryset(self):
        course_id = self.kwargs.get("pk")
        queryset = CourseReview.objects.filter(course=course_id)
        return queryset


class CorseReviewEdit(RetrieveUpdateAPIView):
    serializer_class = CourseReviewSerializer
    queryset = CourseReview.objects.all()

    def update(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        user_id = request.data.get('user')
        review_id = kwargs.get('pk')
        review_instance = get_object_or_404(
            CourseReview, id=review_id, user=user_id, course=course_id)

        if CourseReview.objects.filter(user=user_id, course=course_id).exists():

            serializer = self.get_serializer(
                instance=review_instance, data=request.data, partial=True)
            if serializer.is_valid():
                self.perform_update(serializer)
                data = {
                    "info": serializer.data,
                    "message": "Review edited successfully",
                    "status": status.HTTP_200_OK
                }
                return Response(data=data)
            else:
                data = {
                    "message": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST
                }
                return Response(data=data)
        else:
            return Response({"error: Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)

    def perform_update(self, serializer):
        serializer.save()


class VideoCommentApi(APIView):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"message": "Authentication required for commenting."},
                            status=status.HTTP_401_UNAUTHORIZED)
        video_id = request.data.get('video')
        video_instance = get_object_or_404(VideosCourse, id=video_id)
        user = request.user
        print(user, "-------------------------->>")
        serializer = VideoCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            video_instance.comment += 1
            video_instance.save()
            data = {
                "message": "Comment added successfully"

            }
            video_id = request.data.get('video')
            message = 'New comment added!'
            async_to_sync(send_comment_update)(video_id, message)
            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        created_at = request.data.get('created_at')
        user_id = request.data.get('user')
        video_id = request.data.get('video')

        # Parse the created_at string to a datetime object
        created_at_dt = parse_datetime(created_at)

        try:
            comment_instance = VideoComment.objects.get(
                created_at=created_at_dt,
                user__id=user_id,
                video=video_id
            )
        except VideoComment.DoesNotExist:
            data = {
                "message": "Comment not found."
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        serializer = VideoCommentSerializer(
            instance=comment_instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = {
                "message": "Comment updated successfully."
            }
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": serializer.errors
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

# button removing


class PurchasedStudentList(ListAPIView):
    serializer_class = PurchaseCourseSerializer

    def get_queryset(self):
        student_id = self.kwargs.get('pk')
        queryset = CoursePurchase.objects.filter(student=student_id)
        return queryset


class VideoCommentListing(ListAPIView):
    serializer_class = VideoCommentListSerializer

    def get_queryset(self):
        video_id = self.kwargs.get('pk')
        queryset = VideoComment.objects.filter(video=video_id)
        return queryset


class VideoCommentUserListing(ListAPIView):
    serializer_class = VideoCommentListSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        queryset = VideoComment.objects.filter(user=user_id)
        return queryset
