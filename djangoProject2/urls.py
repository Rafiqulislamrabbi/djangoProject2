from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserRegistrationAPIView, UserLoginAPIView, UserProfileViewSet, WalletViewSet

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'wallet', WalletViewSet, basename='wallet')

urlpatterns = [
    path('api/auth/register/', UserRegistrationAPIView.as_view(), name='register'),
    path('api/auth/login/', UserLoginAPIView.as_view(), name='login'),
    path('api/', include(router.urls)),
]
