from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

notes = [
    {"id": 1, "title": "Note-1"},
    {"id": 2, "title": "Note-2"},
]


class NoteListAPIView(APIView):
    def get(self, request):
        return Response(notes)

    def post(self, request):
        title = request.data.get("title")

        if not title:
            return Response(
                {"error": "Title is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_note = {
            "id": len(notes) + 1,
            "title": title,
        }

        notes.append(new_note)

        return Response(
            new_note,
            status=status.HTTP_201_CREATED,
        )
