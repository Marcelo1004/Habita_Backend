# dashboard/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, F, ExpressionWrapper, DecimalField, Q
from django.db.models.functions import TruncMonth
from rest_framework.permissions import IsAuthenticated, BasePermission
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models  # Asegúrate de importar models si usas F, Q, etc.

# Importa tus modelos. ¡ASEGÚRATE DE QUE ESTAS RUTAS SEAN CORRECTAS!
from apps.usuarios.models import CustomUser

from apps.categorias.models import Categoria
from apps.servicios.models import Servicio
from apps.suscripciones.models import Suscripcion




# Asegúrate de que este serializer exista y esté definido correctamente
from .serializers import DashboardERPSerializer


class IsWorkerUser(BasePermission):
    """
    Permiso personalizado para permitir acceso a SuperUsuarios, Administrativos y Empleados.
    Los clientes no tienen acceso al dashboard.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.role in ['ADMINISTRATIVO', 'EMPLEADO']


class DashboardERPView(APIView):
    permission_classes = [IsWorkerUser]

    def get(self, request):
        user = request.user

        dashboard_data = {
            'total_usuarios': 0,
            'total_propiedades': 0,
            'total_servicios': 0,
            'total_categorias': 0,
            'total_suscripciones': 0,
            'distribucion_suscripciones': [],
            'monthly_sales': [],
            'top_service': [],
            'category_distribution': [],
            'recent_activities': [],  # Aseguramos que esté aquí desde el inicio

        }

        try:
            empresa_filter = Q()


            # Aplicamos el filtro a todos los QuerySets
            user_qs = CustomUser.objects.filter()
            categoria_qs = Categoria.objects.filter()
            servicio_qs = Servicio.objects.filter()





            # -----------------------------------------------------------
            # CÁLCULO DE MÉTRICAS
            # -----------------------------------------------------------

            # Métricas Core
            dashboard_data['total_usuarios'] = user_qs.count()
            dashboard_data['total_suscripciones'] = Suscripcion.objects.count()
            dashboard_data['total_categorias'] = categoria_qs.count()
            dashboard_data['total_productos'] = servicio_qs.count()




        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error en DashboardERPView: {str(e)}")
            return Response(
                {"error": f"Ha ocurrido un error al obtener las estadísticas del dashboard. Detalles: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )