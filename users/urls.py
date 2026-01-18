from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("search", UserViewSet, basename="user-search")

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
]

urlpatterns += router.urls
