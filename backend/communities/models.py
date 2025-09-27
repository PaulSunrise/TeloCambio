from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email debe ser proporcionado')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'superadmin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Community(models.Model):
    COMMUNITY_TYPES = [
        ('department', 'Departamento'),
        ('condominium', 'Condominio'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre de la comunidad")
    community_type = models.CharField(max_length=20, choices=COMMUNITY_TYPES, verbose_name="Tipo de comunidad")
    address = models.TextField(verbose_name="Dirección")
    community_code = models.CharField(max_length=50, unique=True, verbose_name="Código de comunidad")
    admin_contact = models.EmailField(verbose_name="Contacto del administrador")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    
    class Meta:
        verbose_name = "Comunidad"
        verbose_name_plural = "Comunidades"
    
    def __str__(self):
        return f"{self.name} ({self.community_code})"

class CommunityEmailRegistry(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, verbose_name="Comunidad")
    email = models.EmailField(verbose_name="Correo electrónico")
    tower = models.CharField(max_length=100, blank=True, null=True, verbose_name="Torre/Edificio")
    house_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de vivienda")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    is_enabled = models.BooleanField(default=True, verbose_name="Habilitado")
    is_used = models.BooleanField(default=False, verbose_name="Usado")
    loaded_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de carga")
    loaded_by = models.EmailField(verbose_name="Cargado por", blank=True, null=True)
    
    class Meta:
        verbose_name = "Registro de correo"
        verbose_name_plural = "Registro de correos"
        unique_together = ['community', 'email']
    
    def __str__(self):
        return f"{self.email} - {self.community.name}"

class CustomUser(AbstractUser):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, verbose_name="Comunidad", null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    
    # Campos para departamento
    tower = models.CharField(max_length=100, blank=True, null=True, verbose_name="Torre/Edificio")
    house_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de vivienda")
    
    # Campos para condominio
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    
    ROLE_CHOICES = [
        ('resident', 'Residente'),
        ('admin', 'Administrador'),
        ('superadmin', 'Super Administrador'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident', verbose_name="Rol")
    is_active_user = models.BooleanField(default=True, verbose_name="Usuario activo")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    
    # Sobrescribir el campo username para usar email como identificador principal
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        unique_together = ['community', 'email']
    
    def __str__(self):
        community_name = self.community.name if self.community else "Sin comunidad"
        return f"{self.email} - {community_name}"