from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import Pago, TarifaMatricula, Metodo_pago


# ─────────────────────────────────────────────────────────────────
# INLINE DE PAGOS (usado en MatriculaAdmin de matriculas)
# ─────────────────────────────────────────────────────────────────
class PagoInline(admin.TabularInline):
    model           = Pago
    extra           = 0
    fields          = ['valor_pago', 'metodo_pago', 'get_estado_pago_badge', 'fecha_pago']
    readonly_fields = ['get_estado_pago_badge', 'fecha_pago']
    verbose_name        = "Pago"
    verbose_name_plural = "Pagos Registrados"

    @admin.display(description='Estado del Pago')
    def get_estado_pago_badge(self, obj):
        colores = {
            'pendiente':  ('#fef9c3', '#854d0e', ''),
            'confirmado': ('#dcfce7', '#166534', ''),
            'rechazado':  ('#fee2e2', '#991b1b', ''),
            'error':      ('#fce7f3', '#9d174d', ''),
        }
        bg, color, icon = colores.get(obj.estado_pago, ('#f1f5f9', '#475569', '•'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:20px;'
            'font-size:11px;font-weight:600;">{} {}</span>',
            bg, color, icon, obj.get_estado_pago_display()
        )


# ─────────────────────────────────────────────────────────────────
# PAGOS
# ─────────────────────────────────────────────────────────────────
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display    = ['id', 'get_matricula_link', 'get_valor_badge',
                       'metodo_pago', 'get_estado_badge', 'fecha_pago']
    list_filter     = ['estado_pago', 'metodo_pago']
    search_fields   = ['matricula__estudiante__nombre_completo']
    readonly_fields = ['fecha_pago']
    ordering        = ['-fecha_pago']
    list_per_page   = 25

    fieldsets = (
        ('Información del Pago', {
            'fields': (
                'matricula',
                ('valor_pago', 'metodo_pago'),
                'estado_pago',
                'fecha_pago',
            ),
            'classes': ('wide',),
        }),
    )

    @admin.display(description='Matrícula')
    def get_matricula_link(self, obj):
        if not obj.matricula:
            return mark_safe('<span style="color:#94a3b8;">—</span>')
        url = reverse('admin:matriculas_matricula_change', args=[obj.matricula.pk])
        return format_html('<a href="{}" style="color:#6366f1;font-weight:600;">{}</a>',
                           url, str(obj.matricula))

    @admin.display(description='Valor')
    def get_valor_badge(self, obj):
        if obj.valor_pago is None:
            return mark_safe('<span style="color:#94a3b8;">—</span>')
        return format_html('<strong style="color:#166534;">{}</strong>', f"${obj.valor_pago:,.0f}")

    @admin.display(description='Estado')
    def get_estado_badge(self, obj):
        colores = {
            'pendiente':  ('#fef9c3', '#854d0e', ''),
            'confirmado': ('#dcfce7', '#166534', ''),
            'rechazado':  ('#fee2e2', '#991b1b', ''),
            'error':      ('#fce7f3', '#9d174d', ''),
        }
        bg, color, icon = colores.get(obj.estado_pago, ('#f1f5f9', '#475569', '•'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:20px;'
            'font-size:11px;font-weight:600;">{} {}</span>',
            bg, color, icon, obj.get_estado_pago_display()
        )


# ─────────────────────────────────────────────────────────────────
# TARIFAS DE MATRÍCULA
# ─────────────────────────────────────────────────────────────────
@admin.register(TarifaMatricula)
class TarifaMatriculaAdmin(admin.ModelAdmin):
    list_display  = ['curso', 'year_lectivo', 'get_valor_badge', 'get_activo_badge', 'fecha_creacion']
    list_filter   = ['year_lectivo', 'activo', 'curso__jornada']
    search_fields = ['curso__nombre_curso', 'curso__grado']
    ordering      = ['-year_lectivo', 'curso__grado']

    fieldsets = (
        ('Configuración de Tarifa', {
            'fields': (('curso', 'year_lectivo'), 'valor', 'activo', 'descripcion'),
            'classes': ('wide',),
        }),
    )

    @admin.display(description='Valor')
    def get_valor_badge(self, obj):
        return format_html('<strong style="color:#166534;font-size:13px;">{}</strong>', f"${obj.valor:,.0f}")

    @admin.display(description='Activo')
    def get_activo_badge(self, obj):
        if obj.activo:
            return mark_safe('<span style="background:#dcfce7;color:#166534;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;">Activa</span>')
        return mark_safe('<span style="background:#fee2e2;color:#991b1b;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;">Inactiva</span>')
