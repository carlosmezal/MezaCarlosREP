"""Configuracion del proyecto."""

# Rutas
DATA_DIR = "data"
OUTPUT_DIR = "outputs"
INVENTARIO_FILE = f"{DATA_DIR}/inventario.csv"
REPORTE_FILE = f"{OUTPUT_DIR}/reporte.csv"

# Configuracion de negocio
STOCK_MINIMO_DEFAULT = 10
DESCUENTO_MAYOREO = 0.15
IVA = 0.16

# Formatos
FORMATO_FECHA = "%Y-%m-%d"
DECIMALES_PRECIO = 2