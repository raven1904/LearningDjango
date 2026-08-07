from rest_framework import serializers
from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "members",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "owner",
            "members",
            "created_at",
            "updated_at",
        )
