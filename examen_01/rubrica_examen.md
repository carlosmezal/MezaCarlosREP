# Rúbrica - Examen Parcial 1: Programación para Ciencia de Datos

## Resumen de evaluación

| Criterio | Puntos | Método de evaluación |
|----------|--------|---------------------|
| Estructura del proyecto | 15 | Automático + visual |
| Clase del modelo | 20 | Automático + revisión de código |
| Validación de datos | 10 | Automático (incluido en detalle) |
| Conversión de unidades | 15 | Automático (incluido en detalle) |
| Clasificación | 10 | Automático (incluido en detalle) |
| Agrupación y métricas | 15 | Automático (incluido en resumen) |
| Formato de salida | 10 | Automático |
| Git | 5 | Automático + revisión |
| **Total** | **100** | |

---

## Detalle por criterio

### 1. Estructura del proyecto (15 pts)

| Elemento | Pts | Descripción |
|----------|-----|-------------|
| `main.py` en raíz | 2 | Punto de entrada funcional |
| `models/` con `__init__.py` | 2 | Paquete de modelos |
| `models/<entidad>.py` | 3 | Archivo de clase con nombre correcto |
| `utils/` con `__init__.py` | 2 | Paquete de utilidades |
| `utils/io_helpers.py` | 2 | Funciones de lectura/escritura separadas |
| `utils/validators.py` | 2 | Funciones de validación separadas |
| `datos/` y `salidas/` | 2 | Carpetas de datos y salidas |

**Nota:** Se acepta `io.py` o `csv_utils.py` en lugar de `io_helpers.py` (puntaje parcial).

### 2. Clase del modelo (20 pts)

| Elemento | Pts | Descripción |
|----------|-----|-------------|
| Definición de clase | 5 | `class Entidad:` correctamente definida |
| `__init__` | 5 | Recibe y almacena todos los atributos necesarios |
| `clasificar()` | 4 | Método que retorna la clasificación correcta |
| `__str__` | 3 | Representación legible para el usuario |
| `__repr__` | 3 | Representación técnica/debug |

**Penalizaciones:**
- Si la clase existe pero no se usa en `main.py`: -5 pts
- Si los métodos existen pero tienen lógica incorrecta: puntaje parcial

### 3. Validación de datos (10 pts)

| Elemento | Pts | Descripción |
|----------|-----|-------------|
| Detecta columnas faltantes/extra | 3 | Filas con != N columnas se ignoran |
| Detecta valores no numéricos | 3 | `try/except` o validación explícita |
| Detecta unidades inválidas | 2 | Solo acepta las dos unidades válidas |
| Ignora líneas vacías | 2 | No crashea con líneas en blanco |

### 4. Conversión de unidades (15 pts)

| Elemento | Pts | Descripción |
|----------|-----|-------------|
| Fórmula correcta | 8 | Aplica la conversión indicada |
| Solo convierte unidad de origen | 4 | Valores en unidad destino se mantienen |
| Precisión decimal correcta | 3 | Redondeo al número de decimales indicado |

### 5. Clasificación (10 pts)

| Elemento | Pts | Descripción |
|----------|-----|-------------|
| Umbrales correctos | 5 | Usa los umbrales exactos del enunciado |
| Inclusividad correcta | 3 | Límite inferior inclusivo, superior exclusivo |
| Todas las categorías cubiertas | 2 | Sin valores sin clasificar |

### 6. Agrupación y métricas (15 pts)

| Elemento | Pts | Descripción |
|----------|-----|-------------|
| Agrupación correcta | 5 | Usa diccionarios para agrupar |
| Conteo correcto | 3 | Número de registros por grupo |
| Promedio correcto | 4 | Media aritmética correcta |
| Máximo correcto | 3 | Valor máximo por grupo |

### 7. Formato de salida (10 pts)

| Elemento | Pts | Descripción |
|----------|-----|-------------|
| Headers correctos | 3 | Nombres de columna exactos |
| Orden correcto (detalle por ID) | 3 | Ordenado ascendentemente por ID |
| Orden correcto (resumen por conteo desc) | 2 | Ordenado descendentemente por conteo |
| Archivos en `salidas/` | 2 | Rutas correctas de salida |

### 8. Git (5 pts)

| Elemento | Pts | Descripción |
|----------|-----|-------------|
| Mínimo 5 commits | 3 | Con timestamps razonables |
| Mensajes descriptivos | 1 | No "update", "fix", "asdf" |
| `.gitignore` presente | 1 | Ignora `__pycache__`, `.pyc`, etc. |

---

## Criterios de aprobación

- **90-100:** Excelente. Solución completa, bien estructurada, código limpio.
- **75-89:** Bueno. Funciona correctamente con errores menores de formato u organización.
- **60-74:** Suficiente. Funcionalidad básica presente, faltan algunos componentes.
- **40-59:** Insuficiente. Faltan componentes importantes o errores significativos.
- **0-39:** No aprobado. Solución incompleta o no funcional.

## Indicadores de copia

Señales de alerta para revisión manual:
1. **Código idéntico** entre alumnos con variantes diferentes
2. **Variables/comentarios** que mencionan un dominio diferente al asignado
3. **Commits concentrados** en < 10 minutos (sugiere commit dump)
4. **Sin `.gitignore`** o con estructura diferente a la practicada en clase
5. **Alumno no puede explicar** su código en defensa oral

Si se detectan 2+ indicadores, programar defensa oral obligatoria.
