from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.db import transaction
from .models import CustomUser as User






from apps.rbac.models import Role, Permission
from apps.rbac.serializers import RoleSerializer  # Importa RoleSerializer para anidar



# Serializer para el token JWT personalizado
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        serializer = UserProfileSerializer(user)
        data['user'] = serializer.data
        return data



class UserProfileSerializer(serializers.ModelSerializer):

    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'telefono', 'ci', 'direccion',

            'is_active', 'is_staff', 'is_superuser',
            'date_joined',
            'last_login'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'date_joined', 'last_login',
            'is_active', 'is_staff', 'is_superuser', 'role'
        ]


# Serializer para el registro de usuarios (creación)
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    # 'role' acepta un ID de Role para escritura. El queryset asegura que solo se puedan asignar roles existentes.
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), required=False, allow_null=True
    )


    suscripcion_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True,
        help_text="ID de suscripción para la nueva empresa (para SuperUsuarios)."
    )

    class Meta:
        model = User  # Esto ahora apuntará correctamente a la clase CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 'role',
            'telefono', 'ci', 'direccion',
            'password', 'password2',
            'suscripcion_id'
        ]
        read_only_fields = [
            'id', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'ci': {'required': True},
            'telefono': {'required': False, 'allow_null': True},
            'direccion': {'required': False, 'allow_null': True},

        }

    def validate(self, attrs):
        # 1. Validar contraseñas
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})

        # Obtener el rol. Si viene como ID, PrimaryKeyRelatedField ya lo convierte a instancia en attrs.
        user_role_instance = attrs.get('role')

        # Si no se proporciona rol, intenta asignar el rol 'Cliente' por defecto
        if user_role_instance is None:
            try:
                default_client_role = Role.objects.get(name='Cliente')
                attrs['role'] = default_client_role
                user_role_instance = default_client_role
            except Role.DoesNotExist:
                raise serializers.ValidationError(
                    {"role": "El rol 'Cliente' por defecto no existe. Por favor, créalo en el administrador."})


        suscripcion_id = attrs.get('suscripcion_id')



        # Lógica de validación para ADMINISTRATIVOS o EMPLEADOS que crean usuarios
        if not self.context['request'].user.is_superuser:
            if user_role_instance.name != 'Cliente':
                request_user = self.context['request'].user






    def create(self, validated_data):
        with transaction.atomic():
            validated_data.pop('password2')


            suscripcion_id = validated_data.pop('suscripcion_id', None)

            role_instance = validated_data.pop('role', None)

            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                role=role_instance,  # Asigna la instancia del rol directamente
                telefono=validated_data.get('telefono'),
                ci=validated_data.get('ci'),
                direccion=validated_data.get('direccion'),
            )
            user.set_password(validated_data['password'])




            user.save()
        return user




# Serializer para la actualización de usuarios por parte de un administrador
class AdminUserUpdateSerializer(serializers.ModelSerializer):
    # 'role' acepta un ID de Role para escritura
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), required=False, allow_null=True
    )

    # Campo opcional para cambio de contraseña
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'telefono', 'ci', 'direccion', 'is_active', 'is_staff', 'is_superuser',
            'date_joined',
            'last_login',
            'password',
            'password2',
        ]
        read_only_fields = [
            'id', 'username', 'email', 'date_joined', 'last_login',
        ]

    def validate(self, attrs):
        current_user = self.instance  # El usuario que se está actualizando
        request_user = self.context['request'].user  # El usuario que realiza la solicitud

        # Validar contraseñas si se proporcionan
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password or password2:
            if password != password2:
                raise serializers.ValidationError({"password": "Las nuevas contraseñas no coinciden."})
            if not password:
                raise serializers.ValidationError({"password": "Debe proporcionar una nueva contraseña."})
            attrs.pop('password2', None)

        # Obtener el nuevo rol. Si no se proporciona en attrs, usar el rol actual del usuario.
        new_role_instance = attrs.get('role', current_user.role)

        # Validar que `new_role_instance` no sea `None` si `role` fue proporcionado
        if attrs.get('role') is not None and new_role_instance is None:
            raise serializers.ValidationError({"role": "El ID de rol proporcionado no es válido."})

        # Validar permisos de asignación de flags de usuario para no-SuperUsuarios
        if not request_user.is_superuser:
            # Un administrador de empresa (o cualquier otro rol) NO puede cambiar el rol de Super Usuario
            if new_role_instance and new_role_instance.name == 'Super Usuario' and new_role_instance != current_user.role:
                raise serializers.ValidationError(
                    {"role": "Solo un Super Usuario puede asignar el rol 'Super Usuario'."})

            # Un administrador NO puede desasignar el rol de Super Usuario
            if current_user.role and current_user.role.name == 'Super Usuario' and (
                    not new_role_instance or new_role_instance.name != 'Super Usuario'
            ):
                raise serializers.ValidationError({
                    "role": "Solo un Super Usuario puede modificar o eliminar el rol 'Super Usuario' de otro usuario."})

            # Adicionalmente, si el request_user no es superuser, no pueden cambiar 'is_active', 'is_staff', 'is_superuser'
            if 'is_active' in attrs and attrs['is_active'] != current_user.is_active:
                raise serializers.ValidationError(
                    {"is_active": "Solo un Super Usuario puede cambiar el estado de actividad."})
            if 'is_staff' in attrs and attrs['is_staff'] != current_user.is_staff:
                raise serializers.ValidationError(
                    {"is_staff": "Solo un Super Usuario puede cambiar el estado de staff."})
            if 'is_superuser' in attrs and attrs['is_superuser'] != current_user.is_superuser:
                raise serializers.ValidationError(
                    {"is_superuser": "Solo un Super Usuario puede cambiar el estado de superusuario."})

        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance