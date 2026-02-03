from rest_framework import generics, permissions, status
from .models import Room, RoomParticipant
from .serializers import RoomSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class RoomListView(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Room.objects.filter(
            participants__user=self.request.user,
            participants__is_active=True,
        ).distinct()


class RoomDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            participant = RoomParticipant.objects.get(room_id=pk, user=user)
            participant.is_active = False
            participant.save()
            return Response(
                {"detail": "Room eliminado para el usuario."}, status=status.HTTP_200_OK
            )
        except RoomParticipant.DoesNotExist:
            return Response(
                {"detail": "Room no encontrada o ya eliminada."},
                status=status.HTTP_404_NOT_FOUND,
            )


class LastRoomView(generics.RetrieveAPIView):
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return (
            Room.objects.filter(
                participants__user=self.request.user, participants__is_active=True
            )
            .order_by("-created_at")  # la más reciente
            .first()
        )


class FindRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        other_user_id = request.query_params.get("user_id")

        if not other_user_id:
            return Response({"exists": False})

        rooms = (
            Room.objects.filter(
                participants__user=user,
                participants__is_active=True,
            )
            .filter(
                participants__user_id=other_user_id,
                participants__is_active=True,
            )
            .distinct()
        )

        room = rooms.first()

        if room:
            return Response({"exists": True, "room_id": room.id})

        return Response({"exists": False})
