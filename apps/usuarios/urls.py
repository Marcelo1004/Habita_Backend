# apps/usuarios/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    UserProfileView,
)

# Ya no hay un DefaultRouter local aquí.
urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('registro/', RegisterView.as_view(), name='user_register'),
    path('perfil/', UserProfileView.as_view(), name='user_profile'),
]