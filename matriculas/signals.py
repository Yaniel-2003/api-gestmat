from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Q


@receiver(post_save, sender='matriculas.Matricula')
def crear_seguimientos_iniciales(sender, instance, created, **kwargs):
    """Al crear una matrícula, descuenta cupo y marca pasos iniciales como completados."""
    if not created:
        return
    from matriculas.models import Proceso_matricula, Seguimiento_matricula
    from academico.models import Curso

    if instance.curso and instance.curso.cupo_disponible > 0:
        instance.curso.cupo_disponible -= 1
        instance.curso.save(update_fields=['cupo_disponible'])

    pasos_iniciales = [
        {'key': 'estudiante', 'nombre': 'Registrar estudiante'},
        {'key': 'acudiente',  'nombre': 'Asignar acudiente'},
        {'key': 'curso',      'nombre': 'Asignar curso y jornada'},
    ]
    for p_info in pasos_iniciales:
        paso_obj = Proceso_matricula.objects.filter(
            Q(nombre_paso__icontains=p_info['nombre']) | Q(nombre_paso__icontains=p_info['key']),
            activo=True
        ).first()
        if paso_obj:
            Seguimiento_matricula.objects.get_or_create(
                matricula=instance,
                paso=paso_obj,
                defaults={
                    'estado': 'completado',
                    'fecha_completado': timezone.now(),
                    'observacion': 'Completado automáticamente por el sistema al finalizar el registro integral.',
                }
            )


@receiver(post_save, sender='matriculas.Matricula')
def gestionar_cupo_retiro(sender, instance, created, **kwargs):
    """Al desactivar una matrícula, devuelve el cupo al curso."""
    if created:
        return
    estado_anterior = getattr(instance, '_estado_anterior', None)
    if estado_anterior is True and instance.estado is False:
        if instance.curso:
            instance.curso.cupo_disponible += 1
            instance.curso.save(update_fields=['cupo_disponible'])
    instance._estado_anterior = instance.estado

@receiver(pre_save, sender='matriculas.Matricula')
def asignar_fecha_inicio_por_mes(sender, instance, **kwargs):
    """Antes de crear la matrícula, asigna la fecha de inicio según la configuración del mes."""
    if not instance.pk:  # Solo al crear
        current_month = timezone.now().month
        current_year = instance.year_lectivo or timezone.now().year
        from matriculas.models import ConfiguracionMesIngreso
        config = ConfiguracionMesIngreso.objects.filter(
            mes=current_month, 
            year_lectivo=current_year, 
            activo=True
        ).first()
        if config:
            instance.fecha_inicio = config.fecha_inicio
