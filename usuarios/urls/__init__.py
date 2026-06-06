

from django.urls import path, include

urlpatterns = [
    path('', include('usuarios.urls.auth_urls')),
    path('', include('usuarios.urls.acudiente_urls')),
    path('', include('usuarios.urls.curso_urls')),
    path('', include('usuarios.urls.usuario_urls')),
    path('', include('usuarios.urls.tipo_documento_urls')),
    path('', include('usuarios.urls.estudiante_urls')),
    path('', include('usuarios.urls.perfil_urls')),
    path('', include('usuarios.urls.jornada_urls')),
    path('', include('usuarios.urls.eps_urls')),
    path('', include('usuarios.urls.metodo_Pago_urls')),
    path('', include('usuarios.urls.pagina_urls')),
    path('', include('usuarios.urls.tipo_documento_matricula_urls')),
    path('', include('usuarios.urls.documento_matricula_urls')),
    path('', include('usuarios.urls.matricula_urls')),
    path('', include('usuarios.urls.trazabilidad_urls')),
    path('', include('usuarios.urls.proceso_matricula_urls')),
    path('', include('usuarios.urls.seguimiento_matricula_urls')),
    path('', include('usuarios.urls.pago_urls')),
]

