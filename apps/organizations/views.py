from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOrganizationOwner, IsOrganizationMember, CanManageMembership
from django.db import transaction
from .models import Organization, Membership

from .serializers import (
    OrganizationSerializer,
    MembershipSerializer,
    MembershipRoleSerializer,
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
