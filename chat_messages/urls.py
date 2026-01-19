from django.urls import path
from .views import MessageCreateView, MessageListView

urlpatterns = [
    path("messages/", MessageCreateView.as_view(), name="messages-create"),
    path("messages/<int:room_id>/", MessageListView.as_view(), name="messages-list"),
]
