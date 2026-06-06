from rest_framework.permissions import BasePermission

ACCION_PERMISO = {
    'list':           'view_perfil',
    'retrieve':       'view_perfil',
    'create':         'insert_perfil',
    'update':         'update_perfil',
    'partial_update': 'update_perfil',
    'destroy':        'delete_perfil',
    # APIView métodos HTTP (para tus vistas anteriores)
    'GET':    'view_perfil',
    'POST':   'insert_perfil',
    'PUT':    'update_perfil',
    'PATCH':  'update_perfil',
    'DELETE': 'delete_perfil',
}

class PermisoPorPerfil(BasePermission):
    def has_permission(self, request, view):
        try:
            perfil = request.user.perfil
            action = getattr(view, 'action', None)
            accion = ACCION_PERMISO.get(action) or ACCION_PERMISO.get(request.method)
            if accion is None:
                return False
            return getattr(perfil, accion, False)
        except Exception as e:
            return False