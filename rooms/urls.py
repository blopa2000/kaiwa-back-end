from django.urls import path
from .views import RoomListView, RoomDeleteView
from chat_messages.views import MessageCreateView

urlpatterns = [
    path("rooms/", RoomListView.as_view(), name="rooms-list"),
    path("rooms/<int:pk>/delete/", RoomDeleteView.as_view(), name="rooms-delete"),
    path("messages/", MessageCreateView.as_view(), name="messages-create"),
]
