from rest_framework import serializers
from .models import *
from django.db import transaction

# ----------------------------------------------------------
# MIXIN BASE
# ----------------------------------------------------------

class BaseSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='pk')
    class Meta:
        pass


# ----------------------------------------------------------
# NIVEL 1 - SIMPLES (solo List, no necesitan Create separado
#           porque sus campos son todos planos y sin lógica)
# ----------------------------------------------------------

class EpsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Eps
        fields = ['id', 'id_eps', 'nombre_eps', 'telefono', 'direccion']


class JornadaSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Jornada
        fields = ['id', 'id_jornada', 'nombre_jornada', 'hora_inicio', 'hora_fin', 'descripcion']


class MetodoPagoSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Metodo_pago
        fields = ['id', 'id_metodo_pago', 'nombre', 'descripcion', 'fecha_creacion']


class ProcesoMatriculaSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Proceso_matricula
        fields = ['id', 'id_proceso_matricula', 'nombre_paso', 'descripcion', 'orden', 'obligatorio', 'activo', 'icono', 'color']


class ProcesoMatriculaConEstadoSerializer(BaseSerializer):
    # definimos un campo extra que no existe en el modelo pero lo queremos en el json
    estado_paso = serializers.SerializerMethodField()

    class Meta(BaseSerializer.Meta):
        model = Proceso_matricula
        fields = ['id', 'id_proceso_matricula', 'nombre_paso', 'orden', 'icono', 'color', 'estado_paso']

    def get_estado_paso(self, obj):
        """
        Lógica de Cálculo de Estado:
        ---------------------------
        Este método busca si existe un registro en la tabla Seguimiento_matricula
        para el paso actual y la matrícula solicitada.
        - Si existe: Devuelve el estado registrado (completado, en_progreso, etc.)
        - Si NO existe: Devuelve 'pendiente' por defecto.
        """
        # sacamos o traemos el id de la matricula que mandamos desde la vista a través del contexto
        matricula_id = self.context.get('matricula_id')


        #buscamos en latabla de seguimiento si el paso ya tiene registro
        seguimiento = Seguimiento_matricula.objects.filter(
            paso=obj,
            matricula_id=matricula_id
        ).first()

        #Logica de que responder
        if seguimiento:
            return seguimiento.estado
        return 'pendiente'


class TipoDocumentoMatriculaSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Tipo_documento_matricula
        fields = ['id', 'id_tipo_documento_matricula', 'descripcion', 'obligatorio']


class TipoDocumentoSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Tipo_documento
        fields = ['id', 'id_tipo_documento', 'descripcion', 'sigla']


# ----------------------------------------------------------
# NIVEL 2 - CURSO
# ----------------------------------------------------------

class CursoListSerializer(BaseSerializer):
    jornada = JornadaSerializer()

    class Meta(BaseSerializer.Meta):
        model  = Curso
        fields = ['id', 'id_curso', 'jornada', 'nombre_curso', 'grado', 'activo', 'cupo_total', 'cupo_disponible']


class CursoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Curso
        fields = ['jornada', 'nombre_curso', 'grado', 'activo', 'cupo_total', 'cupo_disponible']

    def validate(self, data):
        # Validación cruzada: cupo_disponible no puede superar cupo_total
        cupo_total      = data.get('cupo_total',      getattr(self.instance, 'cupo_total',      None))
        cupo_disponible = data.get('cupo_disponible', getattr(self.instance, 'cupo_disponible', None))

        if cupo_disponible is not None and cupo_total is not None:
            if cupo_disponible > cupo_total:
                raise serializers.ValidationError('El cupo disponible no puede superar el cupo total')
        return data


# ----------------------------------------------------------
# NIVEL 2 - PERFIL
# ----------------------------------------------------------

class PerfilListSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Perfil
        fields = ['id', 'id_perfil', 'nombre_perfil', 'insert_perfil', 'update_perfil', 'delete_perfil', 'view_perfil', 'estado']


class PerfilUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Perfil
        fields = ['nombre_perfil', 'insert_perfil', 'update_perfil', 'delete_perfil', 'view_perfil', 'estado']


# ----------------------------------------------------------
# USUARIO
# ----------------------------------------------------------

class FotoUsuarioSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Foto_Usuario
        fields = ['id', 'id_foto_usuario', 'archivo']


class UsuarioBasicoSerializer(BaseSerializer):
    """Solo para anidar en otros serializers, nunca para escribir."""
    class Meta(BaseSerializer.Meta):
        model  = Usuario
        fields = ['id', 'id_usuario', 'username', 'first_name', 'last_name', 'email']


class UsuarioListSerializer(BaseSerializer):
    perfil         = PerfilListSerializer()
    tipo_documento = TipoDocumentoSerializer()
    fotos          = FotoUsuarioSerializer(many=True) # Reemplaza el antiguo campo foto_usuario

    class Meta(BaseSerializer.Meta):
        model  = Usuario
        fields = [
            'id', 'id_usuario', 'username', 'first_name', 'last_name', 'email',
            'telefono', 'num_documento', 'fotos',
            'is_active', 'date_joined', 'perfil', 'tipo_documento',
        ]
        read_only_fields = ['id_usuario', 'date_joined']


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """
    Create y Update en uno solo.
    - password es write_only y opcional en updates (required=False)
    """
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model  = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password',
            'telefono', 'num_documento', 'perfil', 'tipo_documento',
        ]

    def validate_username(self, value):
        # Excluye el propio usuario en updates
        qs = Usuario.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Este usuario ya existe')
        return value

    def validate_email(self, value):
        qs = Usuario.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Este email ya está en uso')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        usuario  = Usuario(**validated_data)
        if password:
            usuario.set_password(password)
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UsuarioLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


# ----------------------------------------------------------
# NIVEL 3 - TRAZABILIDAD
# ----------------------------------------------------------

class TrazabilidadSerializer(BaseSerializer):
    """Solo lectura, la trazabilidad nunca se crea desde un serializer externo."""
    usuario = UsuarioBasicoSerializer()

    class Meta(BaseSerializer.Meta):
        model  = Trazabilidad
        fields = ['id', 'id_trazabilidad', 'usuario', 'accion', 'descripcion', 'fecha_hora', 'ip_origen', 'dispositivo']


# ----------------------------------------------------------
# NIVEL 3 - ACUDIENTE
# ----------------------------------------------------------

class FotoAcudienteSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Foto_Acudiente
        fields = ['id', 'id_foto_acudiente', 'archivo', 'fecha']


class AcudienteListSerializer(BaseSerializer):
    tipo_documento = TipoDocumentoSerializer()
    usuario        = UsuarioBasicoSerializer()
    fotos          = FotoAcudienteSerializer(many=True)      # ← relación real con el modelo

    class Meta(BaseSerializer.Meta):
        model  = Acudiente
        fields = [
            'id', 'id_acudiente', 'tipo_documento', 'usuario', 'numero_documento',
            'nombre_completo', 'parentesco', 'telefono', 'email', 'fotos',
        ]


class AcudienteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Acudiente
        fields = [
            'tipo_documento', 'numero_documento',
            'nombre_completo', 'parentesco', 'telefono', 'email',
        ]
        # usuario se asigna en perform_create, no lo expone el cliente

    def validate_telefono(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError('El teléfono solo debe contener números')
        return value

    def validate_numero_documento(self, value):
        # Excluye el propio acudiente en updates
        qs = Acudiente.objects.filter(numero_documento=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe un acudiente con este documento')
        return value


# ----------------------------------------------------------
# NIVEL 4 - ESTUDIANTE
# ----------------------------------------------------------

class FotoEstudianteSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model  = Foto_Estudiante
        fields = ['id', 'id_foto_estudiante', 'archivo']


class EstudianteListSerializer(BaseSerializer):
    tipo_documento = TipoDocumentoSerializer()
    eps            = EpsSerializer()
    acudientes     = AcudienteListSerializer(many=True)
    fotos          = FotoEstudianteSerializer(many=True)

    class Meta(BaseSerializer.Meta):
        model  = Estudiante
        fields = [
            'id', 'id_estudiante', 'tipo_documento', 'eps', 'acudientes',
            'numero_documento', 'nombre_completo', 'fecha_nacimiento', 'fotos',
        ]


class EstudianteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Estudiante
        fields = [
            'tipo_documento', 'eps', 'acudientes',
            'numero_documento', 'nombre_completo', 'fecha_nacimiento',
        ]

    def validate_numero_documento(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('El número de documento debe contener solo números')
        qs = Estudiante.objects.filter(numero_documento=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe un estudiante con este documento')
        return value


# ----------------------------------------------------------
# NIVEL 5 - MATRÍCULA
# ----------------------------------------------------------

class MatriculaListSerializer(BaseSerializer):
    estudiante = EstudianteListSerializer()
    acudiente  = AcudienteListSerializer()
    curso      = CursoListSerializer()
    jornada    = JornadaSerializer()

    class Meta(BaseSerializer.Meta):
        model  = Matricula
        fields = [
            'id', 'id_matricula', 'estudiante', 'acudiente', 'curso', 'jornada',
            'year_lectivo', 'fecha_matricula', 'fecha_inicio', 'estado', 'observaciones',
        ]


class MatriculaUpdateSerializer(serializers.ModelSerializer):
    #Pasamos los campos completos para crear desde matriculas
    estudiante = EstudianteUpdateSerializer()
    acudiente = AcudienteUpdateSerializer()

    class Meta:
        model  = Matricula
        fields = ['estudiante', 'acudiente', 'curso', 'jornada', 'year_lectivo', 'fecha_inicio', 'estado', 'observaciones']

    def create(self, validated_data):
        #Traemos los datos anidados
        datos_estudiante = validated_data.pop('estudiante')
        datos_acudiente = validated_data.pop('acudiente')
        #usamos un bloque atomico si algo falla no guarda nada 
        with transaction.atomic():
            nuevo_acudiente = Acudiente.objects.create(**datos_acudiente)
            nuevo_estudiante = Estudiante.objects.create(**datos_estudiante)

            nuevo_estudiante.acudientes.add(nuevo_acudiente)
            #creamos el estudiante y le asignamos el acudiente
            
            #Ya por ultimo creamos la matricual 
            matricula = Matricula.objects.create(
                estudiante=nuevo_estudiante,
                acudiente=nuevo_acudiente,
                **validated_data # aui estan los datos de la matricula
            )
            return matricula


    def validate(self, data):
        # Evita matrículas duplicadas del mismo estudiante en el mismo año
        estudiante_data  = data.get('estudiante')
        year_lectivo = data.get('year_lectivo', getattr(self.instance, 'year_lectivo', None))

        # 2. Si estamos CREANDO (Pasarela), buscamos por el documento del estudiante
        if not self.instance and estudiante_data:
            documento = estudiante_data.get('numero_documento')
            
            # Buscamos si existe alguna matrícula donde el estudiante tenga ese documento este año
            qs = Matricula.objects.filter(
                estudiante__numero_documento=documento, 
                year_lectivo=year_lectivo
            )
            
            if qs.exists():
                raise serializers.ValidationError(
                    {'estudiante': f'El estudiante con documento {documento} ya está matriculado para el año {year_lectivo}.'}
                )

        # 3. Si estamos ACTUALIZANDO (un registro que ya existe)
        elif self.instance:
            estudiante_obj = getattr(self.instance, 'estudiante', None)
            qs = Matricula.objects.filter(estudiante=estudiante_obj, year_lectivo=year_lectivo).exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise serializers.ValidationError('Este registro ya existe para el año lectivo indicado.')

        return data


# ----------------------------------------------------------
# NIVEL 6 - DOCUMENTO MATRÍCULA
# ----------------------------------------------------------

class DocumentoMatriculaListSerializer(BaseSerializer):
    matricula                = MatriculaListSerializer()
    tipo_documento_matricula = TipoDocumentoMatriculaSerializer()
    usuario_carga            = UsuarioBasicoSerializer()
    usuario_revisa           = UsuarioBasicoSerializer()

    class Meta(BaseSerializer.Meta):
        model  = Documento_matricula
        fields = [
            'id', 'id_documento_matricula', 'matricula', 'tipo_documento_matricula', 'nombre_archivo',
            'ruta_archivo', 'fecha_carga', 'fecha_entrega', 'estado',
            'observacion', 'usuario_carga', 'usuario_revisa', 'fecha_revision',
        ]


class DocumentoMatriculaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Documento_matricula
        fields = [
            'matricula', 'tipo_documento_matricula', 'nombre_archivo', 'ruta_archivo',
            'fecha_entrega', 'estado', 'observacion', 'usuario_revisa', 'fecha_revision',
        ]
        read_only_fields = ['nombre_archivo', 'ruta_archivo']
        # usuario_carga se asigna en la view, no lo expone el cliente


# ----------------------------------------------------------
# NIVEL 6 - PAGO
# ----------------------------------------------------------

class PagoListSerializer(BaseSerializer):
    matricula   = MatriculaListSerializer()
    metodo_pago = MetodoPagoSerializer()

    class Meta(BaseSerializer.Meta):
        model  = Pago
        fields = ['id', 'id_pago', 'matricula', 'fecha_pago', 'valor_pago', 'metodo_pago', 'estado_pago']


class PagoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Pago
        fields = ['matricula', 'fecha_pago', 'valor_pago', 'metodo_pago', 'estado_pago']

    def validate_valor_pago(self, value):
        if value <= 0:
            raise serializers.ValidationError('El valor del pago debe ser mayor a 0')
        return value


# ----------------------------------------------------------
# NIVEL 6 - SEGUIMIENTO MATRÍCULA
# ----------------------------------------------------------

# ----------------------------------------------------------
# NIVEL 6 - SEGUIMIENTO MATRÍCULA
# ----------------------------------------------------------

class SeguimientoMatriculaListSerializer(BaseSerializer):
    """
    SERIALIZER DE LECTURA PARA SEGUIMIENTO_MATRICULA
    
    Función: Transformar datos de BD a JSON para consultas GET
    Campos mostrados: Todos los detalles del seguimiento incluyendo relaciones
    
    Relaciones expandidas:
    - matricula: Muestra los datos completos de la matrícula
    - paso: Muestra los datos completos del paso del proceso
    - usuario_actualiza: Muestra los datos básicos del usuario que actualizó
    """
    matricula         = MatriculaListSerializer()
    paso              = ProcesoMatriculaSerializer()
    usuario_actualiza = UsuarioBasicoSerializer()

    class Meta(BaseSerializer.Meta):
        model  = Seguimiento_matricula
        fields = [
            'id', 'id_seguimiento_matricula', 'matricula', 'paso', 'usuario_actualiza', 'estado',
            'fecha_inicio', 'fecha_completado', 'observacion', 'fecha_actualizacion',
        ]


class SeguimientoMatriculaUpdateSerializer(serializers.ModelSerializer):
    """
    SERIALIZER DE ESCRITURA PARA SEGUIMIENTO_MATRICULA
    
    Función: Validar y transformar datos JSON a registros BD para POST, PATCH, PUT
    Métodos de validación: Se ejecutan automáticamente antes de guardar
    
    Flujo de validación:
    1. validate_paso() - Valida que el paso exista y esté activo
    2. validate() - Valida la lógica de negocio completa (orden de pasos, no duplicados, etc.)
    3. perform_create() / perform_update() - Asigna usuario y fecha automáticamente
    
    Campo especial:
    - usuario_actualiza: Es read_only, no viene del frontend. Se asigna en la vista.
    """
    usuario_actualiza = UsuarioBasicoSerializer(read_only=True)

    class Meta:
        model  = Seguimiento_matricula
        fields = ['matricula', 'paso', 'usuario_actualiza', 'estado', 'fecha_completado', 'observacion']
        read_only_fields = ['usuario_actualiza']

    def validate_paso(self, value):
        """
        VALIDADOR DE CAMPO: paso
        
        Cuándo se ejecuta: Después de que el campo 'paso' es deserializado
        Qué valida: 
        - Que el paso exista (ya se valida por FK)
        - Que el paso esté activo en el catálogo
        
        Si falla: Levanta ValidationError con mensaje personalizado
        
        Lógica:
        -------
        1. Recibe 'value' que es la instancia de Proceso_matricula
        2. Si value.activo es False, rechaza con error
        3. Si es True, permite continuar
        
        Ejemplo de error:
        "El paso seleccionado no está activo en el catálogo"
        """
        if not value.activo:
            raise serializers.ValidationError(
                'El paso seleccionado no está activo en el catálogo'
            )
        return value

    def validate(self, attrs):
        """
        VALIDADOR GLOBAL: validate()
        
        Cuándo se ejecuta: Después de que TODOS los campos han sido validados
        Qué valida: Lógica de negocio compleja que involucra múltiples campos
        
        Validaciones que hace:
        ----------------------
        
        1. EXISTENCIA DE CAMPOS REQUERIDOS
           - Verifica que matricula y paso existan (necesarios para buscar historiales)
        
        2. PREVENCIÓN DE DUPLICADOS
           - Si es CREATE (self.instance is None):
             Si ya existe otro Seguimiento_matricula con la misma matricula+paso,
             rechaza y sugiere usar PATCH en lugar de POST
        
        3. VALIDACIÓN DE ORDEN
           - Busca el paso anterior (orden < paso actual)
           - Si existe paso anterior, REQUIERE que esté marcado como 'completado'
           - Esto evita que el usuario se salte pasos
           
           Ejemplo:
           Paso 1 = "Registrar estudiante"
           Paso 2 = "Asignar acudiente"
           Paso 3 = "Pagar matrícula"
           
           El usuario NO puede ir directamente a Paso 3 si no completó Paso 2.
        
        Flujo paso a paso:
        ------------------
        """
        
        # Obtener matricula del payload o de la instancia si es update
        matricula = attrs.get('matricula', getattr(self.instance, 'matricula', None))
        paso = attrs.get('paso', getattr(self.instance, 'paso', None))

        # 1. Validar que ambos campos existan
        if not matricula or not paso:
            raise serializers.ValidationError(
                'Debe enviar matricula y paso para el seguimiento'
            )

        # 2. Validar duplicados solo en CREATE
        if self.instance is None and Seguimiento_matricula.objects.filter(
            matricula=matricula,
            paso=paso
        ).exists():
            raise serializers.ValidationError(
                'Ya existe un seguimiento para esta matrícula y paso. Use PATCH para actualizarlo.'
            )

        # 3. Validar orden: el paso anterior debe estar completado
        
        # Buscar el paso inmediatamente anterior (orden < paso actual)
        paso_anterior = Proceso_matricula.objects.filter(
            orden__lt=paso.orden,  # orden menor que el paso actual
            activo=True
        ).order_by('-orden').first()  # Traer el más cercano (el anterior directo)
        
        if paso_anterior:
            # Si existe paso anterior, verificar que ya esté completado
            seguimiento_anterior = Seguimiento_matricula.objects.filter(
                matricula=matricula,
                paso=paso_anterior,
                estado='completado'
            ).first()
            
            if not seguimiento_anterior:
                # El paso anterior NO está completado, rechazar
                raise serializers.ValidationError(
                    f'No se puede avanzar al paso actual si el paso anterior "{paso_anterior.nombre_paso}" no está completado.'
                )

        return attrs

