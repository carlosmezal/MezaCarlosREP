#!/usr/bin/env python3

import argparse
import csv
import os


def es_valor_nulo(valor):
    if valor is None:
        return True
    return isinstance(valor, str) and valor.strip() == ""


def es_numerico(valor):
    try:
        float(str(valor).replace(",", "").strip())
        return True
    except (ValueError, TypeError):
        return False


def es_fecha(valor):
    v = str(valor).strip()
    if len(v) >= 10 and v[4] == "-" and v[7] == "-":
        try:
            anio, mes, dia = map(int, v[:10].split("-"))
            return 1900 <= anio <= 2100 and 1 <= mes <= 12 and 1 <= dia <= 31
        except ValueError:
            return False
    return False


def es_booleano(valor):
    v = str(valor).strip().lower()
    return v in ["true", "false", "yes", "no", "si", "1", "0", "t", "f"]


def inferir_tipo(valores):
    valores_validos = [v for v in valores if not es_valor_nulo(v)]

    if not valores_validos:
        return "texto"

    total = len(valores_validos)
    umbral = 0.8

    fechas = sum(1 for v in valores_validos if es_fecha(v))
    booleanos = sum(1 for v in valores_validos if es_booleano(v))
    numericos = sum(1 for v in valores_validos if es_numerico(v))

    if fechas / total >= umbral:
        return "fecha"
    if booleanos / total >= umbral:
        return "booleano"
    if numericos / total >= umbral:
        return "numerico"

    return "texto"


def calcular_porcentaje(parte, total):
    if total == 0:
        return 0.00
    return round((parte / total) * 100, 2)


def perfilar_columna(nombre, valores):
    total = len(valores)
    nulos = sum(1 for v in valores if es_valor_nulo(v))
    no_nulos = [v for v in valores if not es_valor_nulo(v)]
    unicos = len(set(no_nulos))
    ejemplo = no_nulos[0] if no_nulos else ""

    return {
        "nombre_columna": nombre,
        "tipo_inferido": inferir_tipo(valores),
        "total_registros": total,
        "valores_nulos": nulos,
        "porcentaje_nulos": f"{calcular_porcentaje(nulos, total):.2f}",
        "valores_unicos": unicos,
        "porcentaje_unicos": f"{calcular_porcentaje(unicos, total):.2f}",
        "ejemplo_valor": ejemplo
    }


def leer_csv(ruta):
    with open(ruta, "r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        encabezados = lector.fieldnames

        if encabezados is None:
            return [], []

        filas = list(lector)

    return encabezados, filas


def perfilar_csv(ruta_entrada):
    encabezados, filas = leer_csv(ruta_entrada)
    perfiles = []

    for columna in encabezados:
        valores = [fila.get(columna, "") for fila in filas]
        perfiles.append(perfilar_columna(columna, valores))

    return perfiles


def guardar_perfil(perfiles, ruta_salida):
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    columnas = [
        "nombre_columna",
        "tipo_inferido",
        "total_registros",
        "valores_nulos",
        "porcentaje_nulos",
        "valores_unicos",
        "porcentaje_unicos",
        "ejemplo_valor"
    ]

    with open(ruta_salida, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(perfiles)


def main():
    parser = argparse.ArgumentParser(description="Perfilador de datasets CSV")
    parser.add_argument("-i", "--input", required=True, help="Ruta del CSV de entrada")
    parser.add_argument("-o", "--output", required=True, help="Ruta del CSV de salida")

    args = parser.parse_args()

    perfiles = perfilar_csv(args.input)
    guardar_perfil(perfiles, args.output)

    print(f"Perfil generado correctamente en: {args.output}")


if __name__ == "__main__":
    main()