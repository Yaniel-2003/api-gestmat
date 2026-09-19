from .models import Trazabilidad

def registrar_auditoria(request, accion, objecto_afectado):

    #capturar las ip real
    x_forwarder_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarder_for:
        ip = x_forwarder_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    #crear registro 
    Trazabilidad.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        accion=accion.upper(),
        descripcion=f"El usuario {request.user.username} realizo: {accion} sobre {objecto_afectado}",
        ip_origen=ip,
        dispositivo=request.META.get('HTTP_USER_AGENT', 'Desconocido')[:100]
    )