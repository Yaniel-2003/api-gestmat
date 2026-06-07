import os
import time 
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from ..models import Documento_matricula, Tipo_documento_matricula
from ..serializers import (
    DocumentoMatriculaListSerializer,
    DocumentoMatriculaUpdateSerializer
)

from backend.permissions import PermisoPorPerfil
from ..utils import registrar_auditoria


# ─────────────────────────────────────────────
# MANEJO DE ARCHIVOS FÍSICOS
# ─────────────────────────────────────────────

# Extensiones permitidas para subir archivos
EXTENSIONES_PERMITIDAS = ['pdf', 'jpg', 'jpeg', 'png']

# Carpeta donde se guardarán los documentos
DIRECTORIO_DOCUMENTOS = 'media/documentos/matriculas/'


def guardar_documento(archivo):
    # Obtenemos la extensión del archivo
    # split('.') separa el texto cada vez que encuentra un punto
    # [-1] obtiene el último valor de la lista
    # lower() convierte el texto a minúsculas


    extension = archivo.name.split('.')[-1].lower()

    # Validamos si la extensión está permitida
    if extension not in EXTENSIONES_PERMITIDAS:
        raise ValueError( f'Extensión no permitida. ' f'Solo se permiten: {",".join(EXTENSIONES_PERMITIDAS)}')

    # Creamos el directorio si no existe
    os.makedirs(DIRECTORIO_DOCUMENTOS, exist_ok=True)

    # Creamos un nombre único para evitar archivos repetidos
    # time.time() devuelve el tiempo actual en segundos

    nombre_archivo = ( f'doc_matricula_{int(time.time())}_{archivo.name}' )

    # Unimos la carpeta con el nombre del archivo
    ruta_archivo = os.path.join( DIRECTORIO_DOCUMENTOS, nombre_archivo )

    # Este bloque hace esto:
    #
    # Abre o crea un archivo en la ruta especificada
    # y le ponemos el alias "destino"

    with open(ruta_archivo, 'wb+') as destino:

        # Django divide el archivo en chunks (pedazos)
        # para no cargar todo el archivo en memoria RAM

        for chunk in archivo.chunks():

            # Escribe cada chunk dentro del archivo destino
            destino.write(chunk)

    # Retornamos:
    # nombre del archivo y ruta completa
    return nombre_archivo, ruta_archivo


# VIEWSET DOCUMENTOS MATRÍCULA


class DocumentoMatriculaViewSet(viewsets.ModelViewSet):

    # Solo usuarios autenticados pueden entrar
    # y además deben pasar el permiso personalizado
    permission_classes = [IsAuthenticated,PermisoPorPerfil]

    # Esto permite recibir:
    # imágenes, pdf y formularios
    parser_classes = [MultiPartParser,FormParser, JSONParser]

    # Traemos todos los documentos
    # select_related optimiza las consultas SQL
    # cuando usamos ForeignKey

    queryset = Documento_matricula.objects.select_related( 'matricula', 'tipo_documento_matricula', 'usuario_carga', 'usuario_revisa' ).all()

    # Dependiendo de la acción del CRUD
    # usamos un serializer diferente

    def get_serializer_class(self):
        # Para crear o editar
        if self.action in ('create','update','partial_update'):
            return DocumentoMatriculaUpdateSerializer
        # Para listar y mostrar información detallada
        return DocumentoMatriculaListSerializer


    # LISTAR DOCUMENTOS


    def list(self, request, *args, **kwargs):

        # Obtenemos el id de matrícula enviado
        # por query params

        matricula_id = request.query_params.get(
            'matricula_id'
        )

        # Si no enviaron matrícula
        if not matricula_id:
            return Response(
                {'error': ('Debes enviar matricula_id ''como parámetro')},status=status.HTTP_400_BAD_REQUEST
            )

        # Filtramos documentos de esa matrícula
        documentos = self.get_queryset().filter(
            matricula_id=matricula_id
        )

        # Serializamos los datos
        serializer = self.get_serializer(documentos, many=True)

        # Retornamos los datos
        return Response(serializer.data)


    # CREAR DOCUMENTO

    def create(self, request, *args, **kwargs):

        # Obtenemos el archivo enviado desde el front
        # request.FILES contiene:
        # imágenes, pdf y documentos

        archivo = request.FILES.get('archivo')

        # Si no enviaron archivo
        if not archivo:
            return Response({'error': 'Debes adjuntar un archivo'},status=status.HTTP_400_BAD_REQUEST)

        try:
            # Intentamos guardar el archivo físico
            nombre_archivo, ruta_archivo = guardar_documento(archivo)

        # Si ocurre un error
        except ValueError as e:
            return Response({'error': str(e)},status=status.HTTP_400_BAD_REQUEST)

        # Validamos datos enviados
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Guardamos en base de datos
        documento = serializer.save(

            # Usuario que subió el archivo
            usuario_carga=request.user,

            # Estado inicial
            estado='Pendiente',

            # Información del archivo
            nombre_archivo=nombre_archivo,
            ruta_archivo=ruta_archivo
        )
        registrar_auditoria(request, "SUBIDA DOCUMENTO", f"Se subió documento '{nombre_archivo}' para matrícula ID {documento.matricula_id}")

        # Retornamos datos detallados
        return Response(DocumentoMatriculaListSerializer(documento).data,status=status.HTTP_201_CREATED)

    # ELIMINAR DOCUMENTO

    def destroy(self, request, *args, **kwargs):

        # Obtenemos el documento
        documento = self.get_object()

        # Solo se pueden eliminar
        # documentos pendientes

        if documento.estado.lower() != 'pendiente':
            return Response({'error': ('Solo se pueden eliminar ''documentos pendientes')},status=status.HTTP_400_BAD_REQUEST)

        # Capturamos info antes de eliminar
        nombre_doc = documento.nombre_archivo
        matricula_id_doc = documento.matricula_id

        # Eliminamos el archivo físico
        if (documento.ruta_archivo and os.path.exists(documento.ruta_archivo)):
            os.remove(documento.ruta_archivo)

        # Eliminamos registro de base de datos
        documento.delete()
        registrar_auditoria(request, "ELIMINACIÓN DOCUMENTO", f"Se eliminó documento '{nombre_doc}' de matrícula ID {matricula_id_doc}")
        return Response({'mensaje': ('Documento eliminado correctamente')},status=status.HTTP_200_OK)


    # TIPOS DE DOCUMENTOS DISPONIBLES


    @action( detail=False, methods=['get'], url_path='tipos_disponibles')

    def tipos_disponibles(self, request):
        # Obtenemos matrícula
        matricula_id = request.query_params.get('matricula_id')

        # Validamos
        if not matricula_id:
            return Response({'error': ('Debes enviar matricula_id')},status=status.HTTP_400_BAD_REQUEST)

        # Traemos todos los tipos de documentos
        todos_los_tipos = (Tipo_documento_matricula.objects.all())

        # Obtenemos ids de documentos ya cargados
        tipos_ya_cargados = (Documento_matricula.objects.filter(matricula_id=matricula_id).values_list('tipo_documento_matricula_id', flat=True))

        # Creamos el resultado
        resultado = [
            {
                'id': tipo.id,
                'nombre': tipo.descripcion,

                # Verificamos si ya fue cargado
                'ya_cargado': (
                    tipo.id in tipos_ya_cargados
                ),
            }

            for tipo in todos_los_tipos
        ]

        return Response(
            resultado,
            status=status.HTTP_200_OK
        )


    # REVISAR DOCUMENTO

    @action(detail=True, methods=['put'])

    def revisar(self, request, pk=None):

        # Solo administradores pueden revisar
        if (request.user.perfil.nombre_perfil != 'Administrador'):

            return Response( { 'error': ( 'No tienes permiso ' 'para revisar documentos' ) }, status=status.HTTP_403_FORBIDDEN )

        # Obtenemos el documento
        documento = self.get_object()

        # Obtenemos el nuevo estado
        nuevo_estado = request.data.get('estado')

        # Observación opcional
        observacion = request.data.get( 'observacion', '')

        # Validamos estado
        if nuevo_estado not in [ 'Aprobado', 'Rechazado', 'aprobado', 'rechazado' ]:

            return Response( { 'error': ( 'El estado debe ser ' 'aprobado o rechazado' ) }, status=status.HTTP_400_BAD_REQUEST )

        # Actualizamos información
        documento.estado = nuevo_estado.capitalize()

        documento.observacion = observacion

        documento.usuario_revisa = request.user

        documento.fecha_revision = timezone.now()

        documento.save()
        registrar_auditoria(request, "REVISIÓN DOCUMENTO", f"Documento '{documento.nombre_archivo}' marcado como {documento.estado}")

        # Retornamos documento actualizado
        return Response( DocumentoMatriculaListSerializer( documento ).data, status=status.HTTP_200_OK )