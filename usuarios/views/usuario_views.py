from rest_framework import viewsets, status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import os

from ..models import Usuario, Foto_Usuario
from ..serializers import UsuarioListSerializer, UsuarioUpdateSerializer # CORREGIDO
from backend.permissions import PermisoPorPerfil
  

# ----------------------------------------------------------
# HELPERS DE PERMISOS - evita repetir la lógica en cada método
# ----------------------------------------------------------

def es_admin(user):
    return user.perfil.nombre_perfil == 'Administrador'

def es_propio_usuario(user, id):
    return user.id == id


# ----------------------------------------------------------
# CRUD PRINCIPAL
# ----------------------------------------------------------

class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]

    def get_permissions(self):
        # El registro es público, el resto requiere autenticación
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        qs = Usuario.objects.select_related('perfil', 'tipo_documento')
        if es_admin(self.request.user):
            return qs.all()
        # Cualquier otro perfil solo se ve a sí mismo
        return qs.filter(id=self.request.user.id)

    def get_serializer_class(self):
        # CORREGIDO: Usar UsuarioUpdateSerializer en lugar de Login
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioUpdateSerializer 
        return UsuarioListSerializer

    def retrieve(self, request, *args, **kwargs):
        # No administrador solo puede ver su propio detalle
        instance = self.get_object()
        if not es_admin(request.user) and not es_propio_usuario(request.user, instance.id):
            return Response(
                {'error': 'No puedes ver datos de otro usuario'},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(UsuarioListSerializer(instance).data)

    def update(self, request, *args, **kwargs):
        # No administrador solo puede editarse a sí mismo
        instance = self.get_object()
        if not es_admin(request.user) and not es_propio_usuario(request.user, instance.id):
            return Response(
                {'error': 'No puedes editar datos de otro usuario'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Solo el administrador puede eliminar
        if not es_admin(request.user):
            return Response(
                {'error': 'Solo el Administrador puede eliminar usuarios'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()

        # Un administrador no puede eliminarse a sí mismo
        if es_propio_usuario(request.user, instance.id):
            return Response(
                {'error': 'No puedes eliminarte a ti mismo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Borra fotos físicas antes de eliminar
        for foto in instance.fotos.all():
            if foto.archivo and os.path.isfile(foto.archivo.path):
                os.remove(foto.archivo.path)
            foto.delete()

        instance.delete()
        return Response({'mensaje': 'Usuario eliminado correctamente'}, status=status.HTTP_200_OK)


# ----------------------------------------------------------
# FOTOS - Endpoint dedicado
# ----------------------------------------------------------

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated, PermisoPorPerfil])
def fotos_usuario(request, id):
    """
    GET  → lista las fotos del usuario
    POST → sube hasta 4 fotos
    """
    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    # Solo admin o el propio usuario pueden ver/subir fotos
    if not es_admin(request.user) and not es_propio_usuario(request.user, id):
        return Response({'error': 'No tienes permiso para acceder a estas fotos'}, status=status.HTTP_403_FORBIDDEN)

    # ── GET ──────────────────────────────────────────────
    if request.method == 'GET':
        # CORREGIDO: Se quitó el order_by y el campo subida_el
        fotos = usuario.fotos.all()
        data  = [
            {
                'id'  : foto.id,
                'url' : request.build_absolute_uri(foto.archivo.url),
            }
            for foto in fotos
        ]
        return Response(data, status=status.HTTP_200_OK)

    # ── POST ─────────────────────────────────────────────
    if request.method == 'POST':
        EXTENSIONES_PERMITIDAS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        fotos_guardadas = []
        errores         = []

        for i in range(4):
            archivo = request.FILES.get(f'foto_{i}')
            if not archivo:
                continue

            ext = os.path.splitext(archivo.name)[1].lower()
            if ext not in EXTENSIONES_PERMITIDAS:
                errores.append(f'foto_{i}: extensión {ext} no permitida')
                continue

            foto = Foto_Usuario(usuario=usuario)
            foto.archivo.save(archivo.name, archivo, save=True)
            fotos_guardadas.append({
                'id' : foto.id,
                'url': request.build_absolute_uri(foto.archivo.url),
            })

        if not fotos_guardadas and errores:
            return Response({'errores': errores}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'usuario': id,
            'fotos'  : fotos_guardadas,
            **(({'advertencias': errores}) if errores else {}),
        }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, PermisoPorPerfil])
def eliminar_foto_usuario(request, id, foto_id):
    """DELETE → elimina una foto específica del usuario."""

    if not es_admin(request.user) and not es_propio_usuario(request.user, id):
        return Response({'error': 'No tienes permiso para eliminar esta foto'}, status=status.HTTP_403_FORBIDDEN)

    try:
        foto = Foto_Usuario.objects.get(id=foto_id, usuario_id=id)
    except Foto_Usuario.DoesNotExist:
        return Response({'error': 'Foto no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    if foto.archivo and os.path.isfile(foto.archivo.path):
        os.remove(foto.archivo.path)

    foto.delete()
    return Response({'mensaje': 'Foto eliminada correctamente'}, status=status.HTTP_200_OK)