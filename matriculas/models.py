from django.db import models
from django.db.models import Q


# ── TIPO DE DOCUMENTOS PARA MATRÍCULA ────────────────────────────
class Tipo_documento_matricula(models.Model):
    id_tipo_documento_matricula = models.BigAutoField(primary_key=True)
    descripcion = models.CharField(max_length=100, null=True, blank=True)
    obligatorio = models.BooleanField(default=False)

    class Meta:
        db_table = 'tipos_documento_matricula'
        managed  = True

    def __str__(self):
        return self.descripcion or "Sin descripción"


# ── TABLA DE MATRÍCULAS ──────────────────────────────────────────
class Matricula(models.Model):
    id_matricula    = models.BigAutoField(primary_key=True)
    estudiante      = models.ForeignKey('academico.Estudiante', on_delete=models.SET_NULL, null=True, blank=True)
    acudiente       = models.ForeignKey('academico.Acudiente',  on_delete=models.SET_NULL, null=True, blank=True)
    curso           = models.ForeignKey('academico.Curso',      on_delete=models.SET_NULL, null=True, blank=True)
    jornada         = models.ForeignKey('academico.Jornada',    on_delete=models.SET_NULL, null=True, blank=True)
    year_lectivo    = models.IntegerField()
    fecha_matricula = models.DateField(auto_now_add=True)
    fecha_inicio    = models.DateField(null=True, blank=True)
    estado          = models.BooleanField(default=True)
    observaciones   = models.TextField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._estado_anterior = self.estado if self.pk else None

    class Meta:
        db_table = 'MAT_Matriculas'
        managed  = True

    def __str__(self):
        return f"{self.estudiante} - {self.year_lectivo}" if self.year_lectivo else "Sin datos"


# ── TABLA PASOS PROCESO MATRÍCULA ────────────────────────────────
class Proceso_matricula(models.Model):
    id_proceso_matricula = models.BigAutoField(primary_key=True)
    nombre_paso = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    orden       = models.IntegerField()
    obligatorio = models.BooleanField(default=True)
    activo      = models.BooleanField(default=True)
    icono       = models.CharField(max_length=50, null=True, blank=True)
    color       = models.CharField(max_length=20, default='#3B82F6')

    class Meta:
        db_table = 'PRCM_Matricula'
        managed  = True

    def __str__(self):
        return self.nombre_paso or "Sin nombre"


# ── TABLA SEGUIMIENTO DE MATRÍCULA ───────────────────────────────
class Seguimiento_matricula(models.Model):
    id_seguimiento_matricula = models.BigAutoField(primary_key=True)
    matricula         = models.ForeignKey('Matricula',        on_delete=models.SET_NULL, null=True, blank=True)
    paso              = models.ForeignKey('Proceso_matricula', on_delete=models.SET_NULL, null=True, blank=True)
    usuario_actualiza = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    estado            = models.CharField(
                            max_length=30,
                            choices=[
                                ('pendiente',  'Pendiente'),
                                ('en_proceso', 'En Proceso'),
                                ('completado', 'Completado'),
                                ('rechazado',  'Rechazado'),
                            ],
                            default='pendiente'
                        )
    fecha_inicio        = models.DateTimeField(auto_now_add=True)
    fecha_completado    = models.DateTimeField(null=True, blank=True)
    observacion         = models.TextField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'MAT_Seguimientos_Matricula'
        managed  = True

    def __str__(self):
        return f"{self.matricula} - {self.paso} - {self.estado}"


# ── TABLA DOCUMENTOS DE MATRÍCULA ────────────────────────────────
class Documento_matricula(models.Model):
    id_documento_matricula   = models.BigAutoField(primary_key=True)
    matricula                = models.ForeignKey('Matricula',               on_delete=models.SET_NULL, null=True, blank=True)
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
                                        ('Rechazado', 'Rechazado'),
                                    ],
                                    default='Pendiente'
                                )
    observacion    = models.TextField(null=True, blank=True)
    usuario_carga  = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='cargas')
    usuario_revisa = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='revisiones')
    fecha_revision = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'MAT_Documentos_Matricula'
        managed  = True

    def __str__(self):
        return self.nombre_archivo or "Sin nombre"

# ─────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE MES DE INGRESO
# ─────────────────────────────────────────────────────────────────
class ConfiguracionMesIngreso(models.Model):
    MESES = [
        (1, 'Enero'),
        (2, 'Febrero'),
        (3, 'Marzo'),
        (4, 'Abril'),
        (5, 'Mayo'),
        (6, 'Junio'),
        (7, 'Julio'),
        (8, 'Agosto'),
        (9, 'Septiembre'),
        (10, 'Octubre'),
        (11, 'Noviembre'),
        (12, 'Diciembre'),
    ]
    id_config        = models.BigAutoField(primary_key=True)
    mes              = models.IntegerField(choices=MESES)
    year_lectivo     = models.IntegerField()
    fecha_inicio     = models.DateField()
    activo           = models.BooleanField(default=True)
    
    class Meta:
        db_table        = 'MAT_Configuracion_Mes_Ingreso'
        managed         = True
        unique_together = [('mes', 'year_lectivo')]
        verbose_name    = 'Configuración Mes de Ingreso'
        verbose_name_plural = 'Configuraciones Meses de Ingreso'

    def __str__(self):
        return f"{self.get_mes_display()} {self.year_lectivo} - Inicia: {self.fecha_inicio.strftime('%d/%m/%Y')}"
