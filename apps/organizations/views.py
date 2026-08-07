from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Organization
from .serializers import OrganizationSerializer
from .permissions import IsOrganizationOwner


class OrganizationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        organization = serializer.save(owner=self.request.user)

        organization.members.add(self.request.user)


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [
        IsAuthenticated,
        IsOrganizationOwner,
    ]

    def get_queryset(self):
        return Organization.objects.filter(members=self.request.user)
