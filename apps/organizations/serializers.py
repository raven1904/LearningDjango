from rest_framework import serializers
from .models import Organization, OrganizationInvitation
from .models import Membership, Team, TeamMembership
from django.contrib.auth import get_user_model


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


class OrganizationInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInvitation

        fields = (
            "id",
            "email",
            "role",
            "status",
            "expires_at",
            "created_at",
            "accepted_at",
        )

        read_only_fields = (
            "id",
            "status",
            "expires_at",
            "created_at",
            "accepted_at",
        )

    def validate_role(self, value):
        if value == Membership.Role.OWNER:
            raise serializers.ValidationError(
                "OWNER cannot be assigned through an invitation."
            )

        return value


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team

        fields = (
            "id",
            "name",
            "description",
            "created_by",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
        )


User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
        )
        read_only_fields = (
            "id",
            "username",
            "email",
        )


class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = TeamMembership

        fields = (
            "id",
            "user",
            "role",
            "joined_at",
        )

        read_only_fields = (
            "id",
            "user",
            "joined_at",
        )
