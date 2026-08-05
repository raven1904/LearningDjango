from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

class User(AbstractUser):
    email = models.EmailField(
        unique=True,
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
    )
