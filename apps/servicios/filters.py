import django_filters
from .models import Servicio

class ServicioFilter(django_filters.FilterSet):
    """
    Filtros para el modelo Producto.
    Permite filtrar por nombre (búsqueda parcial insensible a mayúsculas/minúsculas)
    y por categoría (ID exacto).
    """
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    categoria = django_filters.NumberFilter(field_name='categoria')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')


    class Meta:
        model = Servicio
        fields = ['nombre', 'categoria','precio']
