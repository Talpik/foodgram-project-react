from rest_framework.permissions import BasePermission


class IsOwnerOrAdminOrReadOnly(BasePermission):
    """
    Class for checking the permissions of users
    to execute certain requests to the API.
    """
    def has_permission(self, request, view):
        """
        Only authenticated users are allowed to post requests.

        """
        if request.method == "POST":
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        """
        The method allows the execution of queries to users -
        who are the author of these objects,
        or this user is a superuser, or these are safe methods.

        """
        if request.method in ("GET", "HEAD", "OPTIONS") or request.user.is_superuser:
            return True
        return request.user == obj.author
