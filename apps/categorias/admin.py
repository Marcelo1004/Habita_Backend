from django.contrib import admin
from .models import Categoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Configuración para la visualización del modelo Categoria en el panel de administración.
    """
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('nombre',)