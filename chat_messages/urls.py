from django.urls import path
from .views import MessageCreateView, MessageEditView, MessageListView

urlpatterns = [
    path("messages/", MessageCreateView.as_view(), name="messages-create"),
    path("messages/<int:room_id>/", MessageListView.as_view(), name="messages-list"),
    path("messages/<int:pk>/edit/", MessageEditView.as_view(), name="message-edit"),
]
