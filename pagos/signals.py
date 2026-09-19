from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender='pagos.Pago')
def crear_seguimiento_desde_pago(sender, instance, created, **kwargs):
    """Al confirmar un pago, marca el paso de pago como completado en el seguimiento."""
    if instance.estado_pago != 'confirmado':
        return
    if not instance.matricula:
        return
    from matriculas.models import Proceso_matricula, Seguimiento_matricula

    paso_pago = Proceso_matricula.objects.filter(
        nombre_paso__icontains='pago',
        activo=True
    ).first()
    if not paso_pago:
        return

    seguimiento, created_seg = Seguimiento_matricula.objects.get_or_create(
        matricula=instance.matricula,
        paso=paso_pago,
        defaults={
            'estado': 'completado',
            'fecha_completado': timezone.now(),
        }
    )
    if not created_seg and seguimiento.estado != 'completado':
        seguimiento.estado = 'completado'
        seguimiento.fecha_completado = timezone.now()
        seguimiento.save(update_fields=['estado', 'fecha_completado'])


@receiver(post_save, sender='pagos.Pago')
def asignar_tarifa_default_pago(sender, instance, created, **kwargs):
    """Al crear un pago sin valor, lo asigna desde la tarifa del curso."""
    if not created:
        return
    if instance.valor_pago is not None:
        return
    if not instance.matricula:
        return
    mat = instance.matricula
    if not mat.curso or not mat.year_lectivo:
        return
    from pagos.models import TarifaMatricula, Pago
    tarifa = TarifaMatricula.objects.filter(
        curso=mat.curso,
        year_lectivo=mat.year_lectivo,
        activo=True
    ).first()
    if tarifa:
        Pago.objects.filter(pk=instance.pk).update(valor_pago=tarifa.valor)
