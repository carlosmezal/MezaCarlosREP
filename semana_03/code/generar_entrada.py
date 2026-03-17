"""
Generador de entradas aleatorias para el Reto 03: Analizador de Ventas.

Uso:
    python generar_entrada.py <num_registros> [porcentaje_errores]

Ejemplo:
    python generar_entrada.py 10
    python generar_entrada.py 100 15 > entrada.txt
    python generar_entrada.py 1000 20 > entrada_con_errores.txt

El porcentaje_errores (0-100) indica que fraccion de las lineas tendran
errores (columnas faltantes, columnas extra, valores no numericos).
Por defecto es 0 (sin errores).
"""

import sys
import random
import string
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Categorias de productos con (precio_min, precio_max)
# Se generan combinaciones de marca + modelo para superar los 1000 productos
# ---------------------------------------------------------------------------

CATEGORIAS = {
    # Laptops
    "Laptop": (8000, 25000),
    "Ultrabook": (12000, 30000),
    "Chromebook": (5000, 12000),
    "MacBook": (18000, 45000),
    "Notebook": (7000, 18000),
    # Monitores
    "Monitor": (3000, 12000),
    "Monitor_Curvo": (5000, 18000),
    "Monitor_Gaming": (6000, 20000),
    "Monitor_4K": (8000, 25000),
    "Pantalla_Portatil": (2000, 8000),
    # Perifericos de entrada
    "Mouse": (150, 500),
    "Mouse_Gaming": (400, 2000),
    "Mouse_Ergonomico": (300, 1200),
    "Teclado": (400, 1500),
    "Teclado_Mecanico": (800, 3500),
    "Teclado_Gaming": (1000, 4000),
    "Touchpad": (500, 2000),
    "Stylus": (300, 2500),
    # Audio
    "Audifonos": (200, 800),
    "Audifonos_Bluetooth": (400, 3000),
    "Audifonos_Gaming": (500, 2500),
    "Bocina": (300, 2000),
    "Bocina_Bluetooth": (500, 4000),
    "Barra_Sonido": (1500, 8000),
    "Microfono": (500, 3000),
    "Microfono_USB": (400, 2000),
    # Almacenamiento
    "SSD": (800, 3500),
    "SSD_Externo": (1000, 5000),
    "HDD": (500, 2500),
    "HDD_Externo": (800, 3500),
    "USB": (50, 300),
    "MicroSD": (100, 800),
    "NAS": (5000, 20000),
    # Componentes
    "RAM": (500, 2500),
    "Tarjeta_Video": (3000, 25000),
    "Procesador": (2000, 15000),
    "Fuente_Poder": (800, 3500),
    "Placa_Base": (1500, 10000),
    "Gabinete": (600, 4000),
    "Ventilador": (200, 1000),
    "Disipador": (300, 2000),
    "Pasta_Termica": (50, 300),
    # Redes
    "Router": (400, 2000),
    "Router_Mesh": (2000, 8000),
    "Switch_Red": (300, 3000),
    "Repetidor_WiFi": (300, 1500),
    "Adaptador_WiFi": (200, 800),
    "Cable_Ethernet": (50, 300),
    # Cables y adaptadores
    "Cable_HDMI": (80, 350),
    "Cable_USB_C": (80, 400),
    "Cable_DisplayPort": (100, 400),
    "Adaptador_USB": (100, 500),
    "Hub_USB": (200, 800),
    "Docking_Station": (1500, 6000),
    # Accesorios
    "Cargador": (200, 600),
    "Cargador_Inalambrico": (300, 1200),
    "Powerbank": (300, 1500),
    "Mousepad": (100, 500),
    "Mousepad_XL": (200, 800),
    "Funda_Laptop": (200, 800),
    "Mochila_Laptop": (400, 2000),
    "Soporte_Laptop": (300, 1500),
    "Soporte_Monitor": (400, 2000),
    "Lampara_Escritorio": (300, 1500),
    # Camaras y video
    "Webcam": (300, 1200),
    "Webcam_4K": (1000, 4000),
    "Camara_Seguridad": (500, 3000),
    "Capturadora_Video": (1500, 5000),
    # Tablets y moviles
    "Tablet": (5000, 15000),
    "iPad": (8000, 25000),
    "Smartwatch": (1500, 6000),
    "Banda_Inteligente": (500, 2000),
    "Funda_Tablet": (200, 800),
    # Impresion
    "Impresora": (2000, 8000),
    "Impresora_Laser": (3000, 12000),
    "Escaner": (1500, 6000),
    "Toner": (300, 1500),
    "Cartucho_Tinta": (200, 800),
    # Gaming
    "Control_Gaming": (500, 2000),
    "Silla_Gaming": (3000, 12000),
    "Tapete_Gaming": (300, 1200),
    "Volante_Gaming": (2000, 8000),
    # Energia
    "UPS": (1500, 6000),
    "Regulador": (300, 1500),
    "Multicontacto": (100, 500),
    "Extension_Electrica": (80, 300),
    # Software (licencias fisicas)
    "Licencia_Office": (1000, 3000),
    "Licencia_Antivirus": (300, 1200),
    "Licencia_Windows": (1500, 4000),
    "Licencia_Adobe": (2000, 8000),
}

MARCAS = [
    "Acer", "Apple", "Asus", "BenQ", "Canon", "Corsair", "Dell",
    "Epson", "Gigabyte", "HP", "HyperX", "Kingston", "Lenovo",
    "LG", "Logitech", "MSI", "Razer", "Samsung", "SanDisk",
    "Seagate", "Sony", "TP_Link", "WD", "Xiaomi", "Anker",
]

SUFIJOS = [
    "Pro", "Max", "Ultra", "Lite", "Plus", "Air", "SE",
    "X", "S", "Mini", "Elite", "Basic", "V2", "V3",
]


def construir_catalogo():
    """Genera un catalogo de al menos 1000 productos combinando
    categoria + marca + sufijo, cada uno con su rango de precio."""
    catalogo = {}
    productos_generados = set()

    # Primero agregar las categorias base
    for cat, rango in CATEGORIAS.items():
        catalogo[cat] = rango
        productos_generados.add(cat)

    # Generar combinaciones hasta superar 1000
    for cat, rango in CATEGORIAS.items():
        for marca in MARCAS:
            nombre = f"{cat}_{marca}"
            if nombre not in productos_generados:
                # Variar ligeramente el rango por marca
                factor = random.uniform(0.8, 1.3)
                catalogo[nombre] = (
                    round(rango[0] * factor, 2),
                    round(rango[1] * factor, 2),
                )
                productos_generados.add(nombre)
            if len(catalogo) >= 1000:
                break

        if len(catalogo) >= 1000:
            break

    # Si aun no alcanzamos 1000, agregar con sufijos
    if len(catalogo) < 1000:
        for cat, rango in CATEGORIAS.items():
            for marca in MARCAS:
                for sufijo in SUFIJOS:
                    nombre = f"{cat}_{marca}_{sufijo}"
                    if nombre not in productos_generados:
                        factor = random.uniform(0.7, 1.4)
                        catalogo[nombre] = (
                            round(rango[0] * factor, 2),
                            round(rango[1] * factor, 2),
                        )
                        productos_generados.add(nombre)
                    if len(catalogo) >= 1000:
                        break
                if len(catalogo) >= 1000:
                    break
            if len(catalogo) >= 1000:
                break

    return catalogo


FECHA_INICIO = date(2026, 1, 1)

# Textos basura para generar errores de tipo no numerico
TEXTOS_BASURA = [
    "abc", "N/A", "null", "None", "error", "---", "???",
    "pendiente", "sin_dato", "vacio", "INVALIDO", "NaN",
    "#REF!", "TBD", "xx", "cien", "mil", "muchos", "$100",
    "12..5", "3,500", "1e999", "inf", "-", "", " ",
]


def generar_registro_valido(fecha, producto, rango_precio):
    cantidad = random.randint(1, 20)
    precio = round(random.uniform(rango_precio[0], rango_precio[1]), 2)
    return f"{fecha},{producto},{cantidad},{precio:.2f}"


def generar_registro_con_error(fecha, producto, rango_precio):
    """Genera una linea con algun tipo de error aleatorio."""
    tipo_error = random.choices(
        ["cantidad_no_numerica", "precio_no_numerico", "columnas_faltantes", "columnas_extra"],
        weights=[25, 25, 25, 25],
        k=1,
    )[0]

    cantidad = random.randint(1, 20)
    precio = round(random.uniform(rango_precio[0], rango_precio[1]), 2)

    if tipo_error == "cantidad_no_numerica":
        cantidad_str = random.choice(TEXTOS_BASURA)
        return f"{fecha},{producto},{cantidad_str},{precio:.2f}"

    elif tipo_error == "precio_no_numerico":
        precio_str = random.choice(TEXTOS_BASURA)
        return f"{fecha},{producto},{cantidad},{precio_str}"

    elif tipo_error == "columnas_faltantes":
        # Generar linea con 1, 2 o 3 columnas
        n_cols = random.randint(1, 3)
        cols = [str(fecha), producto, str(cantidad), f"{precio:.2f}"]
        return ",".join(cols[:n_cols])

    elif tipo_error == "columnas_extra":
        # Agregar 1 a 3 columnas extra
        extras = [random.choice(TEXTOS_BASURA) for _ in range(random.randint(1, 3))]
        return f"{fecha},{producto},{cantidad},{precio:.2f}," + ",".join(extras)


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
    productos_lista = list(catalogo.items())

    print("fecha,producto,cantidad,precio_unitario")

    for i in range(n):
        fecha = FECHA_INICIO + timedelta(days=random.randint(0, max(n, 30)))
        producto, rango_precio = random.choice(productos_lista)

        if pct_errores > 0 and random.randint(1, 100) <= pct_errores:
            print(generar_registro_con_error(fecha, producto, rango_precio))
        else:
            print(generar_registro_valido(fecha, producto, rango_precio))


if __name__ == "__main__":
    main()
