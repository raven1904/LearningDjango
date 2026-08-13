from rest_framework.permissions import BasePermission
from .models import Membership, Organization
from .policies import is_owner, is_member, is_admin, can_manage_members

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
        return is_owner(request.user, obj)


class IsOrganizationOwnerOrMemberReadOnly(BasePermission):
    """
    Allow any organization member to view the organization,
    but only the owner may modify or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return is_member(request.user, obj)
        return is_owner(request.user, obj)


class IsOrganizationMember(BasePermission):
    """
    Allows access only to users who belong to the organization.
    """

    def has_permission(self, request, view):
        organization_id = view.kwargs.get("organization_id")
        if organization_id is None:
            return False

        # Use policies helper for membership checks

        try:
            organization = Organization.objects.get(pk=organization_id)
        except Organization.DoesNotExist:
            return False

        return is_member(request.user, organization)

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return is_member(request.user, obj)


class IsOrganizationAdmin(BasePermission):
    """
    Allows organization owners and admins.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return is_admin(request.user, obj)


class CanManageMembership(BasePermission):
    """
    Owners and admins can manage memberships. Non-owner members may leave the organization.
    Nobody can modify the organization owner through this endpoint.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        # obj is a Membership instance representing the target membership
        if request.method == "DELETE" and obj.user == request.user:
            # Allow non-owner members to remove themselves from the organization.
            return obj.role != Membership.Role.OWNER

        # Allow only admins/owners to manage memberships
        if not can_manage_members(request.user, obj.organization):
            return False

        # Protect owner membership from being modified
        if obj.role == Membership.Role.OWNER:
            return False

        return True
