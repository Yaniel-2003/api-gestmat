from django.db import models


# ── TABLA MÉTODO DE PAGO ─────────────────────────────────────────
class Metodo_pago(models.Model):
    id_metodo_pago = models.BigAutoField(primary_key=True)
    nombre         = models.CharField(max_length=255, null=True, blank=True)
    descripcion    = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'metodos_pago'
        managed  = True

    def __str__(self):
        return self.nombre or "Sin nombre"


# ── TABLA TARIFAS DE MATRÍCULA ───────────────────────────────────
class TarifaMatricula(models.Model):
    curso        = models.ForeignKey('academico.Curso', on_delete=models.CASCADE, related_name='tarifas')
    year_lectivo = models.IntegerField()
    valor        = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion  = models.TextField(null=True, blank=True)
    activo       = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'PAG_Tarifas_Matricula'
        managed         = True
        unique_together = [('curso', 'year_lectivo')]

    def __str__(self):
        return f"{self.curso} — {self.year_lectivo}: ${self.valor:,.0f}"


# ── TABLA DE PAGOS ───────────────────────────────────────────────
class Pago(models.Model):
    matricula   = models.ForeignKey('matriculas.Matricula', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_pago  = models.DateTimeField(auto_now_add=True)
    valor_pago  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    metodo_pago = models.ForeignKey('Metodo_pago', on_delete=models.SET_NULL, null=True, blank=True)
    estado_pago = models.CharField(
                    max_length=50,
                    choices=[
                        ('pendiente',  'Pendiente de Pago'),
                        ('confirmado', 'Pago Confirmado'),
                        ('rechazado',  'Pago Rechazado'),
                        ('error',      'Error en Transacción'),
                    ],
                    default='pendiente'
                  )

    class Meta:
        db_table = 'PAG_Pagos'
        managed  = True

    def __str__(self):
        return f"{self.matricula} - {self.fecha_pago}"
