from django.db import models


# ── TABLA EPS ────────────────────────────────────────────────────
class Eps(models.Model):
    id_eps     = models.BigAutoField(primary_key=True)
    nombre_eps = models.CharField(max_length=100, null=True, blank=True)
    telefono   = models.CharField(max_length=15,  null=True, blank=True)
    direccion  = models.CharField(max_length=50,  null=True, blank=True)

    class Meta:
        db_table = 'eps'
        managed  = True

    def __str__(self):
        return self.nombre_eps or "Sin nombre"


# ── TABLA JORNADA ────────────────────────────────────────────────
class Jornada(models.Model):
    id_jornada     = models.BigAutoField(primary_key=True)
    nombre_jornada = models.CharField(max_length=50, null=True, blank=True)
    hora_inicio    = models.TimeField(null=True, blank=True)
    hora_fin       = models.TimeField(null=True, blank=True)
    descripcion    = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'jornadas'
        managed  = True

    def __str__(self):
        return self.nombre_jornada or "Sin nombre"


# ── TABLA CURSOS ──────────────────────────────────────────────────
class Curso(models.Model):
    id_curso        = models.BigAutoField(primary_key=True)
    jornada         = models.ForeignKey('Jornada', on_delete=models.SET_NULL, null=True, blank=True)
    nombre_curso    = models.CharField(max_length=20, null=True, blank=True)
    grado           = models.CharField(max_length=10, null=True, blank=True)
    activo          = models.BooleanField(default=True)
    cupo_total      = models.IntegerField(default=30)
    cupo_disponible = models.IntegerField(default=30)

    class Meta:
        db_table = 'ACA_Cursos'
        managed  = True

    def __str__(self):
        return f"{self.nombre_curso} - Grado {self.grado}" if self.nombre_curso else "Sin nombre"


# ── TABLA ACUDIENTES ──────────────────────────────────────────────
class Acudiente(models.Model):
    id_acudiente     = models.BigAutoField(primary_key=True)
    tipo_documento   = models.ForeignKey('usuarios.Tipo_documento', on_delete=models.SET_NULL, null=True, blank=True)
    usuario          = models.ForeignKey('usuarios.Usuario',        on_delete=models.SET_NULL, null=True, blank=True)
    numero_documento = models.CharField(max_length=20,  null=True, blank=True)
    nombre_completo  = models.CharField(max_length=100, null=True, blank=True)
    parentesco       = models.CharField(max_length=50,  null=True, blank=True)
    telefono         = models.CharField(max_length=15,  null=True, blank=True)
    email            = models.EmailField(max_length=50, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'ACA_Acudientes'
        managed  = True

    def __str__(self):
        return self.nombre_completo or "Sin nombre"


def Ruta_Foto_Acudientes(instance, filename):
    return f'Acudientes/id_{instance.acudiente.pk}/{filename}'


class Foto_Acudiente(models.Model):
    id_foto_acudiente = models.BigAutoField(primary_key=True)
    acudiente  = models.ForeignKey('Acudiente', on_delete=models.CASCADE, related_name='fotos')
    archivo    = models.ImageField(upload_to=Ruta_Foto_Acudientes)
    ruta_disco = models.CharField(max_length=500, null=True, blank=True)
    fecha      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ACA_Fotos_Acudientes'
        managed  = True

    def __str__(self):
        return f"Foto de {self.acudiente.nombre_completo} - ID: {self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.archivo and not self.ruta_disco:
            self.ruta_disco = self.archivo.path
            super().save(update_fields=['ruta_disco'])


# ── TABLA ESTUDIANTE ─────────────────────────────────────────────
class Estudiante(models.Model):
    id_estudiante    = models.BigAutoField(primary_key=True)
    tipo_documento   = models.ForeignKey('usuarios.Tipo_documento', on_delete=models.SET_NULL, null=True, blank=True)
    eps              = models.ForeignKey('Eps',       on_delete=models.SET_NULL, null=True, blank=True)
    acudientes       = models.ManyToManyField('Acudiente', blank=True)
    numero_documento = models.CharField(max_length=20,  null=True, blank=True)
    nombre_completo  = models.CharField(max_length=100, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'ACA_Estudiantes'
        managed  = True

    def __str__(self):
        return self.nombre_completo or "Sin nombre"


def Ruta_Foto_Estudiante(instance, filename):
    return f'Estudiante/id_{instance.estudiante.pk}/{filename}'


class Foto_Estudiante(models.Model):
    id_foto_estudiante = models.BigAutoField(primary_key=True)
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE, related_name='fotos')
    archivo    = models.ImageField(upload_to=Ruta_Foto_Estudiante)
    ruta_disco = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'ACA_Fotos_Estudiantes'
        managed  = True

    def __str__(self):
        return f"Foto de {self.estudiante.nombre_completo} - ID: {self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.archivo and not self.ruta_disco:
            self.ruta_disco = self.archivo.path
            super().save(update_fields=['ruta_disco'])
