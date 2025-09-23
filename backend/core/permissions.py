from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission: only the creator (created_by) of an Article can edit/delete.
    """
    def has_object_permission(self, request, view, obj):
        # Always allow GET, HEAD, OPTIONS
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "created_by", None) == request.user


class IsCommentOwnerOrReadOnly(BasePermission):
    """
    Object-level permission: only the user who wrote a Comment can edit/delete.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "author", None) == request.user


class ReadOnly(BasePermission):
    """
    Read-only permission, useful for Author/Tag/Authorship/ArticleTag endpoints
    if you expose them directly.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
