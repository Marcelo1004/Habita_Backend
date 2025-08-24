from django.contrib import admin
from .models import Servicio

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    """
    Configuración para la visualización del modelo Producto en el panel de administración.
    """
    list_display = ('nombre', 'precio', 'categoria','imagen_tag')

    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('imagen_tag',) # Para mostrar la imagen en el admin

    # Método para mostrar la imagen en la lista del admin
    def imagen_tag(self, obj):
        if obj.imagen:
            from django.utils.html import mark_safe
            return mark_safe(f'<img src="{obj.imagen.url}" width="50" height="50" />')
        return "No Image"
    imagen_tag.short_description = 'Imagen'
