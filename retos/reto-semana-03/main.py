import sys

def main():
    productos = {}

    primera_linea = True

    for linea in sys.stdin:
        linea = linea.strip()

        if primera_linea:
            primera_linea = False
            continue

        if not linea:
            continue

        partes = linea.split(',')

        if len(partes) != 4:
            continue

        try:
            producto = partes[1].strip()
            cantidad = int(partes[2])
            precio = float(partes[3])

            if cantidad < 0 or precio < 0:
                continue

        except ValueError:
            continue

        if producto not in productos:
            productos[producto] = {
                "unidades": 0,
                "ingreso": 0.0
            }

        productos[producto]["unidades"] += cantidad
        productos[producto]["ingreso"] += cantidad * precio

    resultado = []

    for producto, datos in productos.items():
        unidades = datos["unidades"]
        ingreso = datos["ingreso"]

        promedio = 0.0
        if unidades > 0:
            promedio = ingreso / unidades

        resultado.append(
            (producto, unidades, ingreso, promedio)
        )

    resultado.sort(key=lambda x: x[2], reverse=True)

    print("producto,unidades_vendidas,ingreso_total,precio_promedio")

    for producto, unidades, ingreso, promedio in resultado:
        print(
            f"{producto},{unidades},{ingreso:.2f},{promedio:.2f}"
        )

if __name__ == "__main__":
    main()