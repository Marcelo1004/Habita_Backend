from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")



    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre'] # Ordenar por nombre por defecto
        unique_together = [['nombre', ]]

    def __str__(self):
        return f"{self.nombre} "

