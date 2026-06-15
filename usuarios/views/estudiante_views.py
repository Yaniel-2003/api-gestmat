from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from backend.permissions import PermisoPorPerfil
from ..utils import registrar_auditoria
from ..models import Estudiante, Foto_Estudiante
from ..serializers import EstudianteListSerializer, EstudianteUpdateSerializer
import os 


### PERMISOS Y CRUD
class EstudianteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]

    def get_queryset(self):
        queryset = Estudiante.objects.select_related('tipo_documento').prefetch_related('fotos')

        user = self.request.user
         
        if user.perfil.nombre_perfil != 'Administrador':
            queryset = queryset.filter(acudientes__usuario=user)   

        # Force django reloader update
        #par_bus = self.request.query_params
    
        #busqueda = par_bus.get('buscar')
        busqueda = self.request.query_params.get('buscar')

        if busqueda:
            queryset = queryset.filter(
                Q(nombre_completo__icontains=busqueda)|
                Q(numero_documento__icontains=busqueda)
            )

        tipo_doc = self.request.query_params.get('tipo_documento')
        tipo_eps = self.request.query_params.get('eps')

        if tipo_doc:
            queryset = queryset.filter(tipo_documento=tipo_doc)
        if tipo_eps:
            queryset = queryset.filter(eps=tipo_eps)

        return queryset
    
        
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EstudianteUpdateSerializer
        return EstudianteListSerializer

    def perform_create(self, serializer):
        instance = serializer.save()

        foto_archivo = self.request.FILES.get('foto_estudiante')
        if foto_archivo:
            foto_obj = Foto_Estudiante(estudiante=instance)
            foto_obj.archivo.save(foto_archivo.name, foto_archivo, save=True)

        registrar_auditoria(self.request, "CREACIÓN", f"Se registró el estudiante {instance.nombre_completo} (Documento: {instance.numero_documento})")

    def perform_update(self, serializer):
        instance = serializer.save()

        foto_archivo = self.request.FILES.get('foto_estudiante')
        if foto_archivo:
            for vieja_foto in instance.fotos.all():
                if vieja_foto.archivo and os.path.isfile(vieja_foto.archivo.path):
                    try:
                        os.remove(vieja_foto.archivo.path)
                    except Exception:
                        pass
                vieja_foto.delete()
            
            foto_obj = Foto_Estudiante(estudiante=instance)
            foto_obj.archivo.save(foto_archivo.name, foto_archivo, save=True)
                
        registrar_auditoria(self.request, "ACTUALIZACIÓN", f"Se actualizó el estudiante {instance.nombre_completo} (ID: {instance.pk})")
    
    def destroy(self, request, *args, **kwargs):
        estudiante = self.get_object()
        nombre = estudiante.nombre_completo
        doc = estudiante.numero_documento

        for foto in estudiante.fotos.all():
            if foto.archivo and os.path.isfile(foto.archivo.path):
                os.remove(foto.archivo.path)
            foto.delete()
        estudiante.delete()
        registrar_auditoria(request, "ELIMINACIÓN", f"Se eliminó el estudiante {nombre} (Doc: {doc})")
        return Response({'mensaje':'Estudiante eliminado correctamente'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='agregar-acudiente', parser_classes=[MultiPartParser, FormParser])
    def agregar_acudiente(self, request, pk=None):
        estudiante = self.get_object()
        
        from ..serializers import AcudienteUpdateSerializer
        from ..models import Acudiente, Foto_Acudiente
        
        numero_documento = request.data.get('numero_documento')
        if numero_documento:
            acudiente = Acudiente.objects.filter(numero_documento=numero_documento).first()
            if acudiente:
                if acudiente not in estudiante.acudientes.all():
                    estudiante.acudientes.add(acudiente)
                    registrar_auditoria(request, "ACTUALIZACIÓN", f"Se vinculó acudiente existente {acudiente.nombre_completo} (ID: {acudiente.pk}) al estudiante {estudiante.nombre_completo} (ID: {estudiante.pk})")
                    return Response({'mensaje': 'Acudiente existente vinculado correctamente', 'acudiente_id': acudiente.pk}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'El acudiente ya está vinculado a este estudiante'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AcudienteUpdateSerializer(data=request.data)
        if serializer.is_valid():
            acudiente = serializer.save(usuario=request.user)
            
            foto_archivo = request.FILES.get('foto_acudiente')
            if foto_archivo:
                foto_obj = Foto_Acudiente(acudiente=acudiente)
                foto_obj.archivo.save(foto_archivo.name, foto_archivo, save=True)
            
            estudiante.acudientes.add(acudiente)
            
            registrar_auditoria(request, "CREACIÓN", f"Se registró y vinculó acudiente {acudiente.nombre_completo} (ID: {acudiente.pk}) al estudiante {estudiante.nombre_completo} (ID: {estudiante.pk})")
            return Response({'mensaje': 'Acudiente registrado y vinculado correctamente', 'acudiente_id': acudiente.pk}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

### FOTOS ESTUDIANTE 

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated, PermisoPorPerfil])
def fotos_estudiante(request, id):
    try:
        estudiante = Estudiante.objects.get(id=id)
    except Estudiante.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        fotos = estudiante.fotos.all()
        data = [
            {
                'id_foto_estudiante': foto.pk,
                'url': request.build_absolute_uri(foto.archivo.url),
                'fecha': None,
            }
            for foto in fotos
        ]
        return Response(data, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        fotos_guardadas = []
        errores = []

        for i in range(4):
            archivo = request.FILES.get(f'foto_{i}')

            if not archivo:
                continue

            ext = os.path.splitext(archivo.name)[1].lower()

            if ext not in ['.jpg','.jpeg','.png', '.gif', '.webp']:
                errores.append(f'foto_{i}: extension {ext} no permitida')
                continue


            foto = Foto_Estudiante(estudiante=estudiante)
            foto.archivo.save(archivo.name, archivo, save=True)

            fotos_guardadas.append({
                'id_foto_acudiente': foto.pk,
                'url': request.build_absolute_uri(foto.archivo.url),
            })

        if fotos_guardadas:
            registrar_auditoria(request, "SUBIDA FOTOS", f"Se subieron {len(fotos_guardadas)} fotos para el estudiante {estudiante.nombre_completo}")
        
        if not fotos_guardadas and errores:
            return Response({'errores': errores},status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': True,
            'estudiante': id,
            'fotos': fotos_guardadas,
            **(({'advertencias': errores}) if errores else {})
        }, status=status.HTTP_201_CREATED)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, PermisoPorPerfil])
def eliminar_fotos_estudiante(request, id, foto_id):
    try:
        foto = Foto_Estudiante.objects.get(id=foto_id, estudiante_id=id)
    except Foto_Estudiante.DoesNotExist:
        return Response({'error':'Foto no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if foto.archivo and os.path.isfile(foto.archivo.path):
        os.remove(foto.archivo.path)

    foto.delete()
    registrar_auditoria(request, "ELIMINAR FOTO", f"Se eliminó una foto (ID: {foto_id}) del estudiante ID {id}")
    return Response({'mensaje':'Fotoeliminada correctamente'}, status=status.HTTP_200_OK)