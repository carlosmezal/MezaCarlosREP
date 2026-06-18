import csv

def leer_inventario(ruta_archivo):

    productos = []

    with open(ruta_archivo, encoding="utf-8") as archivo:

        lector = csv.DictReader(archivo)

        for fila in lector:
            productos.append(fila)

    return productos


def escribir_reporte(productos, ruta_archivo):

    with open(
        ruta_archivo,
        "w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        writer = csv.writer(archivo)

        writer.writerow([
            "sku",
            "nombre",
            "stock",
            "stock_minimo",
            "faltantes"
        ])

        for producto in productos:

            writer.writerow([
                producto.sku,
                producto.nombre,
                producto.stock,
                producto.stock_minimo,
                producto.unidades_faltantes()
            ])