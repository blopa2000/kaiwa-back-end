from rest_framework import generics, permissions, status
from .models import Room, RoomParticipant
from .serializers import RoomSerializer


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
