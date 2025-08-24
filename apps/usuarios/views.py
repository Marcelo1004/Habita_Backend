# apps/usuarios/views.py

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework import filters
import django_filters.rest_framework
from rest_framework import viewsets

# Importa tus serializers
from .serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    AdminUserUpdateSerializer,
    CustomTokenObtainPairSerializer
)

# Importa tu modelo CustomUser
from .models import CustomUser

# Importa tu permiso centralizado
from erp.permissions import IsAdminOrSuperUser

from rest_framework_simplejwt.views import TokenObtainPairView


# --- Vistas ---

# 1. Autenticación Personalizada con JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# 2. Registro de Nuevo Usuario
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer


# 3. Perfil de Usuario (para que el propio usuario vea/edite su información)
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=False, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(UserProfileSerializer(user, context={'request': request}).data)

    def patch(self, request):
        user = request.user
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(UserProfileSerializer(user, context={'request': request}).data)


# 4. Gestión de Usuarios por Administrador (ModelViewSet)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de usuarios por parte de SuperUsuarios.
    Proporciona operaciones de listado, creación, detalle, actualización y eliminación.
    """
    queryset = CustomUser.objects.all()
    permission_classes = [IsAdminOrSuperUser]

    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email', 'ci', 'telefono']
    filterset_fields = {
        'role__name': ['exact'],
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CustomUser.objects.none()

        user = self.request.user
        queryset = super().get_queryset()

        # Solo los superusuarios pueden ver todos los usuarios
        if user.is_superuser:
            return queryset.order_by('username')
        else:
            # Los demás usuarios (admin, empleado, etc.) no pueden listar otros usuarios
            return CustomUser.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        elif self.action in ['update', 'partial_update']:
            return AdminUserUpdateSerializer
        return UserProfileSerializer

    def perform_create(self, serializer):
        request_user = self.request.user

        if request_user.is_superuser:
            serializer.save()
        else:
            # Nadie más que un superusuario puede crear usuarios en este endpoint
            raise PermissionDenied("Solo un Super Usuario puede crear usuarios.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.is_superuser:
            if not request.user.is_superuser:
                raise PermissionDenied("No se puede eliminar a un Super Usuario sin ser Super Usuario.")
            if request.user.id == instance.id:
                raise PermissionDenied("Un Super Usuario no puede eliminar su propia cuenta a través de esta API.")

        if request.user == instance:
            raise PermissionDenied("No puedes eliminar tu propia cuenta a través de esta API.")

        # Eliminada toda la lógica de validación por empresa

        username = instance.username
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Usuario {username} eliminado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )