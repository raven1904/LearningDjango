from django.urls import path

from .views import RegisterView, ProfileView

urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    path(
            "profile/",
            ProfileView.as_view(),
            name="profile",
        ),
]
