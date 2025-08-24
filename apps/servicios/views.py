from rest_framework import viewsets, permissions, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework import filters
import django_filters.rest_framework
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Servicio
from .serializers import ServicioSerializer, ServicioListSerializer
from .filters import ServicioFilter


class ServicioPermission(permissions.BasePermission):



    def has_permission(self, request, view):
        if not request.user or request.user.is_anonymous:
            raise PermissionDenied("Debe estar autenticado para acceder a los servicios.")

        if request.user.is_superuser:
            return True

        if not hasattr(request.user, 'role') or request.user.role is None:
            raise PermissionDenied("Su cuenta no tiene un rol  válido asignado.")

        user_role_name = request.user.role.name

        if user_role_name == 'Administrador':
            return True

        if user_role_name in ['Cliente', 'Empleado'] and request.method in permissions.SAFE_METHODS:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.is_authenticated:

            if request.method in permissions.SAFE_METHODS:
                return True

            if hasattr(request.user,
                       'role') and request.user.role is not None and request.user.role.name == 'Administrador':
                return True

        return False


class ServicioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de Servicios (parte administrativa).
    Proporciona acciones de listado, creación, recuperación, actualización y eliminación,
    con soporte para filtrado y búsqueda.
    """
    serializer_class = ServicioSerializer
    permission_classes = [ServicioPermission]

    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = ServicioFilter
    search_fields = [
        'nombre',
        'precio',
        'categoria__nombre',

    ]

    queryset = Servicio.objects.all()

    # --- Consolidación del get_queryset ---
    def get_queryset(self):
        print("\n--- DEBUG: get_queryset de ServicioViewSet llamado ---")

        if getattr(self, 'swagger_fake_view', False):
            print("--- DEBUG: Modo Swagger_fake_view activado, retornando queryset vacío. ---")
            return Servicio.objects.none()

        user = self.request.user
        if user.is_superuser:
            # Superusuario puede ver todos los servicios (activos o inactivos)
            return Servicio.objects.all().order_by('nombre')
        elif user.is_authenticated:
            # Usuarios autenticados :
            # Solo pueden ver y operar con Servicios y que estén activos
            return Servicio.objects.filter( is_active=True).order_by('nombre')

        # Si el usuario no es superusuario, no está autenticado, o no tiene empresa asignada,
        # no debe ver ningún producto en el listado del ViewSet administrativo.
        return Servicio.objects.none()

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()
        print(f"\n--- DEBUG: ServViewSet está usando el serializer: {serializer_class.__name__} ---")
        return serializer_class




class ServicioListView(generics.ListAPIView):

    serializer_class = ServicioListSerializer
    permission_classes = []

    def get_queryset(self):
        return Servicio.objects.filter( is_active=True).order_by('nombre')


class ServicioDetailView(generics.RetrieveAPIView):


    serializer_class = ServicioSerializer
    lookup_field = 'pk'
    permission_classes = []

    def get_queryset(self):
        return Servicio.objects.filter(is_active=True)


