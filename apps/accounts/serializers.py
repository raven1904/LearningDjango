from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        return value

    def validate(self, attrs):
        if attrs["username"] == attrs["email"]:
            raise serializers.ValidationError("Username cannot be the same as email.")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
