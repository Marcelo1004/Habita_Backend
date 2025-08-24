from rest_framework import serializers
from .models import Servicio
from apps.categorias.serializers import CategoriaSerializer

class ServicioSerializer(serializers.ModelSerializer):
    categoria_detail = CategoriaSerializer(source='categoria', read_only=True)

    imagen = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Servicio
        fields = [
            'id', 'nombre', 'descripcion', 'precio',
            'categoria', 'categoria_detail',
            'is_active','fecha_Creacion'

        ]
        extra_kwargs = {
            'categoria': {'write_only': True, 'required': False},
        }

class ServicioListSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)


    class Meta:
        model = Servicio
        fields = [
            'id', 'nombre', 'descripcion', 'precio',
            'categoria_nombre',
            'is_active','fecha_Creacion'
        ]