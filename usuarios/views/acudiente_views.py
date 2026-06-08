from rest_framework import viewsets, status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from backend.permissions import PermisoPorPerfil
from ..models import Acudiente, Foto_Acudiente
from ..serializers import AcudienteUpdateSerializer, AcudienteListSerializer
from ..utils import registrar_auditoria  # Importación de la utilidad
import os

# ----------------------------------------------------------
# CRUD PRINCIPAL - Acudientes
# ----------------------------------------------------------

class AcudienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]

    def get_queryset(self):
        queryset = Acudiente.objects.select_related('tipo_documento', 'usuario').prefetch_related('fotos')

        if self.request.user.perfil.nombre_perfil != 'Administrador':
            return queryset.filter(usuario=self.request.user)
        
        busqueda = self.request.query_params.get('buscar')
        if busqueda:
            queryset = queryset.filter(
                Q(numero_documento__icontains=busqueda)|
                Q(nombre_completo__icontains=busqueda)|
                Q(email__icontains=busqueda)
            )

        parentescos = self.request.query_params.get('parentesco')
        tipo_doc = self.request.query_params.get('tipo_documento')

        if tipo_doc is not None:
            queryset = queryset.filter(tipo_documento__sigla__icontains=tipo_doc)
        if parentescos:
            queryset = queryset.filter(parentesco__icontains=parentescos)

        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AcudienteUpdateSerializer
        return AcudienteListSerializer

    # --- TRAZABILIDAD: CREAR ---
    def perform_create(self, serializer):
        instance = serializer.save(usuario=self.request.user)
        
        # Guardar la foto del acudiente si se envió una
        foto_archivo = self.request.FILES.get('foto_acudiente')
        if foto_archivo:
            foto_obj = Foto_Acudiente(acudiente=instance)
            foto_obj.archivo.save(foto_archivo.name, foto_archivo, save=True)

        registrar_auditoria(
            self.request, 
            "CREACIÓN", 
            f"Se registró el acudiente {instance.nombre_completo} (Documento: {instance.numero_documento})"
        )

    # --- TRAZABILIDAD: ACTUALIZAR ---
    def perform_update(self, serializer):
        instance = serializer.save()
        
        # Guardar la foto del acudiente si se envió una nueva
        foto_archivo = self.request.FILES.get('foto_acudiente')
        if foto_archivo:
            # Limpiamos las fotos anteriores para que solo quede la última activa
            for vieja_foto in instance.fotos.all():
                if vieja_foto.archivo and os.path.isfile(vieja_foto.archivo.path):
                    try:
                        os.remove(vieja_foto.archivo.path)
                    except Exception:
                        pass
                vieja_foto.delete()
                
            foto_obj = Foto_Acudiente(acudiente=instance)
            foto_obj.archivo.save(foto_archivo.name, foto_archivo, save=True)

        registrar_auditoria(
            self.request, 
            "ACTUALIZACIÓN", 
            f"Se modificaron datos del acudiente {instance.nombre_completo} (ID: {instance.pk})"
        )


    # --- TRAZABILIDAD: ELIMINAR ---
    def destroy(self, request, *args, **kwargs):
        acudiente = self.get_object()
        # Guardamos datos antes de la eliminación física
        nombre_eliminado = acudiente.nombre_completo
        doc_eliminado = acudiente.numero_documento

        # Borra los archivos físicos
        for foto in acudiente.fotos.all():
            if foto.archivo and os.path.isfile(foto.archivo.path):
                os.remove(foto.archivo.path)
            foto.delete()

        acudiente.delete()

        registrar_auditoria(
            request, 
            "ELIMINACIÓN", 
            f"Se eliminó permanentemente al acudiente {nombre_eliminado} (Doc: {doc_eliminado})"
        )
        
        return Response({'mensaje': 'Acudiente eliminado correctamente'}, status=status.HTTP_200_OK)


# ----------------------------------------------------------
# FOTOS - Endpoints
# ----------------------------------------------------------

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated, PermisoPorPerfil])
def fotos_acudiente(request, id):
    try:
        acudiente = Acudiente.objects.get(id=id)
    except Acudiente.DoesNotExist:
        return Response({'error': 'Acudiente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        fotos = acudiente.fotos.all().order_by('-fecha')
        data = [
            {
                'id_foto_acudiente': foto.pk,
                'url': request.build_absolute_uri(foto.archivo.url),
                'fecha': foto.fecha,
            } for foto in fotos
        ]
        return Response(data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        fotos_guardadas = []
        errores = []

        for i in range(4):
            archivo = request.FILES.get(f'foto_{i}')
            if not archivo: continue

            ext = os.path.splitext(archivo.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                errores.append(f'foto_{i}: extensión {ext} no permitida')
                continue

            foto = Foto_Acudiente(acudiente=acudiente)
            foto.archivo.save(archivo.name, archivo, save=True)
            fotos_guardadas.append({'id_foto_acudiente': foto.pk, 'url': request.build_absolute_uri(foto.archivo.url)})

        if fotos_guardadas:
            # TRAZABILIDAD: SUBIDA DE ARCHIVOS
            registrar_auditoria(
                request, 
                "SUBIDA FOTOS", 
                f"Se subieron {len(fotos_guardadas)} fotos para el acudiente {acudiente.nombre_completo}"
            )

        if not fotos_guardadas and errores:
            return Response({'errores': errores}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': True, 'fotos': fotos_guardadas, 'advertencias': errores}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, PermisoPorPerfil])
def eliminar_foto_acudiente(request, id, foto_id):
    try:
        foto = Foto_Acudiente.objects.get(id=foto_id, acudiente_id=id)
        nombre_ac = foto.acudiente.nombre_completo
    except Foto_Acudiente.DoesNotExist:
        return Response({'error': 'Foto no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    if foto.archivo and os.path.isfile(foto.archivo.path):
        os.remove(foto.archivo.path)

    foto.delete()

    # TRAZABILIDAD: ELIMINAR FOTO
    registrar_auditoria(
        request, 
        "ELIMINAR FOTO", 
        f"Se eliminó una foto (ID: {foto_id}) del acudiente {nombre_ac}"
    )

    return Response({'mensaje': 'Foto eliminada correctamente'}, status=status.HTTP_200_OK)