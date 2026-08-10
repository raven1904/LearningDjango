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


class MembershipRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ("role",)

    def validate_role(self, value):
        if value == Membership.Role.OWNER:
            raise serializers.ValidationError(
                "Ownership cannot be assigned through this endpoint."
            )

        return value
