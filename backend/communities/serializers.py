from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Community, CommunityEmailRegistry, CustomUser

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'

class CommunityEmailRegistrySerializer(serializers.ModelSerializer):
    community_name = serializers.CharField(source='community.name', read_only=True)
    
    class Meta:
        model = CommunityEmailRegistry
        fields = '__all__'

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)  # CAMBIADO: password_confirmation → password2
    community_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 
                 'phone', 'community_code', 'tower', 'house_number', 'address')
        extra_kwargs = {
            'phone': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True},
            'tower': {'required': False, 'allow_blank': True},
            'house_number': {'required': False, 'allow_blank': True},
        }
    
    def validate(self, data):
        # CAMBIADO: Validar password2 en lugar de password_confirmation
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data
    
    def create(self, validated_data):
        # CAMBIADO: Remover password2 en lugar de password_confirmation
        validated_data.pop('password2')
        community_code = validated_data.pop('community_code')
        
        try:
            community = Community.objects.get(community_code=community_code, is_active=True)
        except Community.DoesNotExist:
            raise serializers.ValidationError("Código de comunidad inválido")
        
        # Verificar si el correo está en el padrón y habilitado
        try:
            email_registry = CommunityEmailRegistry.objects.get(
                community=community, 
                email=validated_data['email'],
                is_enabled=True,
                is_used=False
            )
        except CommunityEmailRegistry.DoesNotExist:
            raise serializers.ValidationError("Correo no autorizado para registrarse en esta comunidad")
        
        # Asegurar que los campos opcionales tengan valores por defecto si están vacíos
        if 'phone' not in validated_data or validated_data['phone'] is None:
            validated_data['phone'] = ""
        if 'address' not in validated_data or validated_data['address'] is None:
            validated_data['address'] = ""
        if 'tower' not in validated_data or validated_data['tower'] is None:
            validated_data['tower'] = ""
        if 'house_number' not in validated_data or validated_data['house_number'] is None:
            validated_data['house_number'] = ""
        
        user = CustomUser.objects.create_user(
            community=community,
            **validated_data
        )
        
        # Marcar el correo como usado
        email_registry.is_used = True
        email_registry.save()
        
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_active_user:
                    raise serializers.ValidationError("Usuario desactivado")
                data['user'] = user
            else:
                raise serializers.ValidationError("Credenciales inválidas")
        else:
            raise serializers.ValidationError("Email y contraseña son requeridos")
        
        return data

class UserSerializer(serializers.ModelSerializer):
    community_name = serializers.CharField(source='community.name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'community', 
                 'community_name', 'role', 'tower', 'house_number', 'address', 
                 'is_active_user', 'registration_date')