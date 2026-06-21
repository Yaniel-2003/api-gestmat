from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ['get_avatar_badge', 'username', 'get_nombre_completo',
                     'email', 'get_perfil_badge', 'telefono', 'get_estado_badge']
    list_filter   = ['is_active', 'is_staff', 'perfil']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'num_documento']
    ordering      = ['-date_joined']
    list_per_page = 20

    fieldsets = (
        ('Credenciales de Acceso', {
            'fields': ('username', 'password'),
            'classes': ('wide',),
        }),
        ('Información Personal', {
            'fields': (
                ('first_name', 'last_name'),
                'email',
                'telefono',
                ('tipo_documento', 'num_documento'),
            ),
            'classes': ('wide',),
        }),
        ('Rol y Permisos', {
            'fields': (
                'perfil',
                ('is_active', 'is_staff', 'is_superuser'),
                'groups',
                'user_permissions',
            ),
            'classes': ('wide',),
        }),
        ('Fechas Importantes', {
            'fields': (('last_login', 'date_joined'),),
            'classes': ('wide', 'collapse'),
        }),
        ('Token de Restablecimiento', {
            'fields': ('token_reset', 'fecha_solicitud', 'token_bloqueado'),
            'classes': ('wide', 'collapse'),
        }),
    )

    add_fieldsets = (
        ('Crear Nuevo Usuario', {
            'classes': ('wide',),
            'fields': (
                'username',
                ('first_name', 'last_name'),
                'email',
                'telefono',
                ('tipo_documento', 'num_documento'),
                'perfil',
                ('password1', 'password2'),
            ),
        }),
    )

    readonly_fields = ['last_login', 'date_joined']

    @admin.display(description='')
    def get_avatar_badge(self, obj):
        initials = ''
        if obj.first_name:
            initials += obj.first_name[0].upper()
        if obj.last_name:
            initials += obj.last_name[0].upper()
        if not initials:
            initials = (obj.username[0].upper() if obj.username else '?')
        color = '#7c3aed' if obj.is_superuser else ('#0ea5e9' if obj.is_staff else '#64748b')
        return format_html(
            '<div style="width:34px;height:34px;border-radius:50%;background:{};'
            'color:#fff;display:inline-flex;align-items:center;justify-content:center;'
            'font-weight:700;font-size:13px;">{}</div>',
            color, initials
        )

    @admin.display(description='Nombre completo')
    def get_nombre_completo(self, obj):
        return obj.get_full_name() or '—'

    @admin.display(description='Perfil')
    def get_perfil_badge(self, obj):
        if not obj.perfil:
            return mark_safe('<span style="color:#94a3b8;">Sin perfil</span>')
        colors = {
            'admin': '#7c3aed', 'secretaria': '#0284c7',
            'rector': '#b45309', 'docente': '#059669',
        }
        key   = (obj.perfil.nombre_perfil or '').lower()
        color = next((v for k, v in colors.items() if k in key), '#475569')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:20px;'
            'font-size:11px;font-weight:600;">{}</span>',
            color, obj.perfil.nombre_perfil
        )

    @admin.display(description='Estado')
    def get_estado_badge(self, obj):
        if obj.is_active:
            return mark_safe(
                '<span style="background:#dcfce7;color:#166534;padding:2px 10px;'
                'border-radius:20px;font-size:11px;font-weight:600;">Activo</span>'
            )
        return mark_safe(
            '<span style="background:#fee2e2;color:#991b1b;padding:2px 10px;'
            'border-radius:20px;font-size:11px;font-weight:600;">Inactivo</span>'
        )


admin.site.site_header  = "GestMat — Gestión de Matrículas"
admin.site.site_title   = "GestMat Admin"
admin.site.index_title  = "Panel de Administración"
