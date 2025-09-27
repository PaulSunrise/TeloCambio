from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.db import models
from .models import Community, CommunityEmailRegistry, CustomUser
from .serializers import (
    CommunitySerializer, 
    CommunityEmailRegistrySerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer
)

# Permiso personalizado para admin y superadmin
class IsAdminOrSuperAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in ['admin', 'superadmin']

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_registration(request):
    """Verifica si un usuario puede registrarse"""
    community_code = request.data.get('community_code')
    email = request.data.get('email')
    
    print(f"🔍 BACKEND: Verificando código='{community_code}', email='{email}'")
    
    if not community_code or not email:
        print("❌ BACKEND: Faltan código o email")
        return Response(
            {'error': 'Código de comunidad y email son requeridos'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        community = Community.objects.get(community_code=community_code, is_active=True)
        print(f"✅ BACKEND: Comunidad encontrada - '{community.name}' (ID: {community.id})")
    except Community.DoesNotExist:
        print(f"❌ BACKEND: Comunidad NO encontrada con código '{community_code}'")
        return Response(
            {'error': 'Código de comunidad inválido o comunidad inactiva'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        email_registry = CommunityEmailRegistry.objects.get(
            community=community, 
            email=email,
            is_enabled=True,
            is_used=False
        )
        print(f"✅ BACKEND: Email AUTORIZADO - '{email}' (Habilitado: {email_registry.is_enabled}, Usado: {email_registry.is_used})")
        
        if community.community_type == 'condominium':
            tipo_comunidad = 'condominio'
        elif community.community_type == 'department':
            tipo_comunidad = 'departamento'
        else:
            tipo_comunidad = community.community_type
        
        return Response({
            'success': True,
            'community_name': community.name,
            'community_type': tipo_comunidad
        })
    except CommunityEmailRegistry.DoesNotExist:
        print(f"❌ BACKEND: Email NO autorizado - '{email}'")
        try:
            registry_exists = CommunityEmailRegistry.objects.get(community=community, email=email)
            print(f"🔍 BACKEND: Email existe pero - Habilitado: {registry_exists.is_enabled}, Usado: {registry_exists.is_used}")
        except CommunityEmailRegistry.DoesNotExist:
            print(f"🔍 BACKEND: Email no existe en el padrón")
        
        return Response(
            {'error': 'Correo no autorizado para registrarse en esta comunidad'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    """Registro de nuevo usuario"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Crear tokens JWT para el nuevo usuario
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'user_id': user.id,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """Login de usuario con JWT"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'error': 'Email y contraseña son requeridos'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar si el usuario existe primero
    try:
        user = CustomUser.objects.get(email=email)
        
        # Si el usuario existe pero está desactivado
        if not user.is_active:
            return Response(
                {'error': 'Tu cuenta ha sido desactivada. Por favor, contacta al administrador de tu comunidad.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Si el usuario existe y está activo, intentar autenticar
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            # Crear tokens JWT
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            
            return Response({
                'success': True,
                'message': 'Login exitoso',
                'user': user_data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            })
        else:
            # Las credenciales son incorrectas
            return Response(
                {'error': 'Credenciales inválidas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except CustomUser.DoesNotExist:
        # El usuario no existe
        return Response(
            {'error': 'Credenciales inválidas'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    """Refresh JWT token"""
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response(
            {'error': 'Refresh token es requerido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        return Response({
            'success': True,
            'access': access_token
        })
    except Exception as e:
        return Response(
            {'error': 'Token inválido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """Logout de usuario (JWT es stateless, solo devolver éxito)"""
    return Response({
        'success': True, 
        'message': 'Logout exitoso'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Obtener perfil del usuario actual"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminOrSuperAdmin])
def community_users_list(request):
    """
    Lista todos los usuarios de la comunidad del administrador
    Con soporte para búsqueda por nombre, apellido, email, teléfono
    Y NUEVOS FILTROS por estado (activo/inactivo)
    """
    try:
        user = request.user
        search_query = request.GET.get('search', '').strip()
        status_filter = request.GET.get('status', 'all')  # 'all', 'active', 'inactive'
        
        users = get_user_model().objects.all()
        
        if user.role == 'admin':
            # Admin solo ve usuarios RESIDENTES de su comunidad
            users = users.filter(community=user.community, role='resident')
        elif user.role == 'superadmin':
            # Superadmin ve todos los usuarios (puede gestionar admins también)
            users = users.all()
        else:
            return Response({
                'success': False,
                'error': 'No tienes permisos para acceder a esta función'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # ✅ NUEVO: Aplicar filtro por estado
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
        # 'all' no aplica filtro adicional
        
        # Aplicar filtro de búsqueda si existe
        if search_query:
            users = users.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(email__icontains=search_query) |
                models.Q(phone__icontains=search_query)
            )
        
        # ✅ NUEVO: Contadores para estadísticas
        total_users = users.count()
        active_users = users.filter(is_active=True).count()
        inactive_users = total_users - active_users
        
        users_data = []
        for user_obj in users:
            users_data.append({
                'id': user_obj.id,
                'email': user_obj.email,
                'first_name': user_obj.first_name,
                'last_name': user_obj.last_name,
                'phone': user_obj.phone,
                'role': user_obj.role,
                'is_active_user': user_obj.is_active,
                'registration_date': user_obj.date_joined,
                'community': user_obj.community.id if user_obj.community else None,
                'community_name': user_obj.community.name if user_obj.community else 'Sin comunidad'
            })
        
        return Response({
            'success': True,
            'users': users_data,
            'total': total_users,
            'active_count': active_users,
            'inactive_count': inactive_users,
            'search_query': search_query,
            'status_filter': status_filter
        })
        
    except Exception as e:
        print(f"❌ ERROR en community_users_list: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminOrSuperAdmin])
def toggle_user_status(request, user_id):
    """
    Activar/desactivar usuario (bloquear/desbloquear)
    """
    try:
        target_user = get_user_model().objects.get(id=user_id)
        current_user = request.user
        
        # Validación 1: Un usuario no puede desactivarse a sí mismo
        if target_user.id == current_user.id:
            return Response({
                'success': False,
                'error': 'No puedes desactivar tu propia cuenta'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validación 2: Admin solo puede gestionar residentes de su comunidad
        if current_user.role == 'admin':
            if target_user.community != current_user.community:
                return Response({
                    'success': False,
                    'error': 'No tienes permisos para modificar este usuario'
                }, status=status.HTTP_403_FORBIDDEN)
            if target_user.role != 'resident':
                return Response({
                    'success': False,
                    'error': 'Solo puedes gestionar usuarios residentes'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Validación 3: Solo superadmin puede gestionar otros admins/superadmins
        if target_user.role in ['admin', 'superadmin'] and current_user.role != 'superadmin':
            return Response({
                'success': False,
                'error': 'No puedes modificar administradores'
            }, status=status.HTTP_403_FORBIDDEN)
        
        target_user.is_active = not target_user.is_active
        target_user.save()
        
        return Response({
            'success': True,
            'message': f'Usuario {"activado" if target_user.is_active else "desactivado"} exitosamente',
            'is_active': target_user.is_active
        })
        
    except get_user_model().DoesNotExist:
        return Response({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommunityListAPIView(generics.ListAPIView):
    """Lista de comunidades (solo para superadmin)"""
    queryset = Community.objects.filter(is_active=True)
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'superadmin':
            return Community.objects.all()
        return Community.objects.none()

@api_view(['GET', 'POST'])
@permission_classes([IsAdminOrSuperAdmin])
def email_registry_list(request):
    """
    Lista y creación de registros de correo (solo admin de comunidad)
    CON NUEVOS FILTROS y BÚSQUEDA AVANZADA
    """
    try:
        user = request.user
        
        if request.method == 'GET':
            # Obtener lista de correos
            if user.role == 'admin':
                emails = CommunityEmailRegistry.objects.filter(community=user.community)
            elif user.role == 'superadmin':
                emails = CommunityEmailRegistry.objects.all()
            else:
                return Response({
                    'success': False,
                    'error': 'No tienes permisos'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # ✅ NUEVO: Aplicar filtro por estado (disponible/usado)
            status_filter = request.GET.get('status', 'all')  # 'all', 'available', 'used'
            if status_filter == 'available':
                emails = emails.filter(is_used=False)
            elif status_filter == 'used':
                emails = emails.filter(is_used=True)
            
            # ✅ NUEVO: Búsqueda avanzada con datos de usuario asociado
            search_query = request.GET.get('search', '').strip()
            if search_query:
                # Búsqueda en campos del correo + datos del usuario asociado (solo para correos usados)
                emails = emails.filter(
                    models.Q(email__icontains=search_query) |
                    models.Q(tower__icontains=search_query) |
                    models.Q(house_number__icontains=search_query) |
                    models.Q(address__icontains=search_query) |
                    # ✅ Búsqueda en usuarios asociados (solo para correos usados)
                    models.Q(
                        is_used=True,
                        customuser__first_name__icontains=search_query
                    ) |
                    models.Q(
                        is_used=True, 
                        customuser__last_name__icontains=search_query
                    ) |
                    models.Q(
                        is_used=True,
                        customuser__phone__icontains=search_query
                    )
                ).distinct()
            
            # ✅ NUEVO: Contadores para estadísticas
            total_emails = emails.count()
            available_emails = emails.filter(is_used=False).count()
            used_emails = total_emails - available_emails
            
            emails_data = []
            for email_reg in emails:
                email_data = {
                    'id': email_reg.id,
                    'email': email_reg.email,
                    'community': email_reg.community.id,
                    'community_name': email_reg.community.name,
                    'is_enabled': email_reg.is_enabled,
                    'is_used': email_reg.is_used,
                    'loaded_date': email_reg.loaded_date,
                    'loaded_by': email_reg.loaded_by,
                    'tower': email_reg.tower,
                    'house_number': email_reg.house_number,
                    'address': email_reg.address,
                    # ✅ NUEVO: Información del usuario asociado (solo si está usado)
                    'associated_user': None
                }
                
                # ✅ SOLO si el correo está USADO, buscar usuario asociado
                if email_reg.is_used:
                    try:
                        user_obj = CustomUser.objects.get(
                            email=email_reg.email, 
                            community=email_reg.community
                        )
                        email_data['associated_user'] = {
                            'id': user_obj.id,
                            'first_name': user_obj.first_name,
                            'last_name': user_obj.last_name,
                            'phone': user_obj.phone,
                            'is_active_user': user_obj.is_active_user
                        }
                    except CustomUser.DoesNotExist:
                        # Correo marcado como usado pero usuario no encontrado
                        email_data['associated_user'] = None
                
                emails_data.append(email_data)
            
            return Response({
                'success': True,
                'results': emails_data,
                'total': total_emails,
                'available_count': available_emails,
                'used_count': used_emails,
                'search_query': search_query,
                'status_filter': status_filter
            })
        
        elif request.method == 'POST':
            # Crear nuevo registro de correo (código existente se mantiene igual)
            email = request.data.get('email')
            
            if not email:
                return Response({
                    'success': False,
                    'error': 'El correo electrónico es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si el correo ya existe en la comunidad
            if user.role == 'admin':
                existing_email = CommunityEmailRegistry.objects.filter(
                    community=user.community, 
                    email=email
                ).first()
                
                if existing_email:
                    return Response({
                        'success': False,
                        'error': 'Este correo ya existe en el padrón de la comunidad'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # ✅ LÓGICA EXISTENTE: Verificar si ya existe un usuario con este email
                existing_user = None
                try:
                    existing_user = CustomUser.objects.get(
                        email=email, 
                        community=user.community
                    )
                except CustomUser.DoesNotExist:
                    existing_user = None
                
                # Si existe usuario, marcar correo como USADO y reactivar usuario
                if existing_user:
                    # Crear registro marcado como USADO
                    email_registry = CommunityEmailRegistry.objects.create(
                        community=user.community,
                        email=email,
                        is_enabled=True,
                        is_used=True,
                        loaded_by=user.email
                    )
                    
                    # Reactivar usuario si estaba desactivado
                    user_was_reactivated = False
                    if not existing_user.is_active:
                        existing_user.is_active = True
                        existing_user.save()
                        user_was_reactivated = True
                    
                    message = f'Correo agregado y marcado como USADO. '
                    if user_was_reactivated:
                        message += f'Usuario {existing_user.first_name} {existing_user.last_name} ha sido reactivado automáticamente.'
                    else:
                        message += f'El usuario {existing_user.first_name} {existing_user.last_name} ya estaba activo.'
                    
                    return Response({
                        'success': True,
                        'id': email_registry.id,
                        'message': message,
                        'user_reactivated': user_was_reactivated
                    }, status=status.HTTP_201_CREATED)
                else:
                    # Crear nuevo registro normal (sin usuario existente)
                    email_registry = CommunityEmailRegistry.objects.create(
                        community=user.community,
                        email=email,
                        is_enabled=True,
                        is_used=False,
                        loaded_by=user.email
                    )
                    
                    return Response({
                        'success': True,
                        'id': email_registry.id,
                        'message': 'Correo agregado exitosamente al padrón'
                    }, status=status.HTTP_201_CREATED)
            
            else:
                return Response({
                    'success': False,
                    'error': 'Función no implementada para superadmin'
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        print(f"❌ ERROR en email_registry_list: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminOrSuperAdmin])
def email_registry_detail(request, email_id):
    """
    Editar o eliminar un registro de correo específico
    """
    try:
        user = request.user
        
        # Obtener el registro de correo
        if user.role == 'admin':
            email_reg = CommunityEmailRegistry.objects.get(id=email_id, community=user.community)
        elif user.role == 'superadmin':
            email_reg = CommunityEmailRegistry.objects.get(id=email_id)
        else:
            return Response({
                'success': False,
                'error': 'No tienes permisos'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            # Editar registro de correo - SOLO si NO está usado
            if email_reg.is_used:
                return Response({
                    'success': False,
                    'error': 'No se puede editar un correo que ya ha sido usado para registro'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            email = request.data.get('email')
            is_enabled = request.data.get('is_enabled')
            
            # Validaciones
            if email and email != email_reg.email:
                # Verificar si el nuevo email ya existe en la comunidad
                existing_email = CommunityEmailRegistry.objects.filter(
                    community=email_reg.community, 
                    email=email
                ).exclude(id=email_id).first()
                
                if existing_email:
                    return Response({
                        'success': False,
                        'error': 'Este correo ya existe en el padrón de la comunidad'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                email_reg.email = email
            
            if is_enabled is not None:
                email_reg.is_enabled = is_enabled
            
            email_reg.save()
            
            return Response({
                'success': True,
                'message': 'Correo actualizado exitosamente',
                'email': {
                    'id': email_reg.id,
                    'email': email_reg.email,
                    'is_enabled': email_reg.is_enabled,
                    'is_used': email_reg.is_used,
                    'loaded_date': email_reg.loaded_date
                }
            })
        
        elif request.method == 'DELETE':
            # ✅ SISTEMA AUTOMÁTICO: Desactivar usuario si el correo está usado
            warning_message = ""
            
            # Si el correo está usado, desactivar al usuario asociado
            if email_reg.is_used:
                try:
                    user_obj = CustomUser.objects.get(email=email_reg.email, community=email_reg.community)
                    user_obj.is_active = False  # Desactivar usuario
                    user_obj.save()
                    warning_message = " ✅ El correo fue usado - Usuario asociado ha sido DESACTIVADO automáticamente"
                except CustomUser.DoesNotExist:
                    warning_message = " ⚠️ Correo marcado como usado pero usuario no encontrado"
            else:
                warning_message = " ℹ️ Correo no estaba usado - Solo eliminación del padrón"
            
            email_reg.delete()
            
            return Response({
                'success': True,
                'message': f'Correo eliminado exitosamente del padrón.{warning_message}'
            })
    
    except CommunityEmailRegistry.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Registro de correo no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"❌ ERROR en email_registry_detail: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Obtener información del usuario actualmente autenticado via JWT
    """
    user = request.user
    user_data = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'community': user.community.id if user.community else None,
        'community_name': user.community.name if user.community else None,
        'is_active_user': user.is_active,
        'registration_date': user.date_joined.isoformat() if user.date_joined else None,
    }
    return Response({'success': True, 'user': user_data})

