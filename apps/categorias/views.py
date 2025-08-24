# apps/categorias/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied

from .models import Categoria



class CategoriaPermission(permissions.BasePermission):
    """
    Permiso personalizado para la gestión de Categorias.
    - Superusuarios: Acceso total a todas las categorias.
    - Otros usuarios autenticados (CLIENTE, EMPLEADO): Solo lectura de categorias de SU propia empresa.
    """

    def has_permission(self, request, view):
        # 1. Verificar si el usuario está autenticado. Si no, denegar explícitamente.
        if not request.user or request.user.is_anonymous: # Usamos is_anonymous para mayor claridad
            raise PermissionDenied("Debe estar autenticado para acceder a las categorías.")

        # 2. Si es superusuario, siempre tiene permiso.
        if request.user.is_superuser:
            return True

        # 3. Verificar que el usuario autenticado tiene un rol válido .
        if not hasattr(request.user, 'role') or request.user.role is None:
            raise PermissionDenied("Su cuenta no tiene un rol  válido asignados.")

        user_role_name = request.user.role.name

        # 4. Lógica de permisos basada en el rol y empresa del usuario
        # Administradores de Empresa: Acceso total a categorías de SU propia empresa.
        if user_role_name == 'Administrador':
            return True

        # Clientes o Empleados: Solo lectura de categorías de SU propia empresa.
        if user_role_name in ['Cliente', 'Empleado'] and request.method in permissions.SAFE_METHODS:
            return True

        # Denegar cualquier otro caso.
        return False

    def has_object_permission(self, request, view, obj):
        # 1. Si es superusuario, siempre tiene permiso sobre el objeto.
        if request.user.is_superuser:
            return True



            # 3. Lógica de permisos sobre el objeto basado en el rol
            # Métodos seguros (GET): permitidos para Clientes, Empleados y Administradores de la misma empresa.
        if request.method in permissions.SAFE_METHODS:
            return True

            # Otros métodos (PUT/PATCH/DELETE): permitidos solo para Administradores de la misma empresa.
        if hasattr(request.user, 'role') and request.user.role is not None and request.user.role.name == 'Administrador':
            return True

        # Denegar cualquier otro caso.
        return False


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de Categorias. Proporciona acciones de listado, creación,
    recuperación, actualización y eliminación.
    """

    permission_classes = [CategoriaPermission]

    def get_queryset(self):
        # === INICIO DE LA CORRECCIÓN CRÍTICA PARA SWAGGER/AnonymousUser ===
        if getattr(self, 'swagger_fake_view', False):
            return Categoria.objects.none()
        # === FIN DE LA CORRECCIÓN ===

        user = self.request.user
        queryset = Categoria.objects.all()

        if user.is_superuser:
            return queryset.order_by('nombre')


        return Categoria.objects.none()

    def perform_create(self, serializer):
        # Al crear una categoría, asigna automáticamente la empresa del usuario autenticado
        user = self.request.user
        if not user.is_superuser:
            if not (hasattr(user, 'empresa') and user.empresa):
                raise PermissionDenied("No estás asociado a ninguna empresa para crear categorías.")
            serializer.save(empresa=user.empresa)
        else:
            serializer.save()