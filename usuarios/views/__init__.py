# ================================================================================
# ARCHIVO DE EXPORTACIÓN DE VISTAS - USUARIOS APP
# ================================================================================
# Este archivo importa y exporta todas las vistas para que puedan ser usadas
# desde otros módulos (principalmente desde las URLs)
# ================================================================================
# Por qué existe:
# ---------------
# Centraliza las importaciones para que las URLs y otros módulos puedan hacer:
# from usuarios.views import MiViewSet
# En lugar de:
# from usuarios.views.mi_modulo_views import MiViewSet
# ================================================================================

# IMPORTACIÓN DE VISTAS DE AUTENTICACIÓN
from .auth_views import LoginView, LogoutView

# IMPORTACIÓN DE VISTAS DE ACUDIENTES
from .acudiente_views import AcudienteViewSet, fotos_acudiente, eliminar_foto_acudiente

# IMPORTACIÓN DE VISTAS DE CURSOS
from .curso_views import CursoViewSet

# IMPORTACIÓN DE VISTAS DE USUARIOS
from .usuario_views import UsuarioViewSet, fotos_usuario, eliminar_foto_usuario

# IMPORTACIÓN DE VISTAS DE TIPOS DE DOCUMENTO
from .tipoDoc_views import TipoDocumentoViewSet

# IMPORTACIÓN DE VISTAS DE ESTUDIANTES
from .estudiante_views import EstudianteViewSet, fotos_estudiante, eliminar_fotos_estudiante

# IMPORTACIÓN DE VISTAS DE PERFILES
from .perfil_views import PerfilViewSet

# IMPORTACIÓN DE VISTAS DE JORNADAS
from .jornada_view import JornadaViewSet

# IMPORTACIÓN DE VISTAS DE EPS
from .eps_view import EpsView

# IMPORTACIÓN DE VISTAS DE MÉTODOS DE PAGO
from .metodo_pago_view import MetodoPagoView

# IMPORTACIÓN DE VISTAS DE PÁGINAS
from .pagina_view import PaginaView

# IMPORTACIÓN DE VISTAS DE TIPOS DE DOCUMENTO PARA MATRÍCULA
from .tipo_documento_matricula_view import TipoDocumentoMatriculaView

# IMPORTACIÓN DE VISTAS DE DOCUMENTOS DE MATRÍCULA
from .documento_matricula_view import guardar_documento, DocumentoMatriculaViewSet

# IMPORTACIÓN DE VISTAS DE MATRÍCULAS
from .matricula_views import MatriculaViewSet

# IMPORTACIÓN DE VISTAS DE TRAZABILIDAD
from .trazabilidad_views import TrazabilidadViewSet

# IMPORTACIÓN DE VISTAS DE PROCESO DE MATRÍCULA
from .proceso_matricula_view import ProcesoMatriculaViewSet

# ================================================================================
# NUEVA IMPORTACIÓN: SEGUIMIENTO DE MATRÍCULA
# ================================================================================
# Esta importación fue AGREGADA para soportar el nuevo endpoint de seguimiento
# Función: Permitir la creación y actualización de registros de seguimiento
# Uso en URLs: router.register(r'seguimiento_matricula', SeguimientoMatriculaViewSet)
from .seguimiento_matricula_views import SeguimientoMatriculaViewSet

from .pago_views import PagoViewSet

