from rest_framework import serializers
from .models import Organization
from .models import Membership

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


class MembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Membership
        fields = (
            "id",
            "user",
            "username",
            "role",
            "joined_at",
        )

        read_only_fields = (
            "id",
            "username",
            "joined_at",
        )
