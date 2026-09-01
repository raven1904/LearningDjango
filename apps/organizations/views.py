from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

import secrets
from datetime import timedelta

from .permissions import IsOrganizationOwner, IsOrganizationMember, CanManageMembership
from .models import Organization, Membership, OrganizationInvitation, Team
from .policies import*
import policies

from .serializers import (
    OrganizationSerializer,
    MembershipSerializer,
    MembershipRoleSerializer,
    OrganizationInvitationSerializer,
    TeamSerializer
)


class OrganizationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(members=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        organization = serializer.save(owner=self.request.user)

        Membership.objects.create(
            organization=organization,
            user=self.request.user,
            role=Membership.Role.OWNER,
        )


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [
        IsAuthenticated,
        IsOrganizationOwner,
    ]

    def get_queryset(self):
        return Organization.objects.filter(
            memberships__user=self.request.user
        ).distinct()


class OrganizationMemberListView(generics.ListAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        organization_id = self.kwargs.get("organization_id")

        return Membership.objects.filter(
            organization_id=organization_id,
            organization__memberships__user=self.request.user,
        ).select_related("user")


class OrganizationMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MembershipRoleSerializer
    permission_classes = [
        IsAuthenticated,
        CanManageMembership,
    ]

    def get_queryset(self):
        return Membership.objects.filter(
            organization_id=self.kwargs.get("organization_id")
        )


class OrganizationInvitationCreateView(generics.CreateAPIView):
    serializer_class = OrganizationInvitationSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(self, serializer):
        organization_id = self.kwargs["organization_id"]

        organization = get_object_or_404(
            Organization,
            pk=organization_id,
        )

        membership = get_object_or_404(
            Membership,
            organization=organization,
            user=self.request.user,
        )

        if not can_manage_members(
            self.request.user,
            organization,
        ):
            raise PermissionDenied(
        "You cannot invite members."
    )

        token = secrets.token_urlsafe(48)

        serializer.save(
            organization=organization,
            invited_by=self.request.user,
            token=token,
            expires_at=timezone.now() + timedelta(days=7),
        )


class OrganizationInvitationAcceptView(generics.GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, token):
        invitation = get_object_or_404(
            OrganizationInvitation,
            token=token,
        )

        if invitation.status != (OrganizationInvitation.Status.PENDING):
            raise ValidationError("This invitation is no longer active.")

        if invitation.is_expired:
            invitation.status = OrganizationInvitation.Status.EXPIRED
            invitation.save(update_fields=["status"])

            raise ValidationError("This invitation has expired.")

        if request.user.email.lower() != (invitation.email.lower()):
            raise PermissionDenied("This invitation belongs to another email address.")

        with transaction.atomic():
            Membership.objects.create(
                organization=invitation.organization,
                user=request.user,
                role=invitation.role,
            )

            invitation.status = OrganizationInvitation.Status.ACCEPTED
            invitation.accepted_at = timezone.now()

            invitation.save(
                update_fields=[
                    "status",
                    "accepted_at",
                ]
            )

        return Response(
            {"detail": ("Invitation accepted successfully.")},
            status=status.HTTP_200_OK,
        )


class TeamCreateView(generics.CreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(self, serializer):
        organization = get_object_or_404(
            Organization,
            pk=self.kwargs["organization_id"],
        )

        if not policies.can_create_team(
            self.request.user,
            organization,
        ):
            raise PermissionDenied("You cannot create teams.")

        serializer.save(
            organization=organization,
            created_by=self.request.user,
        )


class TeamListView(generics.ListAPIView):
    serializer_class = TeamSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        organization = get_object_or_404(
            Organization,
            pk=self.kwargs["organization_id"],
        )

        if not policies.can_view_organization(
            self.request.user,
            organization,
        ):
            raise PermissionDenied("You are not a member of this organization.")

        return Team.objects.filter(
            organization=organization,
        ).select_related(
            "created_by",
        )
