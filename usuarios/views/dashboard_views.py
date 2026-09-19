from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
import datetime
import csv
from django.http import HttpResponse

from matriculas.models import Matricula, Documento_matricula
from pagos.models import Pago
from academico.models import Curso, Estudiante, Acudiente
from ..models import Trazabilidad
from backend.permissions import PermisoPorPerfil


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]

    def get(self, request):
        total_activas = Matricula.objects.filter(estado=True).count()
        total_inactivas = Matricula.objects.filter(estado=False).count()

        ingresos_confirmados = Pago.objects.filter(estado_pago='confirmado').aggregate(total=Sum('valor_pago'))['total'] or 0
        ingresos_pendientes = Pago.objects.filter(estado_pago='pendiente').aggregate(total=Sum('valor_pago'))['total'] or 0

        total_estudiantes = Estudiante.objects.count()

        cupos_start = Curso.objects.aggregate(
            totales=Sum('cupo_total'),
            disponibles=Sum('cupo_disponible')
        )

        cupos_totales = cupos_start['totales'] or 0
        cupos_disponibles = cupos_start['disponibles'] or 0
        cupos_ocupados = max(0, cupos_totales - cupos_disponibles)

        kpis = {
            'matriculas_activas': total_activas,
            'matriculas_inactivas': total_inactivas,
            'ingresos_confirmados': float(ingresos_confirmados),
            'ingresos_pendientes': float(ingresos_pendientes),
            'total_estudiantes': total_estudiantes,
            'cupos_totales': cupos_totales,
            'cupos_disponibles': cupos_disponibles,
            'cupos_ocupados': cupos_ocupados
        } 

        # Alumnos por curso 
        matriculas_por_cursos = []
        cursos = Curso.objects.filter(activo=True)

        for curso in cursos:
            count = Matricula.objects.filter(curso=curso, estado=True).count()
            porcentaje = 0

            if curso.cupo_total > 0:
                porcentaje = round(((curso.cupo_total - curso.cupo_disponible) / curso.cupo_total) * 100, 1)

            matriculas_por_cursos.append({
                'id_curso': curso.id_curso,
                'nombre_curso': f"{curso.nombre_curso} - Grado {curso.grado}",
                'matriculados': count,
                'cupo_total': curso.cupo_total,
                'cupo_disponible': curso.cupo_disponible,
                'porcentaje_ocupacion': porcentaje
            })

        # Tendencia de matriculas por tiempo
        por_anio = Matricula.objects.values('year_lectivo').annotate(cantidad=Count('id_matricula')).order_by('-year_lectivo')

        hace_un_anio = timezone.now().date() - datetime.timedelta(days=365)
        por_mes = (
            Matricula.objects.filter(fecha_matricula__gte=hace_un_anio)
            .annotate(mes=TruncMonth('fecha_matricula'))
            .values('mes')
            .annotate(cantidad=Count('id_matricula'))
            .order_by('mes')
        )
        tendencia_mes = []
        for item in por_mes:
            if item['mes']:
                tendencia_mes.append({
                    'fecha': item['mes'].strftime('%Y-%m'),
                    'cantidad': item['cantidad']
                })
        
        hace_30_dias = timezone.now().date() - datetime.timedelta(days=30)
        por_dia = (
            Matricula.objects.filter(fecha_matricula__gte=hace_30_dias)
            .annotate(dia=TruncDay('fecha_matricula'))
            .values('dia')
            .annotate(cantidad=Count('id_matricula'))
            .order_by('dia')
        )
        tendencia_dia = []
        for item in por_dia:
            if item['dia']:
                tendencia_dia.append({
                    'fecha': item['dia'].strftime('%Y-%m-%d'),
                    'cantidad': item['cantidad']
                })

        pagos_metodos = (
            Pago.objects.filter(estado_pago='confirmado')
            .values('metodo_pago__nombre')
            .annotate(cantidad=Count('id'), total=Sum('valor_pago'))
            .order_by('-total')
        )

        distribucion_pago = []
        for item in pagos_metodos:
            distribucion_pago.append({
                'metodo': item['metodo_pago__nombre'] or 'Desconocido',
                'cantidad': item['cantidad'],
                'total': float(item['total'] or 0)
            })

        docs_estados = (
            Documento_matricula.objects.values('estado')
            .annotate(cantidad=Count('id_documento_matricula'))
        )
        documento_start = {item['estado']: item['cantidad'] for item in docs_estados}

        alerta_cupos = []
        cupos_bajos = Curso.objects.filter(activo=True, cupo_disponible__lte=3).order_by('cupo_disponible')
        for c in cupos_bajos:
            alerta_cupos.append({
                'nombre_curso': f"{c.nombre_curso} - Grado {c.grado}",
                'cupo_disponible': c.cupo_disponible,
                'cupo_total': c.cupo_total
            })

        activdad_reciente = []
        logs = Trazabilidad.objects.select_related('usuario').order_by('-fecha_hora')[:5]

        for log in logs:
            activdad_reciente.append({
                'usuario': log.usuario.username if log.usuario else 'Sistema',
                'accion': log.accion,
                'descripcion': log.descripcion,
                'fecha': log.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
            })

        data = {
            'kpis': kpis,
            'matriculas_por_cursos': matriculas_por_cursos,
            'tendencias': {
                'por_anio': list(por_anio),
                'por_mes': tendencia_mes,
                'por_dia': tendencia_dia
            },
            'distribucion_pagos': distribucion_pago,
            'docuementos': documento_start,
            'alert_cupos': alerta_cupos,
            'actividad_reciente': activdad_reciente
        }

        return Response(data, status=status.HTTP_200_OK)
        


class DashboardExportView(APIView):
    permission_classes = [IsAuthenticated, PermisoPorPerfil]

    def get(self, request):
        query = request.query_params
        tipo_reporte = query.get('tipo_reporte', 'matriculas')
        year = query.get('year_lectivo')
        curso_id = query.get('curso_id')
        fecha_inicio = query.get('fecha_inicio')
        fecha_fin = query.get('fecha_fin')

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response.write(u'\ufeff'.encode('utf8'))

        if tipo_reporte == 'matriculas':
            response['Content-Disposition'] = 'attachment; filename="reporte_matriculas.csv"'
            writer = csv.writer(response, delimiter=';')
            writer.writerow(['ID Matrícula', 'Estudiante', 'Tipo Documento', 'Documento Estudiante',
                             'Acudiente', 'Curso', 'Jornada', 'Año Lectivo', 'Fecha Matrícula', 'Estado'])
            
            qs = Matricula.objects.select_related('estudiante__tipo_documento', 'acudiente', 'curso', 'jornada').all()

            if year:
                qs = qs.filter(year_lectivo=year)
            if curso_id:
                qs = qs.filter(curso_id=curso_id)
            if fecha_inicio:
                qs = qs.filter(fecha_matricula__gte=fecha_inicio)
            if fecha_fin:
                qs = qs.filter(fecha_matricula__lte=fecha_fin)

            for m in qs:
                writer.writerow([
                    m.id_matricula,
                    m.estudiante.nombre_completo if m.estudiante else '',
                    m.estudiante.tipo_documento.sigla if m.estudiante and m.estudiante.tipo_documento else '',
                    m.estudiante.numero_documento if m.estudiante else '',
                    m.acudiente.nombre_completo if m.acudiente else '',
                    f"{m.curso.nombre_curso} - Grado {m.curso.grado}" if m.curso else '',
                    m.jornada.nombre_jornada if m.jornada else '',
                    m.year_lectivo,
                    m.fecha_matricula.strftime('%Y-%m-%d') if m.fecha_matricula else '',
                    'Activo' if m.estado else 'Inactivo'
                ])
        elif tipo_reporte == 'pagos':
            response['Content-Disposition'] = 'attachment; filename="reporte_pagos.csv"'
            writer = csv.writer(response, delimiter=';')
            writer.writerow(['ID Pago', 'Estudiante', 'Curso', 'Fecha Pago', 'Valor Pago', 'Método Pago', 'Estado Pago'])

            qs = Pago.objects.select_related('matricula__estudiante', 'matricula__curso', 'metodo_pago').all()

            if curso_id:
                qs = qs.filter(matricula__curso_id=curso_id)
            if fecha_inicio:
                qs = qs.filter(fecha_pago__date__gte=fecha_inicio)
            if fecha_fin:
                qs = qs.filter(fecha_pago__date__lte=fecha_fin)

            for p in qs:
                writer.writerow([
                    p.pk,
                    p.matricula.estudiante.nombre_completo if p.matricula and p.matricula.estudiante else '',
                    f"{p.matricula.curso.nombre_curso} - Grado {p.matricula.curso.grado}" if p.matricula and p.matricula.curso else '',
                    p.fecha_pago.strftime('%Y-%m-%d %H:%M:%S') if p.fecha_pago else '',
                    p.valor_pago,
                    p.metodo_pago.nombre if p.metodo_pago else '',
                    p.get_estado_pago_display() if hasattr(p, 'get_estado_pago_display') else p.estado_pago
                ])

        elif tipo_reporte == 'cupos':
            response['Content-Disposition'] = 'attachment; filename="reporte_cupos.csv"'
            writer = csv.writer(response, delimiter=';')
            writer.writerow(['ID Curso', 'Curso', 'Jornada', 'Cupos Totales', 'Cupos Disponibles', 'Cupos Ocupados', 'Estado'])

            qs = Curso.objects.select_related('jornada').all()
            if curso_id:
                qs = qs.filter(id_curso=curso_id)
            
            for c in qs:
                ocupados = max(0, c.cupo_total - c.cupo_disponible)
                writer.writerow([
                    c.id_curso,
                    f"{c.nombre_curso} - Grado {c.grado}",
                    c.jornada.nombre_jornada if c.jornada else '',
                    c.cupo_total,
                    c.cupo_disponible,
                    ocupados,
                    'Activo' if c.activo else 'Inactivo'
                ])
        else:
            return Response({'error': 'Tipo de reporte no valido'}, status=status.HTTP_400_BAD_REQUEST)
        return response