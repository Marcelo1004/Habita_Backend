# erp/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from apps.rbac.views import PermissionViewSet, RoleViewSet
from apps.usuarios.views import UserViewSet
from apps.categorias.views import CategoriaViewSet
from apps.suscripciones.views import SuscripcionViewSet
from apps.servicios.views import ServicioViewSet


router = DefaultRouter()

router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'users', UserViewSet, basename='user')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'suscripciones', SuscripcionViewSet, basename='suscripcion')
router.register(r'servicios', ServicioViewSet, basename='servicio')


schema_view = get_schema_view(
    openapi.Info(
        title="Habita",
        default_version='v1',
        description="Documentación de la API para el sistema de Gestión  Habita.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="alcoba80@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Agrupamos todas las URLs de la API bajo un solo 'api/'
    path('api/', include([
        # Rutas generadas por el router (API administrativa)
        path('', include(router.urls)), # Esto incluirá ahora /api/pagos/

        # Rutas específicas de usuarios (si no están en el router)
        path('usuarios/', include('apps.usuarios.urls')),

        # Rutas de dashboard y reportes
        path('dashboard/', include('apps.dashboard.urls')),
        # Asumiendo que reports está en apps.reports.urls

        # --- RUTAS PÚBLICAS DEL MARKETPLACE ---

        path('public-services/', include('apps.servicios.urls')),

    ])),

    # Rutas para Swagger/Redoc (pueden ir fuera del 'api/' si lo prefieres, o dentro)
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
