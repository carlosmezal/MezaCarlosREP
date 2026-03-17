"""
Generador de entradas aleatorias para el Reto 04: Sistema de Inventario Modular.

Genera un archivo CSV con el formato:
    sku,nombre,categoria,precio,stock,stock_minimo

Cada SKU es unico (no hay duplicados). El archivo puede incluir lineas
con errores controlados segun los 5 tipos definidos en la especificacion:
    Tipo 1: precio no numerico
    Tipo 2: stock no numerico
    Tipo 3: stock_minimo no numerico
    Tipo 4: columnas faltantes (menos de 6)
    Tipo 5: columnas extra (mas de 6)

Uso:
    python generar_entrada.py <num_registros> [porcentaje_errores]

Ejemplo:
    python generar_entrada.py 10
    python generar_entrada.py 100 15 > inventario.csv
    python generar_entrada.py 1000 20 > inventario_con_errores.csv

El porcentaje_errores (0-100) indica que fraccion de las lineas tendran
errores. Por defecto es 0 (sin errores).
"""

import sys
import random

# ---------------------------------------------------------------------------
# Categorias base de productos con (precio_min, precio_max)
# Se combinan con MARCAS y SUFIJOS para generar 1000+ productos unicos
# ---------------------------------------------------------------------------

CATEGORIAS_PRECIOS = {
    # Electronica
    "Laptop": (8000, 25000),
    "Ultrabook": (12000, 30000),
    "Chromebook": (5000, 12000),
    "MacBook": (18000, 45000),
    "Notebook": (7000, 18000),
    # Monitores
    "Monitor": (3000, 12000),
    "Monitor Curvo": (5000, 18000),
    "Monitor Gaming": (6000, 20000),
    "Monitor 4K": (8000, 25000),
    "Pantalla Portatil": (2000, 8000),
    # Perifericos de entrada
    "Mouse": (150, 500),
    "Mouse Gaming": (400, 2000),
    "Mouse Ergonomico": (300, 1200),
    "Teclado": (400, 1500),
    "Teclado Mecanico": (800, 3500),
    "Teclado Gaming": (1000, 4000),
    "Touchpad": (500, 2000),
    "Stylus": (300, 2500),
    # Audio
    "Audifonos": (200, 800),
    "Audifonos Bluetooth": (400, 3000),
    "Audifonos Gaming": (500, 2500),
    "Bocina": (300, 2000),
    "Bocina Bluetooth": (500, 4000),
    "Barra Sonido": (1500, 8000),
    "Microfono": (500, 3000),
    "Microfono USB": (400, 2000),
    # Almacenamiento
    "SSD": (800, 3500),
    "SSD Externo": (1000, 5000),
    "HDD": (500, 2500),
    "HDD Externo": (800, 3500),
    "USB Drive": (50, 300),
    "MicroSD": (100, 800),
    "NAS": (5000, 20000),
    # Componentes
    "RAM": (500, 2500),
    "Tarjeta Video": (3000, 25000),
    "Procesador": (2000, 15000),
    "Fuente Poder": (800, 3500),
    "Placa Base": (1500, 10000),
    "Gabinete": (600, 4000),
    "Ventilador": (200, 1000),
    "Disipador": (300, 2000),
    "Pasta Termica": (50, 300),
    # Redes
    "Router": (400, 2000),
    "Router Mesh": (2000, 8000),
    "Switch Red": (300, 3000),
    "Repetidor WiFi": (300, 1500),
    "Adaptador WiFi": (200, 800),
    "Cable Ethernet": (50, 300),
    # Cables y adaptadores
    "Cable HDMI": (80, 350),
    "Cable USB C": (80, 400),
    "Cable DisplayPort": (100, 400),
    "Adaptador USB": (100, 500),
    "Hub USB": (200, 800),
    "Docking Station": (1500, 6000),
    # Accesorios
    "Cargador": (200, 600),
    "Cargador Inalambrico": (300, 1200),
    "Powerbank": (300, 1500),
    "Mousepad": (100, 500),
    "Mousepad XL": (200, 800),
    "Funda Laptop": (200, 800),
    "Mochila Laptop": (400, 2000),
    "Soporte Laptop": (300, 1500),
    "Soporte Monitor": (400, 2000),
    "Lampara Escritorio": (300, 1500),
    # Camaras y video
    "Webcam": (300, 1200),
    "Webcam 4K": (1000, 4000),
    "Webcam HD": (300, 1500),
    "Camara Seguridad": (500, 3000),
    "Capturadora Video": (1500, 5000),
    # Tablets y moviles
    "Tablet": (5000, 15000),
    "iPad": (8000, 25000),
    "Smartwatch": (1500, 6000),
    "Banda Inteligente": (500, 2000),
    "Funda Tablet": (200, 800),
    # Impresion
    "Impresora": (2000, 8000),
    "Impresora Laser": (3000, 12000),
    "Escaner": (1500, 6000),
    "Toner": (300, 1500),
    "Cartucho Tinta": (200, 800),
    # Gaming
    "Control Gaming": (500, 2000),
    "Silla Gaming": (3000, 12000),
    "Tapete Gaming": (300, 1200),
    "Volante Gaming": (2000, 8000),
    # Energia
    "UPS": (1500, 6000),
    "Regulador": (300, 1500),
    "Multicontacto": (100, 500),
    "Extension Electrica": (80, 300),
    # Software (licencias fisicas)
    "Licencia Office": (1000, 3000),
    "Licencia Antivirus": (300, 1200),
    "Licencia Windows": (1500, 4000),
    "Licencia Adobe": (2000, 8000),
}

# Mapa de nombre de producto base -> categoria CSV
# Coincide con las categorias usadas en el notebook:
# Electronica, Accesorios, Audio, Almacenamiento, Componentes,
# Redes, Cables, Video, Impresion, Gaming, Energia, Software
MAPA_CATEGORIA = {}
_CAT_GRUPOS = {
    "Electronica": [
        "Laptop", "Ultrabook", "Chromebook", "MacBook", "Notebook",
        "Monitor", "Monitor Curvo", "Monitor Gaming", "Monitor 4K",
        "Pantalla Portatil", "Tablet", "iPad", "Smartwatch", "Banda Inteligente",
    ],
    "Accesorios": [
        "Mouse", "Mouse Gaming", "Mouse Ergonomico",
        "Teclado", "Teclado Mecanico", "Teclado Gaming", "Touchpad", "Stylus",
        "Cargador", "Cargador Inalambrico", "Powerbank",
        "Mousepad", "Mousepad XL", "Funda Laptop", "Mochila Laptop",
        "Soporte Laptop", "Soporte Monitor", "Lampara Escritorio", "Funda Tablet",
    ],
    "Audio": [
        "Audifonos", "Audifonos Bluetooth", "Audifonos Gaming",
        "Bocina", "Bocina Bluetooth", "Barra Sonido",
        "Microfono", "Microfono USB",
    ],
    "Almacenamiento": [
        "SSD", "SSD Externo", "HDD", "HDD Externo", "USB Drive", "MicroSD", "NAS",
    ],
    "Componentes": [
        "RAM", "Tarjeta Video", "Procesador", "Fuente Poder", "Placa Base",
        "Gabinete", "Ventilador", "Disipador", "Pasta Termica",
    ],
    "Redes": [
        "Router", "Router Mesh", "Switch Red", "Repetidor WiFi",
        "Adaptador WiFi", "Cable Ethernet",
    ],
    "Cables": [
        "Cable HDMI", "Cable USB C", "Cable DisplayPort",
        "Adaptador USB", "Hub USB", "Docking Station",
    ],
    "Video": ["Webcam", "Webcam 4K", "Webcam HD", "Camara Seguridad", "Capturadora Video"],
    "Impresion": ["Impresora", "Impresora Laser", "Escaner", "Toner", "Cartucho Tinta"],
    "Gaming": ["Control Gaming", "Silla Gaming", "Tapete Gaming", "Volante Gaming"],
    "Energia": ["UPS", "Regulador", "Multicontacto", "Extension Electrica"],
    "Software": ["Licencia Office", "Licencia Antivirus", "Licencia Windows", "Licencia Adobe"],
}
for _cat, _prods in _CAT_GRUPOS.items():
    for _p in _prods:
        MAPA_CATEGORIA[_p] = _cat

MARCAS = [
    "Acer", "Apple", "Asus", "BenQ", "Canon", "Corsair", "Dell",
    "Epson", "Gigabyte", "HP", "HyperX", "Kingston", "Lenovo",
    "LG", "Logitech", "MSI", "Razer", "Samsung", "SanDisk",
    "Seagate", "Sony", "TP-Link", "WD", "Xiaomi", "Anker",
]

SUFIJOS = [
    "Pro", "Max", "Ultra", "Lite", "Plus", "Air", "SE",
    "X", "S", "Mini", "Elite", "Basic", "V2", "V3",
]

# Textos basura para errores no numericos.
# Incluye los ejemplos exactos de la especificacion del reto:
#   precio:       N/A, pendiente, $100
#   stock:        abc, null, muchos
#   stock_minimo: ???, sin_dato
TEXTOS_BASURA = [
    "N/A", "pendiente", "$100",          # ejemplos spec: precio
    "abc", "null", "muchos",             # ejemplos spec: stock
    "???", "sin_dato",                   # ejemplos spec: stock_minimo
    "None", "error", "---", "INVALIDO",  # variantes adicionales
    "NaN", "#REF!", "TBD", "vacio",
    "cien", "mil", "12..5", "3,500",
    "inf", "-", "", " ",
]

# Valores posibles de stock_minimo para que sean realistas
VALORES_STOCK_MINIMO = [5, 10, 15, 20, 25, 30, 50]


def construir_catalogo():
    """Genera un catalogo de al menos 1000 productos unicos combinando
    nombre_base + marca (+ sufijo si es necesario).

    Retorna una lista de tuplas: (nombre, categoria, precio_min, precio_max)
    """
    catalogo = []
    nombres_usados = set()

    def agregar(nombre, rango, categoria):
        if nombre not in nombres_usados:
            factor = random.uniform(0.8, 1.3)
            catalogo.append((
                nombre,
                categoria,
                round(rango[0] * factor, 2),
                round(rango[1] * factor, 2),
            ))
            nombres_usados.add(nombre)

    # Paso 1: categorias base sin marca (ej: "Laptop", "Mouse")
    for nombre_base, rango in CATEGORIAS_PRECIOS.items():
        agregar(nombre_base, rango, MAPA_CATEGORIA.get(nombre_base, "General"))

    # Paso 2: base + marca (ej: "Laptop HP", "Mouse Logitech")
    for nombre_base, rango in CATEGORIAS_PRECIOS.items():
        cat = MAPA_CATEGORIA.get(nombre_base, "General")
        for marca in MARCAS:
            agregar(f"{nombre_base} {marca}", rango, cat)
            if len(catalogo) >= 1000:
                break
        if len(catalogo) >= 1000:
            break

    # Paso 3: base + marca + sufijo (ej: "Laptop HP Pro")
    if len(catalogo) < 1000:
        for nombre_base, rango in CATEGORIAS_PRECIOS.items():
            cat = MAPA_CATEGORIA.get(nombre_base, "General")
            for marca in MARCAS:
                for sufijo in SUFIJOS:
                    agregar(f"{nombre_base} {marca} {sufijo}", rango, cat)
                    if len(catalogo) >= 1000:
                        break
                if len(catalogo) >= 1000:
                    break
            if len(catalogo) >= 1000:
                break

    return catalogo


# ---------------------------------------------------------------------------
# Generacion de registros
# ---------------------------------------------------------------------------

def generar_registro_valido(sku, nombre, categoria, precio_min, precio_max):
    """Genera una linea CSV valida con exactamente 6 columnas.
    El stock puede ser 0 o mayor, y puede estar por encima o debajo del minimo."""
    precio = round(random.uniform(precio_min, precio_max), 2)
    stock_minimo = random.choice(VALORES_STOCK_MINIMO)
    # Distribuccion que garantiza mezcla de productos OK y productos que necesitan reorden
    # ~40% de probabilidad de estar por debajo del minimo
    if random.random() < 0.4:
        stock = random.randint(0, max(stock_minimo - 1, 0))
    else:
        stock = random.randint(stock_minimo, stock_minimo * 3)
    return f"{sku},{nombre},{categoria},{precio:.2f},{stock},{stock_minimo}"


def generar_registro_con_error(sku, nombre, categoria, precio_min, precio_max):
    """Genera una linea con uno de los 5 tipos de error de la especificacion.

    Tipo 1: precio no numerico
    Tipo 2: stock no numerico
    Tipo 3: stock_minimo no numerico
    Tipo 4: columnas faltantes (menos de 6)
    Tipo 5: columnas extra (mas de 6)
    """
    tipo_error = random.choices(
        ["precio_no_numerico", "stock_no_numerico", "stock_min_no_numerico",
         "columnas_faltantes", "columnas_extra"],
        weights=[20, 20, 20, 20, 20],
        k=1,
    )[0]

    precio = round(random.uniform(precio_min, precio_max), 2)
    stock_minimo = random.choice(VALORES_STOCK_MINIMO)
    stock = random.randint(0, stock_minimo * 3)

    if tipo_error == "precio_no_numerico":
        # Tipo 1: campo precio con texto invalido
        precio_str = random.choice(TEXTOS_BASURA)
        return f"{sku},{nombre},{categoria},{precio_str},{stock},{stock_minimo}"

    elif tipo_error == "stock_no_numerico":
        # Tipo 2: campo stock con texto invalido
        stock_str = random.choice(TEXTOS_BASURA)
        return f"{sku},{nombre},{categoria},{precio:.2f},{stock_str},{stock_minimo}"

    elif tipo_error == "stock_min_no_numerico":
        # Tipo 3: campo stock_minimo con texto invalido
        stock_min_str = random.choice(TEXTOS_BASURA)
        return f"{sku},{nombre},{categoria},{precio:.2f},{stock},{stock_min_str}"

    elif tipo_error == "columnas_faltantes":
        # Tipo 4: linea con 1 a 5 columnas (menos de 6)
        cols = [sku, nombre, categoria, f"{precio:.2f}", str(stock), str(stock_minimo)]
        n_cols = random.randint(1, 5)
        return ",".join(cols[:n_cols])

    elif tipo_error == "columnas_extra":
        # Tipo 5: linea con 7 a 9 columnas (mas de 6)
        extras = [random.choice(TEXTOS_BASURA) for _ in range(random.randint(1, 3))]
        return f"{sku},{nombre},{categoria},{precio:.2f},{stock},{stock_minimo},{','.join(extras)}"


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(
            f"Uso: python {sys.argv[0]} <num_registros> [porcentaje_errores]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError
    except ValueError:
        print("Error: <num_registros> debe ser un entero positivo.", file=sys.stderr)
        sys.exit(1)

    pct_errores = 0
    if len(sys.argv) == 3:
        try:
            pct_errores = int(sys.argv[2])
            if not (0 <= pct_errores <= 100):
                raise ValueError
        except ValueError:
            print("Error: porcentaje_errores debe ser un entero entre 0 y 100.", file=sys.stderr)
            sys.exit(1)

    catalogo = construir_catalogo()

    # Encabezado CSV (exactamente 6 columnas como pide la especificacion)
    print("sku,nombre,categoria,precio,stock,stock_minimo")

    for i in range(n):
        # SKU unico secuencial (nunca se repite)
        sku = f"SKU{i + 1:05d}"
        nombre, categoria, precio_min, precio_max = random.choice(catalogo)

        if pct_errores > 0 and random.randint(1, 100) <= pct_errores:
            print(generar_registro_con_error(sku, nombre, categoria, precio_min, precio_max))
        else:
            print(generar_registro_valido(sku, nombre, categoria, precio_min, precio_max))


if __name__ == "__main__":
    main()
