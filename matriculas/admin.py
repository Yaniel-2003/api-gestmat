from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.shortcuts import render

from .models import Matricula, Proceso_matricula, Seguimiento_matricula, Documento_matricula, Tipo_documento_matricula, ConfiguracionMesIngreso


# ─────────────────────────────────────────────────────────────────
# FORMULARIO PARA ASIGNAR FECHA DE INGRESO
# ─────────────────────────────────────────────────────────────────
class FechaIngresoForm(forms.Form):
    fecha_ingreso = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'max-width: 200px;'}),
        label="Fecha de ingreso",
    )


# ─────────────────────────────────────────────────────────────────
# INLINES
# ─────────────────────────────────────────────────────────────────
class SeguimientoMatriculaInline(admin.TabularInline):
    model           = Seguimiento_matricula
    extra           = 0
    fields          = ['paso', 'get_estado_colored', 'fecha_inicio', 'fecha_completado', 'observacion']
    readonly_fields = ['paso', 'get_estado_colored', 'fecha_inicio', 'fecha_completado']
    can_delete      = False
    verbose_name        = "Seguimiento"
    verbose_name_plural = "Seguimiento del Proceso"
    show_change_link    = True

    @admin.display(description='Estado')
    def get_estado_colored(self, obj):
        colores = {
            'pendiente':  ('#fef9c3', '#854d0e', ''),
            'en_proceso': ('#dbeafe', '#1e40af', ''),
            'completado': ('#dcfce7', '#166534', ''),
            'rechazado':  ('#fee2e2', '#991b1b', ''),
        }
        bg, color, icon = colores.get(obj.estado, ('#f1f5f9', '#475569', '•'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:20px;'
            'font-size:11px;font-weight:600;">{} {}</span>',
            bg, color, icon, obj.get_estado_display()
        )


class DocumentoMatriculaInline(admin.TabularInline):
    model           = Documento_matricula
    extra           = 0
    fields          = ['tipo_documento_matricula', 'nombre_archivo', 'estado', 'fecha_entrega']
    readonly_fields = ['nombre_archivo']
    verbose_name        = "Documento"
    verbose_name_plural = "Documentos de la Matrícula"
    show_change_link    = True


class FechaFiltroFilter(admin.SimpleListFilter):
    title = 'fecha filtro'
    parameter_name = 'fecha_filtro'

    def lookups(self, request, model_admin):
        return ()

    def queryset(self, request, queryset):
        return queryset


# ─────────────────────────────────────────────────────────────────
# MATRÍCULA
# ─────────────────────────────────────────────────────────────────
@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    change_list_template = 'admin/matriculas_change_list.html'
    list_display   = ['id_matricula', 'get_estudiante_link', 'get_curso_badge',
                      'jornada', 'year_lectivo', 'fecha_matricula',
                      'fecha_inicio', 'get_estado_badge']
    list_filter    = ['year_lectivo', 'estado', 'curso', 'jornada', FechaFiltroFilter]
    search_fields  = ['estudiante__nombre_completo', 'acudiente__nombre_completo']
    actions        = ['accion_asignar_fecha_ingreso']
    ordering       = ['-id_matricula']
    inlines        = [SeguimientoMatriculaInline, DocumentoMatriculaInline]

    def get_list_per_page(self, request):
        # Si hay filtros aplicados (ignorando parámetros internos del admin como 'e' o 'p')
        filtros = [k for k in request.GET.keys() if k not in ('e', 'p', 'clear', 'q')]
        if filtros:
            return 35
        return 10000  # Número alto para desactivar la paginación por defecto

    fieldsets = (
        ('Estudiante y Acudiente', {
            'fields': (('estudiante', 'acudiente'),),
            'classes': ('wide',),
        }),
        ('Curso y Jornada', {
            'fields': (('curso', 'jornada'), 'year_lectivo'),
            'classes': ('wide',),
        }),
        ('Fechas y Estado', {
            'fields': (('fecha_matricula', 'fecha_inicio'), 'estado'),
            'classes': ('wide',),
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('wide', 'collapse'),
        }),
    )

    readonly_fields = ['fecha_matricula']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario_carga = request.user
        obj.save()

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si se está editando una matrícula existente
            return self.readonly_fields + ['curso', 'fecha_inicio']
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        fecha = request.GET.get('fecha_filtro')
        if fecha:
            from datetime import datetime
            try:
                fecha_obj = datetime.strptime(fecha, '%d/%m/%Y').date()
                qs = qs.filter(fecha_matricula=fecha_obj)
            except ValueError:
                qs = qs.filter(fecha_matricula=fecha)
        return qs

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['fecha_filtro'] = request.GET.get('fecha_filtro', '')
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description='Estudiante')
    def get_estudiante_link(self, obj):
        if not obj.estudiante:
            return format_html('<span style="color:#94a3b8;">—</span>')
        try:
            url = reverse('admin:academico_estudiante_change', args=[obj.estudiante.pk])
            return format_html('<a href="{}" style="color:#6366f1;font-weight:600;">{}</a>',
                               url, obj.estudiante.nombre_completo or '—')
        except Exception:
            return format_html('<span style="color:#6366f1;font-weight:600;">{}</span>',
                               obj.estudiante.nombre_completo or '—')

    @admin.display(description='Curso')
    def get_curso_badge(self, obj):
        if not obj.curso:
            return mark_safe('<span style="color:#94a3b8;">—</span>')
        return format_html(
            '<span style="background:#ede9fe;color:#5b21b6;padding:2px 10px;'
            'border-radius:20px;font-size:11px;font-weight:600;">{}</span>',
            str(obj.curso)
        )

    @admin.display(description='Estado')
    def get_estado_badge(self, obj):
        if obj.estado:
            return mark_safe('<span style="background:#dcfce7;color:#166534;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;">Activa</span>')
        return mark_safe('<span style="background:#fee2e2;color:#991b1b;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;">Inactiva</span>')

    def accion_asignar_fecha_ingreso(self, request, queryset):
        if 'aplicar' in request.POST:
            form = FechaIngresoForm(request.POST)
            if form.is_valid():
                fecha = form.cleaned_data['fecha_ingreso']
                actualizadas = queryset.update(fecha_inicio=fecha)
                self.message_user(request, f"Fecha de ingreso asignada a {actualizadas} matrícula(s).")
                return
        else:
            form = FechaIngresoForm()
            
        return render(request, 'admin/asignar_fecha_ingreso.html', {
            'matriculas':           queryset,
            'form':                 form,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        })

    accion_asignar_fecha_ingreso.short_description = "Asignar fecha de ingreso a seleccionadas"

# ─────────────────────────────────────────────────────────────────
# CONFIGURACIÓN MES INGRESO
# ─────────────────────────────────────────────────────────────────
@admin.register(ConfiguracionMesIngreso)
class ConfiguracionMesIngresoAdmin(admin.ModelAdmin):
    list_display = ('mes', 'year_lectivo', 'fecha_inicio', 'activo')
    list_filter = ('year_lectivo', 'mes', 'activo')
    search_fields = ('year_lectivo',)
    ordering = ('-year_lectivo', 'mes')
