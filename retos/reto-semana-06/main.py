import sys
import re

DEPARTAMENTOS_VALIDOS = ["VEN", "ADM", "TEC", "LOG", "RHH"]
SERIES_VALIDAS = ["A", "B", "C", "D", "E"]


def detectar_tipo(codigo):

    if re.match(r'^[A-Za-z]{3}-\d{4}-[A-Za-z]{2}$', codigo):
        return "producto"

    if re.match(r'^ENV-\d{4}-\d{2}-\d{2}-\d{6}$', codigo):
        return "envio"

    if re.match(r'^EMP-[A-Za-z]{3}-\d{4}$', codigo):
        return "empleado"

    if re.match(r'^FAC-[A-Za-z]-\d{6}$', codigo):
        return "factura"

    return "desconocido"


def validar_producto(codigo):

    return re.match(
        r'^[A-Z]{3}-\d{4}-[A-Z]{2}$',
        codigo
    ) is not None


def validar_envio(codigo):

    patron = r'^ENV-(\d{4})-(\d{2})-(\d{2})-(\d{6})$'

    m = re.match(patron, codigo)

    if not m:
        return False

    anio = int(m.group(1))
    mes = int(m.group(2))
    dia = int(m.group(3))

    return (
        2020 <= anio <= 2030
        and 1 <= mes <= 12
        and 1 <= dia <= 31
    )


def validar_empleado(codigo):

    patron = r'^EMP-([A-Z]{3})-(\d{4})$'

    m = re.match(patron, codigo)

    if not m:
        return False

    departamento = m.group(1)
    numero = m.group(2)

    if departamento not in DEPARTAMENTOS_VALIDOS:
        return False

    if numero.startswith("0"):
        return False

    return True


def validar_factura(codigo):

    patron = r'^FAC-([A-Z])-(\d{6})$'

    m = re.match(patron, codigo)

    if not m:
        return False

    serie = m.group(1)

    return serie in SERIES_VALIDAS


def validar_codigo(codigo):

    tipo = detectar_tipo(codigo)

    if tipo == "producto":
        return tipo, validar_producto(codigo)

    if tipo == "envio":
        return tipo, validar_envio(codigo)

    if tipo == "empleado":
        return tipo, validar_empleado(codigo)

    if tipo == "factura":
        return tipo, validar_factura(codigo)

    return "desconocido", False


def main():

    print("codigo,tipo,valido")

    for linea in sys.stdin:

        codigo = linea.strip()

        if not codigo:
            continue

        tipo, valido = validar_codigo(codigo)

        estado = "VALIDO" if valido else "INVALIDO"

        print(f"{codigo},{tipo},{estado}")


if __name__ == "__main__":
    main()