# Create your views here.
from rest_framework import generics
from .serializers import RegisterSerializer
from .models import User

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from .serializers import UserListSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []


class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["username", "email"]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)
