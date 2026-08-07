from rest_framework.permissions import BasePermission

class IsOrganizationOwner(BasePermission):
    """
    Only the organization owner can modify or delete it.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return obj.owner == request.user
