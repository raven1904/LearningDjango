from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Organization
from .serializers import OrganizationSerializer
from .permissions import IsOrganizationOwner

from .models import Membership
from django.db import transaction


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
        return Organization.objects.filter(memberships__user=self.request.user).distinct()
