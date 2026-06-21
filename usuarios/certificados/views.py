from io import BytesIO
from datetime import date

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from matriculas.models import Matricula


class CertificadoMatriculaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id is None:
            raise Http404("Debe proveer id en la URL")

        matricula = get_object_or_404(
            Matricula.objects.select_related(
                "estudiante",
                "acudiente",
                "curso",
                "jornada",
                "estudiante__tipo_documento",
                "acudiente__tipo_documento",
            ),
            pk=id,
        )

        if hasattr(request.user, "perfil") and request.user.perfil.nombre_perfil != "Administrador":
            if matricula.acudiente is None or matricula.acudiente.usuario != request.user:
                raise Http404("No tienes permisos para ver este certificado")

        buffer = _generar_pdf(matricula)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f"certificado_matricula_{id}.pdf",
            content_type="application/pdf",
        )


# ── PDF ───────────────────────────────────────────────────────────────────────

def _generar_pdf(matricula) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    MARGIN_X = 2.5 * cm
    COL2_X   = width / 2 + 0.3 * cm
    LH       = 0.58 * cm

    # Settings
    nombre_colegio    = getattr(settings, "COLOMBO_GIMNASIO",            "Colegio Colombo Gimnasio")
    direccion_colegio = getattr(settings, "COLOMBO_GIMNASIO_DIRECCION",  "Bogotá D.C., Colombia")
    telefono_colegio  = getattr(settings, "COLOMBO_GIMNASIO_TELEFONO",   "(601) 123-4567")
    resolucion        = getattr(settings, "COLOMBO_GIMNASIO_RESOLUCION", "N° 0000")
    nit               = getattr(settings, "COLOMBO_GIMNASIO_NIT",        "000.000.000-0")

    # Datos del modelo — exactamente los del código original
    est     = matricula.estudiante
    acud    = matricula.acudiente
    curso   = matricula.curso
    jornada = matricula.jornada

    tipo_doc_est   = est.tipo_documento.descripcion  if est  and est.tipo_documento  else "—"
    tipo_doc_acud  = acud.tipo_documento.descripcion if acud and acud.tipo_documento else "—"
    estado_text    = "ACTIVO" if matricula.estado else "INACTIVO"

    def _fmt_fecha(valor):
        return valor.strftime("%d/%m/%Y") if hasattr(valor, "strftime") else str(valor)

    hoy     = date.today().strftime("%d de %B de %Y")
    hoy_iso = date.today().strftime("%Y-%m-%d")

    # ── Helpers ──────────────────────────────────────────────────────

    y = 0

    def _header(titulo):
        nonlocal y
        y = height - 2.2 * cm

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawCentredString(width / 2, y, "REPÚBLICA DE COLOMBIA")
        y -= 0.42 * cm

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, y, nombre_colegio.upper())
        y -= 0.45 * cm

        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawCentredString(width / 2, y, f"Resolución de Aprobación {resolucion}  |  NIT {nit}")
        y -= 0.38 * cm
        c.drawCentredString(width / 2, y, f"{direccion_colegio}  |  Tel: {telefono_colegio}")
        y -= 0.6 * cm

        c.setStrokeColor(colors.black)
        c.setLineWidth(1.8)
        c.line(MARGIN_X, y, width - MARGIN_X, y)
        c.setLineWidth(0.5)
        c.line(MARGIN_X, y - 0.18 * cm, width - MARGIN_X, y - 0.18 * cm)
        y -= 0.9 * cm

        c.setFont("Helvetica-Bold", 15)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, y, titulo)
        y -= 0.9 * cm

    def _section(texto):
        nonlocal y
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(MARGIN_X, y, texto)
        y -= 0.25 * cm
        c.setLineWidth(0.5)
        c.setStrokeColor(colors.HexColor("#888888"))
        c.line(MARGIN_X, y, width - MARGIN_X, y)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        y -= 0.5 * cm

    def _field(x, label, value, label_w=4.2 * cm):
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawString(x, y, label)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawString(x + label_w, y, str(value) if value else "—")

    def _rows(pairs, label_w=4.2 * cm):
        nonlocal y
        for left, right in pairs:
            _field(MARGIN_X, left[0],  left[1],  label_w)
            _field(COL2_X,   right[0], right[1], label_w)
            y -= LH
        y -= 0.5 * cm

    def _firma():
        nonlocal y
        c.setLineWidth(0.8)
        c.setStrokeColor(colors.black)
        c.line(width / 2 - 4 * cm, y, width / 2 + 4 * cm, y)
        y -= 0.42 * cm
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width / 2, y, "RECTOR(A)")
        y -= 0.38 * cm
        c.setFont("Helvetica", 9)
        c.drawCentredString(width / 2, y, nombre_colegio)

    def _pie(pagina, total):
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.HexColor("#999999"))
        c.drawCentredString(
            width / 2, 1.8 * cm,
            f"Página {pagina} de {total}  ·  Generado electrónicamente  ·  {hoy_iso}",
        )
        c.setFillColor(colors.black)

    # ════════════════════════════════════════════════════════════════
    # PÁGINA 1 — CERTIFICADO DE MATRÍCULA
    # ════════════════════════════════════════════════════════════════

    _header("CERTIFICADO DE MATRÍCULA")

    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(width / 2, y,
        f"Año Lectivo {matricula.year_lectivo}  ·  Expedido el {hoy}")
    c.setFillColor(colors.black)
    y -= 0.9 * cm

    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, y,
        "El suscrito Rector del Colegio Colombo Gimnasio, en uso de sus facultades legales,")
    y -= 0.45 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, "CERTIFICA QUE:")
    y -= 0.9 * cm

    nombre_est     = est.nombre_completo.upper()   if est     else "—"
    grado_nombre   = curso.grado                   if curso   else "—"
    curso_nombre   = curso.nombre_curso            if curso   else "—"
    jornada_nombre = jornada.nombre_jornada        if jornada else "—"
    num_doc_est    = est.numero_documento           if est     else "—"

    c.setFont("Helvetica", 10)
    for linea in [
        f"El (La) estudiante  {nombre_est},  identificado(a) con",
        f"{tipo_doc_est} N° {num_doc_est},  se encuentra  MATRICULADO(A)",
        f"en el grado  {grado_nombre},  jornada  {jornada_nombre},",
        f"correspondiente al año lectivo  {matricula.year_lectivo}  de esta institución educativa.",
    ]:
        c.drawCentredString(width / 2, y, linea)
        y -= 0.5 * cm

    y -= 0.7 * cm
    _section("INFORMACIÓN DE MATRÍCULA")

    _rows([
        (("Año lectivo:",      str(matricula.year_lectivo)),  ("Curso:",         curso_nombre)),
        (("Grado:",            grado_nombre),                 ("Jornada:",       jornada_nombre)),
        (("Fecha matrícula:",  _fmt_fecha(matricula.fecha_matricula)), ("Fecha inicio:", _fmt_fecha(matricula.fecha_inicio))),
        (("Estado matrícula:", estado_text),                  ("",               "")),
    ], label_w=3.8 * cm)

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawCentredString(width / 2, y,
        "El presente certificado se expide a solicitud del interesado para los fines que estime convenientes.")
    c.setFillColor(colors.black)
    y -= 2.2 * cm

    _firma()
    _pie(1, 2)
    c.showPage()

    # ════════════════════════════════════════════════════════════════
    # PÁGINA 2 — FICHA ESTUDIANTE Y ACUDIENTE
    # ════════════════════════════════════════════════════════════════

    _header("FICHA DE ESTUDIANTE Y ACUDIENTE")

    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(width / 2, y,
        f"Año Lectivo {matricula.year_lectivo}  ·  Expedido el {hoy}")
    c.setFillColor(colors.black)
    y -= 1.0 * cm

    # Datos estudiante
    fecha_nac_est = _fmt_fecha(est.fecha_nacimiento) if est and est.fecha_nacimiento else "—"

    _section("DATOS PERSONALES DEL ESTUDIANTE")
    _rows([
        (("Nombre completo:",      nombre_est),       ("Fecha de nacimiento:", fecha_nac_est)),
        (("Tipo de documento:",    tipo_doc_est),      ("N° de documento:",     num_doc_est)),
    ])

    # Datos acudiente
    nombre_acud  = acud.nombre_completo   if acud else "—"
    num_doc_acud = acud.numero_documento  if acud else "—"
    telefono_acud = acud.telefono         if acud else "—"

    _section("DATOS DEL ACUDIENTE / RESPONSABLE")
    _rows([
        (("Nombre completo:",    nombre_acud),     ("Tipo de documento:", tipo_doc_acud)),
        (("N° de documento:",    num_doc_acud),    ("Teléfono:",          telefono_acud)),
    ])

    y -= 0.3 * cm
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawCentredString(width / 2, y,
        "El presente certificado se expide a solicitud del interesado para los fines que estime convenientes.")
    c.setFillColor(colors.black)
    y -= 2.2 * cm

    _firma()
    _pie(2, 2)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer