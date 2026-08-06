from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name")

    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Username is required.")
        return value.strip()

    def validate_email(self, value):
        value = value.lower().strip()
        if not value:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")

        if username and email and username == email:
            raise serializers.ValidationError(
                {"username": "Username cannot be the same as email."}
            )

        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": "A user with that username already exists."}
            )

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
