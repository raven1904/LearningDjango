from rest_framework.permissions import BasePermission
from .models import Membership

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


class IsOrganizationOwnerOrMemberReadOnly(BasePermission):
    """
    Allow any organization member to view the organization,
    but only the owner may modify or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return Membership.objects.filter(
                organization=obj,
                user=request.user,
            ).exists()
        return obj.owner == request.user


class IsOrganizationMember(BasePermission):
    """
    Allows access only to users who belong to the organization.
    """

    def has_permission(self, request, view):
        organization_id = view.kwargs.get("organization_id")
        if organization_id is None:
            return False

        return Membership.objects.filter(
            organization_id=organization_id,
            user=request.user,
        ).exists()

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return Membership.objects.filter(
            organization=obj,
            user=request.user,
        ).exists()


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
        return Membership.objects.filter(
            organization=obj,
            user=request.user,
            role__in=[
                Membership.Role.OWNER,
                Membership.Role.ADMIN,
            ],
        ).exists()


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
        if request.method == "DELETE" and obj.user == request.user:
            # Allow non-owner members to remove themselves from the organization.
            return obj.role != Membership.Role.OWNER

        requester_membership = Membership.objects.filter(
            organization=obj.organization,
            user=request.user,
        ).first()

        if requester_membership is None:
            return False

        if requester_membership.role not in (
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
        ):
            return False

        if obj.role == Membership.Role.OWNER:
            return False

        return True
