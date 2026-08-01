from django.urls import path

from .views import NoteListAPIView

urlpatterns = [
    path(
        "notes/",
        NoteListAPIView.as_view(),
        name="note-list",
    ),
]
