from django.db import models
from apps.categorias.models import Categoria
class Servicio(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Servicio")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción del servicio")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    is_active = models.BooleanField(default=True)
    fecha_Creacion = models.DateTimeField(auto_now_add=True)


    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='servicios',
        verbose_name="Categoría"
    )



    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['nombre']
        unique_together = [['nombre']]

    def __str__(self):
        return f"{self.nombre} "


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

