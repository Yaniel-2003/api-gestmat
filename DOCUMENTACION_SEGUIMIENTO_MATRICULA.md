# 📚 DOCUMENTACIÓN COMPLETA - SEGUIMIENTO DE MATRÍCULA

## 📋 Resumen de cambios

Este documento detalla **todos los cambios realizados** para implementar el sistema de seguimiento de matrícula con validación de orden de pasos y triggers automáticos.

---

## 📁 Archivos modificados

### 1. `usuarios/models.py`
**Función:** Definir la lógica de negocio con signals

**Cambios realizados:**
- ✅ Agregadas importaciones: `post_save`, `receiver`, `timezone`
- ✅ Creado el signal `crear_seguimiento_desde_pago()`
- ✅ El signal se ejecuta automáticamente cuando un `Pago` se guarda con `estado_pago='confirmado'`

**Cómo funciona:**
```
Evento: Django guarda un Pago con estado_pago='confirmado'
  ↓
@receiver(post_save, sender=Pago) se dispara automáticamente
  ↓
Busca el paso de proceso cuyo nombre contiene 'pago'
  ↓
Si no existe un Seguimiento_matricula para esa matricula+paso:
  → Lo crea automáticamente con estado='completado'
Si ya existe:
  → Actualiza su estado a 'completado'
```

**Líneas documentadas:** 292-347

---

### 2. `usuarios/serializers.py`
**Función:** Validar datos y transformar entre JSON ↔ BD

**Cambios realizados:**

#### 2.1 SeguimientoMatriculaListSerializer
- ✅ Serializer de lectura (GET)
- ✅ Expande relaciones: matricula, paso, usuario_actualiza
- ✅ Devuelve todos los campos para visualización

#### 2.2 SeguimientoMatriculaUpdateSerializer
- ✅ Serializer de escritura (POST, PATCH)
- ✅ Campo `usuario_actualiza` es read-only (no viene del frontend)
- ✅ Validador `validate_paso()`: Verifica que el paso esté activo
- ✅ Validador `validate()`: Lógica de negocio completa

**Validaciones que se ejecutan:**
1. **validate_paso()** → El paso debe estar activo en el catálogo
2. **validate()** → Executa 3 validaciones:
   - Existencia de campos requeridos (matricula, paso)
   - Prevención de duplicados (no crear dos seguimientos iguales)
   - Validación de orden (paso anterior debe estar completado)

**Líneas documentadas:** 473-570

---

### 3. `usuarios/views/seguimiento_matricula_views.py`
**Función:** Manejar requests HTTP para CRUD de seguimiento

**Cambios realizados:**

#### 3.1 ProgresoEstudianteViewSet
- ✅ Lista todos los pasos de proceso con estado actual
- ✅ Override del método `list()` para pasar matricula_id al serializer

#### 3.2 SeguimientoMatriculaViewSet (NUEVO)
- ✅ ViewSet para crear/actualizar seguimientos
- ✅ Métodos HTTP permitidos: GET, POST, PATCH
- ✅ DELETE no permitido (http_method_names)

**Métodos principales:**

1. **get_serializer_class():**
   - Si action ∈ [create, update, partial_update] → SeguimientoMatriculaUpdateSerializer (con validaciones)
   - Si action ∈ [list, retrieve] → SeguimientoMatriculaListSerializer (con relaciones expandidas)

2. **get_queryset():**
   - Soporta filtros opcionales: ?matricula_id=1&paso_id=3
   - Usa select_related() para evitar N+1 queries

3. **perform_create():**
   - Asigna automáticamente usuario_actualiza = request.user
   - Si estado='completado', calcula fecha_completado = timezone.now()

4. **perform_update():**
   - Igual a perform_create() pero para PATCH/PUT

**Líneas documentadas:** 14-137

---

### 4. `usuarios/views/proceso_matricula_view.py`
**Función:** Listar pasos de proceso con estado dinámico

**Cambios realizados:**

#### Método override list()
- ✅ Extrae el parámetro query: ?matricula_id=1
- ✅ Pasa el contexto al serializer: `context={'matricula_id': matricula_id}`
- ✅ El serializer calcula el estado_paso para cada paso

**Qué hace el método list():**
```
GET /api/procesomatricula/?matricula_id=1
  ↓
1. Lee matricula_id = '1'
  ↓
2. Crea serializer con contexto
  ↓
3. El serializer para CADA paso busca en Seguimiento_matricula:
   SELECT * FROM seguimientos_matricula 
   WHERE matricula_id=1 AND paso_id=X
  ↓
4. Si existe → estado_paso = seguimiento.estado
   Si no existe → estado_paso = 'pendiente'
  ↓
5. Devuelve JSON con estado_paso para cada paso
```

**Líneas documentadas:** 8-99

---

### 5. `usuarios/urls/seguimiento_matricula_urls.py` (NUEVO)
**Función:** Definir rutas HTTP para seguimiento

**Contenido:**
- ✅ Importa DefaultRouter y SeguimientoMatriculaViewSet
- ✅ Crea el router y registra el ViewSet
- ✅ Genera URLs automáticamente

**URLs generadas:**
```
GET    /api/seguimiento_matricula/           → list()
POST   /api/seguimiento_matricula/           → create()
GET    /api/seguimiento_matricula/{id}/      → retrieve()
PATCH  /api/seguimiento_matricula/{id}/      → partial_update()
```

**Líneas documentadas:** 1-36

---

### 6. `usuarios/urls/__init__.py`
**Función:** Centralizar todas las importaciones de URLs

**Cambio realizado:**
- ✅ Agregada línea: `path('', include('usuarios.urls.seguimiento_matricula_urls'))`
- ✅ Esta línea hace que las rutas de seguimiento sean accesibles

**Por qué existe este archivo:**
Mantiene organizado el enrutamiento. Sin él, tendríamos que importar cada módulo de URLs manualmente en backend/urls.py

**Líneas documentadas:** 1-71

---

### 7. `usuarios/views/__init__.py`
**Función:** Exportar todas las vistas

**Cambio realizado:**
- ✅ Agregada línea: `from .seguimiento_matricula_views import SeguimientoMatriculaViewSet`
- ✅ Esto permite usar: `from usuarios.views import SeguimientoMatriculaViewSet`

**Por qué:**
Centraliza las importaciones y hace el código más legible.

**Líneas documentadas:** 1-56

---

## 🔄 Flujo completo de una matrícula

### Escenario: Un estudiante inicia matrícula

```
1. CREAR MATRÍCULA
   POST /api/matricula/
   Body: { "estudiante": 1, "acudiente": 2, "curso": 3, "jornada": 1, "year_lectivo": 2026 }
   Respuesta: { "id": 1, ... }
   ↓

2. OBTENER PASOS CON ESTADO
   GET /api/procesomatricula/?matricula_id=1
   Respuesta:
   [
     { "id": 1, "nombre_paso": "Registrar estudiante", "estado_paso": "pendiente" },
     { "id": 2, "nombre_paso": "Asignar acudiente", "estado_paso": "pendiente" },
     { "id": 3, "nombre_paso": "Pagar matrícula", "estado_paso": "pendiente" }
   ]
   ↓

3. MARCAR PASO 1 COMO COMPLETADO
   POST /api/seguimiento_matricula/
   Body: { "matricula": 1, "paso": 1, "estado": "completado" }
   
   Backend valida:
   • ¿El paso 1 está activo? SÍ ✓
   • ¿Ya existe seguimiento para paso 1? NO ✓
   • ¿El paso anterior (0) está completo? NO EXISTE ANTERIOR ✓
   
   Backend asigna automáticamente:
   • usuario_actualiza = usuario autenticado
   • fecha_completado = ahora
   ↓

4. VOLVER A CONSULTAR PASOS
   GET /api/procesomatricula/?matricula_id=1
   Respuesta:
   [
     { "id": 1, "nombre_paso": "Registrar estudiante", "estado_paso": "completado" ✅ },
     { "id": 2, "nombre_paso": "Asignar acudiente", "estado_paso": "pendiente" },
     { "id": 3, "nombre_paso": "Pagar matrícula", "estado_paso": "pendiente" }
   ]
   ↓

5. INTENTAR SALTAR A PASO 3 (ERROR)
   POST /api/seguimiento_matricula/
   Body: { "matricula": 1, "paso": 3, "estado": "completado" }
   
   Backend valida:
   • ¿El paso 3 está activo? SÍ ✓
   • ¿Ya existe seguimiento para paso 3? NO ✓
   • ¿El paso anterior (2) está completo? NO ✗ 
   
   Error: "No se puede avanzar al paso actual si el paso anterior... no está completado"
   ↓

6. COMPLETAR PASO 2
   POST /api/seguimiento_matricula/
   Body: { "matricula": 1, "paso": 2, "estado": "completado" }
   Éxito ✓
   ↓

7. AHORA SÍ COMPLETAR PASO 3
   POST /api/seguimiento_matricula/
   Body: { "matricula": 1, "paso": 3, "estado": "completado" }
   
   TRIGGER AUTOMÁTICO:
   • Backend detecta: paso 3 = "Pagar matrícula"
   • El serializer crea automáticamente un Seguimiento_matricula
   ✓ Éxito
```

---

## 📡 Endpoints disponibles

### 1. Listar pasos de proceso con estado
```
GET /api/procesomatricula/?matricula_id=1

Respuesta:
{
  "id": 1,
  "nombre_paso": "Registrar estudiante",
  "orden": 1,
  "icono": "user",
  "color": "#3B82F6",
  "estado_paso": "completado"
}
```

### 2. Crear seguimiento
```
POST /api/seguimiento_matricula/

Body:
{
  "matricula": 1,
  "paso": 3,
  "estado": "completado",
  "observacion": "Pago recibido"
}

El backend asigna automáticamente:
- usuario_actualiza = usuario autenticado
- fecha_completado = timezone.now()
```

### 3. Actualizar seguimiento
```
PATCH /api/seguimiento_matricula/{id}/

Body:
{
  "estado": "completado",
  "observacion": "Completado exitosamente"
}

Solo se actualizan los campos enviados
```

### 4. Listar seguimientos de una matrícula
```
GET /api/seguimiento_matricula/?matricula_id=1

Respuesta: Lista de todos los seguimientos para esa matrícula
```

---

## 🔍 Validaciones implementadas

### Validación de paso activo
```python
def validate_paso(self, value):
    if not value.activo:
        raise ValidationError('El paso seleccionado no está activo')
    return value
```

### Validación de duplicados
```python
if self.instance is None and Seguimiento_matricula.objects.filter(
    matricula=matricula,
    paso=paso
).exists():
    raise ValidationError('Ya existe un seguimiento para esta matrícula y paso')
```

### Validación de orden
```python
paso_anterior = Proceso_matricula.objects.filter(
    orden__lt=paso.orden,
    activo=True
).order_by('-orden').first()

if paso_anterior:
    seguimiento_anterior = Seguimiento_matricula.objects.filter(
        matricula=matricula,
        paso=paso_anterior,
        estado='completado'
    ).first()
    if not seguimiento_anterior:
        raise ValidationError('El paso anterior debe estar completado')
```

---

## 🎯 Resumen de funciones clave

| Componente | Función | Archivo |
|-----------|---------|---------|
| `@receiver(post_save, sender=Pago)` | Trigger automático para crear seguimiento cuando pago se confirma | models.py |
| `validate_paso()` | Valida que el paso esté activo | serializers.py |
| `validate()` | Valida duplicados y orden | serializers.py |
| `get_serializer_class()` | Selecciona serializer según acción | views.py |
| `perform_create()` | Asigna usuario y fecha automáticamente | views.py |
| `perform_update()` | Igual a perform_create() para PATCH | views.py |
| `list()` (override) | Pasa matricula_id al serializer | views.py |

---

## ✅ Checklist de completitud

- [x] Validación de paso activo
- [x] Prevención de duplicados
- [x] Validación de orden de pasos
- [x] Asignación automática de usuario
- [x] Asignación automática de fecha_completado
- [x] Trigger automático para pagos
- [x] Endpoint GET /api/procesomatricula/?matricula_id=X
- [x] Endpoint POST /api/seguimiento_matricula/
- [x] Endpoint PATCH /api/seguimiento_matricula/{id}/
- [x] Documentación exhaustiva en código

---

## 🚀 Próximos pasos sugeridos

1. Crear datos de prueba en la BD:
   - Inserta 7 procesos de matrícula (Registrar estudiante, Asignar acudiente, etc.)
   - Crea una matrícula de prueba

2. Probar endpoints:
   ```bash
   curl -H "Authorization: Bearer TOKEN" \
        http://127.0.0.1:8000/api/procesomatricula/?matricula_id=1
   ```

3. Validar validaciones:
   - Intentar crear seguimiento sin completar paso anterior
   - Intentar crear duplicado
   - Intentar usar paso inactivo

---

**Fecha de documentación:** 3 de mayo de 2026
**Versión:** 1.0 - Completa
