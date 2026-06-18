from models.producto import Producto
from utils.validators import validar_producto
from utils.io import leer_inventario, escribir_reporte

ARCHIVO_INVENTARIO = "data/inventario.csv"
ARCHIVO_REPORTE = "outputs/reporte_inventario.csv"


def crear_productos(datos_raw):

    productos = []

    for dato in datos_raw:

        if validar_producto(dato):

            productos.append(
                Producto(
                    dato["sku"],
                    dato["nombre"],
                    dato["categoria"],
                    dato["precio"],
                    dato["stock"],
                    dato["stock_minimo"]
                )
            )

    return productos


def main():

    datos = leer_inventario(ARCHIVO_INVENTARIO)

    productos = crear_productos(datos)

    reorden = [
        p for p in productos
        if p.necesita_reorden()
    ]

    escribir_reporte(
        reorden,
        ARCHIVO_REPORTE
    )

    print(
        f"Reporte generado: {ARCHIVO_REPORTE}"
    )


if __name__ == "__main__":
    main()