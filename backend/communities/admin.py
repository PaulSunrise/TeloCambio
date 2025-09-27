from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Community, CommunityEmailRegistry, CustomUser

# Configuración personalizada para CustomUser en el admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'role', 'community', 'is_active', 'date_joined')
    list_filter = ('role', 'community', 'is_active', 'date_joined')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permisos', {'fields': ('role', 'community', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'community')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined')  # Campos de solo lectura

# Configuración para Community
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'community_type', 'community_code', 'is_active')
    list_filter = ('community_type', 'is_active')
    search_fields = ('name', 'community_code')

# Configuración para CommunityEmailRegistry
class CommunityEmailRegistryAdmin(admin.ModelAdmin):
    list_display = ('email', 'community', 'is_enabled', 'is_used', 'loaded_date')
    list_filter = ('community', 'is_enabled', 'is_used')
    search_fields = ('email', 'community__name')

# Registrar modelos en el admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityEmailRegistry, CommunityEmailRegistryAdmin)