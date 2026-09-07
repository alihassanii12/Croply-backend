from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsFarmer(BasePermission):
    """Allow access only to users with the farmer role."""

    message = 'Only farmers can perform this action.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.is_farmer
        except Exception:
            return False


class IsBuyer(BasePermission):
    """Allow access only to users with the buyer role."""

    message = 'Only buyers can perform this action.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.is_buyer
        except Exception:
            return False


class IsFarmerOrReadOnly(BasePermission):
    """
    Read access for any authenticated user.
    Write access only for farmers.
    """

    message = 'Only farmers can create or modify listings.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        try:
            return request.user.profile.is_farmer
        except Exception:
            return False


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level: read for any authenticated user,
    write only for the object's owner.
    Expects obj.owner or obj.seller or obj.user attribute.
    """

    message = 'You can only modify your own resources.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = (
            getattr(obj, 'owner', None)
            or getattr(obj, 'seller', None)
            or getattr(obj, 'user', None)
        )
        return owner == request.user
