# your_app/permissions.py

from rest_framework.permissions import BasePermission


class IsReviewAuthor(BasePermission):
    """
    Custom permission to only allow the author of a review to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user associated with the review is the same as the request user
        return obj.user == request.user
