from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
