import os
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# ================================================================================
# SIGNALS Y RECEIVERS
# ================================================================================
# Se importan aquí para que Django los registre automáticamente al cargar modelos.
# Estos decoradores activan "disparadores" que ejecutan lógica cuando ciertos eventos ocurren.
# ================================================================================

# ── TABLA ACUDIENTES ──────────────────────────────────────────────
class Acudiente(models.Model):
    tipo_documento   = models.ForeignKey('Tipo_documento', on_delete=models.SET_NULL, null=True, blank=True)
    usuario          = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    numero_documento = models.CharField(max_length=20, null=True, blank=True)
    nombre_completo  = models.CharField(max_length=100, null=True, blank=True)
    parentesco       = models.CharField(max_length=50, null=True, blank=True)
    telefono         = models.CharField(max_length=15, null=True, blank=True)
    email            = models.EmailField(max_length=50, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'acudientes'
        verbose_name = 'Acudiente'
        verbose_name_plural = 'Acudientes'

    def __str__(self):
        return self.nombre_completo or "Sin nombre"


def Ruta_Foto_Acudientes(instance, filename):
    return f'Acudientes/id_{instance.acudiente.id}/{filename}'

class Foto_Acudiente(models.Model):
    acudiente = models.ForeignKey('Acudiente', on_delete=models.CASCADE, related_name='fotos')
    archivo = models.ImageField(upload_to=Ruta_Foto_Acudientes)
    ruta_disco = models.CharField(max_length=500, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fotos_acudientes'
        verbose_name = 'Foto de Acudiente'
        verbose_name_plural = 'Fotos de Acudientes'

    def __str__(self):
        return f"Foto de {self.acudiente.nombre_completo} - ID: {self.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.archivo and not self.ruta_disco:
            self.ruta_disco = self.archivo.path
            super().save(update_fields=['ruta_disco'])


# ── TABLA CURSOS ──────────────────────────────────────────────────
class Curso(models.Model):
    jornada         = models.ForeignKey('Jornada', on_delete=models.SET_NULL, null=True, blank=True)
    nombre_curso    = models.CharField(max_length=20, null=True, blank=True)
    grado           = models.CharField(max_length=10, null=True, blank=True)
    activo          = models.BooleanField(default=True)
    cupo_total      = models.IntegerField(default=30)
    cupo_disponible = models.IntegerField(default=30)

    class Meta:
        db_table = 'cursos'
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return f"{self.nombre_curso} - Grado {self.grado}" if self.nombre_curso else "Sin nombre"


# ── TABLA DOCUMENTOS DE MATRICULA ────────────────────────────────
class Documento_matricula(models.Model):
    matricula                = models.ForeignKey('Matricula', on_delete=models.SET_NULL, null=True, blank=True)
    tipo_documento_matricula = models.ForeignKey('Tipo_documento_matricula', on_delete=models.SET_NULL, null=True, blank=True)
    nombre_archivo           = models.CharField(max_length=255, null=True, blank=True)
    ruta_archivo             = models.CharField(max_length=250, null=True, blank=True)
    fecha_carga              = models.DateTimeField(auto_now_add=True)
    fecha_entrega            = models.DateField(null=True, blank=True)
    estado                   = models.CharField(
                                    max_length=20,
                                    choices=[
                                        ('Pendiente', 'Pendiente'),
                                        ('Revision',  'Revision'),
                                        ('Aprobado',  'Aprobado'),
                                        ('Rechazado', 'Rechazado')
                                    ],
                                    default='Pendiente'
                                )
    observacion    = models.TextField(null=True, blank=True)  
    usuario_carga  = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='cargas')
    usuario_revisa = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='revisiones')
    fecha_revision = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'documentos_matricula'
        verbose_name = 'Documento de Matrícula'
        verbose_name_plural = 'Documentos de Matrícula'

    def __str__(self):
        return self.nombre_archivo or "Sin nombre"


# ── TABLA EPS ────────────────────────────────────────────────────
class Eps(models.Model):
    nombre_eps = models.CharField(max_length=100, null=True, blank=True)
    telefono   = models.CharField(max_length=15, null=True, blank=True)
    direccion  = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'eps'
        verbose_name = 'EPS'
        verbose_name_plural = 'EPS'

    def __str__(self):
        return self.nombre_eps or "Sin nombre"


# ── TABLA ESTUDIANTE ─────────────────────────────────────────────
class Estudiante(models.Model):
    tipo_documento   = models.ForeignKey('Tipo_documento', on_delete=models.SET_NULL, null=True, blank=True)
    eps              = models.ForeignKey('Eps', on_delete=models.SET_NULL, null=True, blank=True)
    acudientes       = models.ManyToManyField('Acudiente', blank=True)
    numero_documento = models.CharField(max_length=20, null=True, blank=True)
    nombre_completo  = models.CharField(max_length=100, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'estudiantes'
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'

    def __str__(self):
        return self.nombre_completo or "Sin nombre"


def Ruta_Foto_Estudiante(instance, filename):
    return f'Estudiante/id_{instance.estudiante.id}/{filename}'

class Foto_Estudiante(models.Model):
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE, related_name='fotos')
    archivo = models.ImageField(upload_to=Ruta_Foto_Estudiante)
    ruta_disco = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'fotos_estudiantes'
        verbose_name = 'Foto de Estudiante'
        verbose_name_plural = 'Fotos de Estudiantes'

    def __str__(self):
        return f"Foto de {self.estudiante.nombre_completo} - ID: {self.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.archivo and not self.ruta_disco:
            self.ruta_disco = self.archivo.path
            super().save(update_fields=['ruta_disco'])


# ── TABLA JORNADA ────────────────────────────────────────────────
class Jornada(models.Model):
    nombre_jornada = models.CharField(max_length=50, null=True, blank=True)
    hora_inicio    = models.TimeField(null=True, blank=True)
    hora_fin       = models.TimeField(null=True, blank=True)
    descripcion    = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'jornadas'
        verbose_name = 'Jornada'
        verbose_name_plural = 'Jornadas'

    def __str__(self):
        return self.nombre_jornada or "Sin nombre"


# ── TABLA DE MATRICULAS ──────────────────────────────────────────
class Matricula(models.Model):
    estudiante      = models.ForeignKey('Estudiante', on_delete=models.SET_NULL, null=True, blank=True)
    acudiente       = models.ForeignKey('Acudiente', on_delete=models.SET_NULL, null=True, blank=True)
    curso           = models.ForeignKey('Curso', on_delete=models.SET_NULL, null=True, blank=True)
    jornada         = models.ForeignKey('Jornada', on_delete=models.SET_NULL, null=True, blank=True)
    year_lectivo    = models.IntegerField()
    fecha_matricula = models.DateField(auto_now_add=True)
    fecha_inicio    = models.DateField(null=True, blank=True)  
    estado          = models.BooleanField(default=True)
    observaciones   = models.TextField(null=True, blank=True)  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Guardamos el estado anterior para detectar cambios en signals
        self._estado_anterior = self.estado if self.pk else None

    class Meta:
        db_table = 'matriculas'
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'

    def __str__(self):
        return f"{self.estudiante} - {self.year_lectivo}" if self.year_lectivo else "Sin datos"


# ── TABLA METODO DE PAGO ─────────────────────────────────────────
class Metodo_pago(models.Model):
    nombre         = models.CharField(max_length=255, null=True, blank=True)
    descripcion    = models.TextField(null=True, blank=True)  
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'metodos_pago'
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'

    def __str__(self):
        return self.nombre or "Sin nombre"


# ── TABLA PAGINAS ────────────────────────────────────────────────
class Pagina(models.Model):
    nombre_pagina  = models.CharField(max_length=100, null=True, blank=True)
    ruta_pagina    = models.CharField(max_length=255, null=True, blank=True)
    mostrar_pagina = models.BooleanField(default=False)
    icono_pagina   = models.CharField(max_length=255, null=True, blank=True)
    orden_pagina   = models.IntegerField(null=True, blank=True)
    pagina_padre   = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'paginas'
        verbose_name = 'Página'
        verbose_name_plural = 'Páginas'

    def __str__(self):
        return self.nombre_pagina or "Sin nombre"


# ── TABLA DE COMPONENTES ─────────────────────────────────────────
class Componente(models.Model): 
    pagina        = models.ForeignKey('Pagina', on_delete=models.SET_NULL, null=True, blank=True)
    nombre        = models.CharField(max_length=100, null=True, blank=True)
    identificador = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'componentes'
        verbose_name = 'Componente'
        verbose_name_plural = 'Componentes'

    def __str__(self):
        return self.nombre or "Sin nombre"


# ── TABLA PERFIL ─────────────────────────────────────────────────
class Perfil(models.Model):
    nombre_perfil = models.CharField(max_length=50, null=True, blank=True)
    pagina_inicio = models.ForeignKey('Pagina', on_delete=models.SET_NULL, null=True, blank=True)
    insert_perfil = models.BooleanField(default=False)
    update_perfil = models.BooleanField(default=False)
    delete_perfil = models.BooleanField(default=False)
    view_perfil   = models.BooleanField(default=False)
    estado        = models.BooleanField(default=True)
    paginas       = models.ManyToManyField('Pagina', blank=True, related_name='perfiles')
    componentes   = models.ManyToManyField('Componente', blank=True, related_name='perfiles')  

    class Meta:
        db_table = 'perfiles'
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return self.nombre_perfil or "Sin nombre"


# ── TABLA DE PAGOS ───────────────────────────────────────────────
class Pago(models.Model):  
    matricula   = models.ForeignKey('Matricula', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_pago  = models.DateTimeField(auto_now_add=True)
    valor_pago  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    metodo_pago = models.ForeignKey('Metodo_pago', on_delete=models.SET_NULL, null=True, blank=True)
    estado_pago = models.CharField(
                    max_length=50,
                    choices=[
                        ('pendiente',  'Pendiente de Pago'),
                        ('confirmado', 'Pago Confirmado'),
                        ('rechazado',  'Pago Rechazado'),
                        ('error',      'Error en Transacción')
                    ],
                    default='pendiente'
                )

    class Meta:
        db_table = 'pagos'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f"{self.matricula} - {self.fecha_pago}"


# ================================================================================
# SIGNAL: TRIGGER AUTOMÁTICO PARA PAGOS CONFIRMADOS
# ================================================================================
# Función: crear_seguimiento_desde_pago
# Cuándo se ejecuta: Después de que un registro Pago se guarda en la BD (post_save)
# Por qué: Automatizar la marcación del paso "Pago" como completado sin que el frontend lo tenga que hacer
# ================================================================================

@receiver(post_save, sender=Pago)
def crear_seguimiento_desde_pago(sender, instance, created, **kwargs):

    
    # Paso 1: Validar que el pago es confirmado
    if instance.estado_pago != 'confirmado':
        return

    # Paso 2: Validar que el pago está asociado a una matrícula
    if not instance.matricula:
        return

    # Paso 3: Buscar el paso de proceso cuyo nombre contiene 'pago' (case-insensitive)
    paso_pago = Proceso_matricula.objects.filter(
        nombre_paso__icontains='pago',  # Busca 'pago' en el nombre sin importar mayúsculas
        activo=True  # Solo considerar pasos activos
    ).first()
    
    if not paso_pago:
        # Si no existe el paso de pago en el catálogo, no hacemos nada
        return

    # Paso 4: Usar get_or_create para crear o recuperar el seguimiento
    # get_or_create devuelve una tupla: (objeto, fue_creado)
    seguimiento, created_seg = Seguimiento_matricula.objects.get_or_create(
        matricula=instance.matricula,  # Identificar por matrícula
        paso=paso_pago,  # Identificar por paso de proceso
        defaults={  # Si se crea nuevo, estos son los valores iniciales
            'estado': 'completado',
            'fecha_completado': timezone.now(),
        }
    )
    
    # Paso 5: Si el seguimiento ya existía, actualizar su estado a completado
    if not created_seg and seguimiento.estado != 'completado':
        seguimiento.estado = 'completado'
        seguimiento.fecha_completado = timezone.now()
        seguimiento.save(update_fields=['estado', 'fecha_completado'])


# ================================================================================
# DISPARADOR AUTOMÁTICO: SEGUIMIENTOS INICIALES
# ================================================================================
# Cuándo se ejecuta: Justo después de crear una nueva Matrícula (INSERT).
# Por qué: Evitar que el usuario tenga que marcar manualmente pasos que ya se
# hicieron durante el proceso de registro integral.
# ================================================================================

@receiver(post_save, sender=Matricula)
def crear_seguimientos_iniciales(sender, instance, created, **kwargs):
    """
    RECEIVER POST_SAVE PARA MATRICULA
    
    Este receiver automatiza el inicio del flujo de seguimiento. Al detectarse 
    una nueva matrícula, busca en el catálogo los pasos que corresponden a 
    la creación de los datos base y los marca como completados.
    
    Pasos afectados:
    1. Registrar estudiante (Ya se hizo al crear la matrícula)
    2. Asignar acudiente (Ya se hizo al crear la matrícula)
    3. Asignar curso y jornada (Ya se hizo al crear la matrícula)
    """
    
    # Solo actuamos si es una creación (INSERT), no en actualizaciones
    if not created:
        return

    # ── GESTIÓN AUTOMÁTICA DE CUPO ──
    # Al crear una matrícula, decrementamos el cupo disponible del curso asignado
    if instance.curso and instance.curso.cupo_disponible > 0:
        instance.curso.cupo_disponible -= 1
        instance.curso.save(update_fields=['cupo_disponible'])

    # Definimos los criterios de búsqueda para identificar los pasos en el catálogo.
    # Se usa 'key' y 'nombre' para tener flexibilidad en la búsqueda por icontains.
    pasos_iniciales = [
        {'key': 'estudiante', 'nombre': 'Registrar estudiante'},
        {'key': 'acudiente', 'nombre': 'Asignar acudiente'},
        {'key': 'curso', 'nombre': 'Asignar curso y jornada'},
    ]

    for p_info in pasos_iniciales:
        # Buscamos el paso en el catálogo de Proceso_matricula
        # Se usa Q para buscar coincidencias parciales tanto en el nombre oficial como en palabras clave
        paso_obj = Proceso_matricula.objects.filter(
            Q(nombre_paso__icontains=p_info['nombre']) | Q(nombre_paso__icontains=p_info['key']),
            activo=True
        ).first()

        if paso_obj:
            # get_or_create asegura que no dupliquemos si por alguna razón ya existía
            Seguimiento_matricula.objects.get_or_create(
                matricula=instance,
                paso=paso_obj,
                defaults={
                    'estado': 'completado',
                    'fecha_completado': timezone.now(),
                    'observacion': 'Completado automáticamente por el sistema al finalizar el registro integral.'
                }
            )



# ================================================================================
# SIGNAL: GESTIÓN DE CUPO AL RETIRAR ESTUDIANTE
# ================================================================================
# Cuándo se ejecuta: Después de actualizar una Matrícula (UPDATE, no INSERT)
# Por qué: Si la matrícula pasa de activa (True) a inactiva (False), significa
# que el estudiante se retiró y debemos devolver el cupo al curso.
# ================================================================================

@receiver(post_save, sender=Matricula)
def gestionar_cupo_retiro(sender, instance, created, **kwargs):
    """
    Al desactivar una matrícula (retiro del estudiante), incrementamos
    el cupo disponible del curso. Solo actúa cuando el estado cambia
    de True a False (no en cada guardado).
    """
    # No actuar en creaciones nuevas (eso lo maneja crear_seguimientos_iniciales)
    if created:
        return

    # Solo actuar si el estado cambió de True a False (retiro)
    estado_anterior = getattr(instance, '_estado_anterior', None)
    if estado_anterior is True and instance.estado is False:
        if instance.curso:
            instance.curso.cupo_disponible += 1
            instance.curso.save(update_fields=['cupo_disponible'])

    # Actualizar el estado anterior para futuras comparaciones
    instance._estado_anterior = instance.estado


# ================================================================================



# ── TABLA PASOS PROCESO MATRICULA ────────────────────────────────
class Proceso_matricula(models.Model):
    nombre_paso = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True) 
    orden       = models.IntegerField()
    obligatorio = models.BooleanField(default=True)
    activo      = models.BooleanField(default=True)
    icono       = models.CharField(max_length=50, null=True, blank=True)
    color       = models.CharField(max_length=20, default='#3B82F6')


    class Meta:
        db_table = 'procesos_matricula'
        verbose_name = 'Proceso de Matrícula'
        verbose_name_plural = 'Procesos de Matrícula'

    def __str__(self):
        return self.nombre_paso or "Sin nombre"


# ── TABLA SEGUIMIENTO DE MATRICULA ───────────────────────────────
class Seguimiento_matricula(models.Model):
    matricula         = models.ForeignKey('Matricula', on_delete=models.SET_NULL, null=True, blank=True)
    paso              = models.ForeignKey('Proceso_matricula', on_delete=models.SET_NULL, null=True, blank=True) 
    usuario_actualiza = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    estado            = models.CharField(
                            max_length=30,
                            choices=[
                                ('pendiente',  'Pendiente'),
                                ('en_proceso', 'En Proceso'),
                                ('completado', 'Completado'),
                                ('rechazado',  'Rechazado')
                            ],
                            default='pendiente'
                        )
    fecha_inicio        = models.DateTimeField(auto_now_add=True)
    fecha_completado    = models.DateTimeField(null=True, blank=True) 
    observacion         = models.TextField(null=True, blank=True)      
    fecha_actualizacion = models.DateTimeField(auto_now=True)          

    class Meta:
        db_table = 'seguimientos_matricula'
        verbose_name = 'Seguimiento de Matrícula'
        verbose_name_plural = 'Seguimientos de Matrícula'

    def __str__(self):
        return f"{self.matricula} - {self.paso} - {self.estado}"


# ── TABLA DE TIPO DE DOCUMENTOS ──────────────────────────────────
class Tipo_documento(models.Model):
    descripcion = models.CharField(max_length=50, null=True, blank=True)
    sigla = models.CharField(max_length=20, unique=True, blank=True, null=True)

    class Meta:
        db_table = 'tipos_documento'
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documentos'

    def __str__(self):
        return self.descripcion or "Sin descripción"


# ── TIPOS DE DOCUMENTOS PARA MATRICULA ───────────────────────────
class Tipo_documento_matricula(models.Model):
    descripcion = models.CharField(max_length=100, null=True, blank=True)
    obligatorio = models.BooleanField(default=False)

    class Meta:
        db_table = 'tipos_documento_matricula'
        verbose_name = 'Tipo de Documento Matrícula'
        verbose_name_plural = 'Tipos de Documentos Matrícula'

    def __str__(self):
        return self.descripcion or "Sin descripción"


# ── TABLA TRAZABILIDAD ───────────────────────────────────────────
class Trazabilidad(models.Model):
    usuario     = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    accion      = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)  
    fecha_hora  = models.DateTimeField(auto_now_add=True)
    ip_origen   = models.CharField(max_length=50, null=True, blank=True)
    dispositivo = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'trazabilidad'
        verbose_name = 'Trazabilidad'
        verbose_name_plural = 'Trazabilidades'

    def __str__(self):
        return f"{self.usuario} - {self.accion}" if self.accion else "Sin acción"


# ── TABLA DE USUARIOS ────────────────────────────────────────────
class Usuario(AbstractUser):
    perfil          = models.ForeignKey('Perfil', on_delete=models.SET_NULL, null=True, blank=True)
    tipo_documento  = models.ForeignKey('Tipo_documento', on_delete=models.SET_NULL, null=True, blank=True)

    telefono        = models.CharField(max_length=15, null=True, blank=True)
    num_documento   = models.CharField(max_length=20, null=True, blank=True)
    token_reset     = models.CharField(max_length=255, null=True, blank=True)
    fecha_solicitud = models.DateField(null=True, blank=True)
    token_bloqueado = models.BooleanField(default=True)
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='usuarios_set'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='usuarios_set'
    )

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.get_full_name() or self.username or "Sin nombre"
    

def Ruta_Foto_Usuario(instance, filename):
    return f'Usuario/id_{instance.usuario.id}/{filename}'

class Foto_Usuario(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='fotos')
    archivo = models.ImageField(upload_to=Ruta_Foto_Usuario)
    ruta_disco = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'fotos_usuarios'
        verbose_name = 'Foto de Usuario'
        verbose_name_plural = 'Fotos de Usuarios'

    def __str__(self):
        return f"Foto de {self.usuario.get_full_name() or self.usuario.username} - ID: {self.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.archivo and not self.ruta_disco:
            self.ruta_disco = self.archivo.path
            super().save(update_fields=['ruta_disco'])