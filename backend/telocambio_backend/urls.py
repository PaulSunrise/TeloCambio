from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'message': 'Bienvenido a TeLoCambio API',
        'endpoints': {
            'admin': '/admin/',
            'api_auth': '/api/auth/',
            'api_communities': '/api/communities/'
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('communities.urls')),
]