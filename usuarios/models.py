import os
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser


# ── TABLA DE TIPO DE DOCUMENTOS ──────────────────────────────────
class Tipo_documento(models.Model):
    id_tipo_documento = models.BigAutoField(primary_key=True)
    descripcion = models.CharField(max_length=50,  null=True, blank=True)
    sigla       = models.CharField(max_length=20, unique=True, blank=True, null=True)

    class Meta:
        db_table = 'tipos_documento'
        managed  = True

    def __str__(self):
        return self.sigla or self.descripcion or "Sin descripción"


# ── TABLA PERFIL ─────────────────────────────────────────────────
class Perfil(models.Model):
    id_perfil     = models.BigAutoField(primary_key=True)
    nombre_perfil = models.CharField(max_length=50, null=True, blank=True)
    insert_perfil = models.BooleanField(default=False)
    update_perfil = models.BooleanField(default=False)
    delete_perfil = models.BooleanField(default=False)
    view_perfil   = models.BooleanField(default=False)
    estado        = models.BooleanField(default=True)

    class Meta:
        db_table = 'SEC_Perfiles'
        managed  = True

    def __str__(self):
        return self.nombre_perfil or "Sin nombre"


# ── TABLA DE USUARIOS ────────────────────────────────────────────
class Usuario(AbstractUser):
    id_usuario      = models.BigAutoField(primary_key=True)
    perfil          = models.ForeignKey('Perfil',        on_delete=models.SET_NULL, null=True, blank=True)
    tipo_documento  = models.ForeignKey('Tipo_documento', on_delete=models.SET_NULL, null=True, blank=True)
    telefono        = models.CharField(max_length=15,  null=True, blank=True)
    num_documento   = models.CharField(max_length=20,  null=True, blank=True)
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
        db_table = 'SEC_Usuarios'
        managed  = True
        permissions = [
            ("ver_modulo_matriculas", "Puede ver el módulo de Matrículas"),
            ("ver_modulo_gestion_academica", "Puede ver el módulo de Gestión Académica"),
            ("ver_modulo_administracion", "Puede ver el módulo de Administración"),
            ("ver_dashboard_matriculas", "Puede ver el dashboard de Matrículas"),
        ]

    def __str__(self):
        return self.get_full_name() or self.username or "Sin nombre"


def Ruta_Foto_Usuario(instance, filename):
    return f'Usuario/id_{instance.usuario.pk}/{filename}'


class Foto_Usuario(models.Model):
    id_foto_usuario = models.BigAutoField(primary_key=True)
    usuario    = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='fotos')
    archivo    = models.ImageField(upload_to=Ruta_Foto_Usuario)
    ruta_disco = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'SEC_Fotos_Usuarios'
        managed  = True

    def __str__(self):
        return f"Foto de {self.usuario.get_full_name() or self.usuario.username} - ID: {self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.archivo and not self.ruta_disco:
            self.ruta_disco = self.archivo.path
            super().save(update_fields=['ruta_disco'])


# ── TABLA TRAZABILIDAD ───────────────────────────────────────────
class Trazabilidad(models.Model):
    id_trazabilidad = models.BigAutoField(primary_key=True)
    usuario     = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    accion      = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    fecha_hora  = models.DateTimeField(auto_now_add=True)
    ip_origen   = models.CharField(max_length=50,  null=True, blank=True)
    dispositivo = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'AUD_Trazabilidad'
        managed  = True

    def __str__(self):
        return f"{self.usuario} - {self.accion}" if self.accion else "Sin acción"