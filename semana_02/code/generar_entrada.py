"""
Generador de entradas aleatorias para el Reto 02: Clasificador de Temperaturas.

Uso:
    python generar_entrada.py <num_registros>

Ejemplo:
    python generar_entrada.py 10
    python generar_entrada.py 100 > entrada.txt
"""

import sys
import random

CIUDADES = [
    "CDMX", "Guadalajara", "Monterrey", "Puebla", "Tijuana",
    "Nueva York", "Los Angeles", "Chicago", "Houston", "Miami",
    "Londres", "Paris", "Berlin", "Madrid", "Roma",
    "Tokio", "Pekín", "Mumbai", "Dubai", "Singapur",
    "Moscu", "Oslo", "Helsinki", "Estocolmo", "Reykjavik",
    "Bangkok", "Cairo", "Lagos", "Nairobi", "Lima",
    "Buenos Aires", "Bogota", "Santiago", "Caracas", "Cancun",
    "Phoenix", "Las Vegas", "Denver", "Seattle", "Boston",
    "Ankara", "Atenas", "Budapest", "Varsovia", "Lisboa",
    "Sydney", "Melbourne", "Auckland", "Honolulu", "Toronto",
]


def generar_registro(ciudad):
    unidad = random.choice(["C", "F"])
    if unidad == "C":
        temperatura = round(random.uniform(-30, 50), 1)
    else:
        temperatura = round(random.uniform(-22, 122), 1)
    # Evitar .0 innecesario si es entero
    if temperatura == int(temperatura):
        temperatura = int(temperatura)
    return f"{ciudad},{temperatura},{unidad}"


def main():
    if len(sys.argv) != 2:
        print(f"Uso: python {sys.argv[0]} <num_registros>", file=sys.stderr)
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError
    except ValueError:
        print("Error: <num_registros> debe ser un entero positivo.", file=sys.stderr)
        sys.exit(1)

    print("ciudad,temperatura,unidad")

    ciudades_disponibles = CIUDADES.copy()
    random.shuffle(ciudades_disponibles)

    for i in range(n):
        # Si se agotaron las ciudades únicas, reutilizar con sufijo numérico
        if i < len(ciudades_disponibles):
            ciudad = ciudades_disponibles[i]
        else:
            ciudad = random.choice(CIUDADES) + f"_{i}"
        print(generar_registro(ciudad))


if __name__ == "__main__":
    main()
