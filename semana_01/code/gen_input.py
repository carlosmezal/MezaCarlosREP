"""
Generador de archivos de entrada para el Reto 01: Calculadora de Sumas.

Uso:
    python3 gen_input.py <num_lineas> [archivo_salida]

Ejemplos:
    python3 gen_input.py 50                    # imprime a stdout
    python3 gen_input.py 100 entrada.txt       # guarda en archivo
"""

import sys
import random
import string


def linea_vacia():
    """Linea completamente vacia."""
    return ""


def linea_solo_espacios():
    """Linea con solo espacios."""
    return " " * random.randint(1, 10)


def linea_numeros_enteros():
    """Linea con numeros enteros simples separados por comas."""
    n = random.randint(1, 20)
    nums = [str(random.randint(-1000, 1000)) for _ in range(n)]
    return ",".join(nums)


def linea_un_elemento():
    """Linea con un solo numero."""
    return str(random.randint(-500, 500))


def linea_decimales():
    """Linea con numeros decimales."""
    n = random.randint(1, 15)
    nums = []
    for _ in range(n):
        val = round(random.uniform(-100, 100), random.randint(1, 4))
        nums.append(str(val))
    return ",".join(nums)


def linea_caracteres_basura():
    """Linea con numeros mezclados con caracteres invalidos."""
    n = random.randint(1, 10)
    valores = []
    basura = string.ascii_letters + "!@#$%^&*()_=[]{}|;:'\""
    for _ in range(n):
        num_str = str(random.randint(0, 999))
        # Insertar 1-3 caracteres basura en posiciones aleatorias
        resultado = list(num_str)
        for _ in range(random.randint(1, 3)):
            pos = random.randint(0, len(resultado))
            resultado.insert(pos, random.choice(basura))
        valores.append("".join(resultado))
    return ",".join(valores)


def linea_solo_letras():
    """Linea donde todos los valores son solo letras (resultado 0)."""
    n = random.randint(1, 5)
    vals = ["".join(random.choices(string.ascii_letters, k=random.randint(1, 5))) for _ in range(n)]
    return ",".join(vals)


def linea_espacios_extra():
    """Linea con espacios alrededor de los valores."""
    n = random.randint(2, 10)
    valores = []
    for _ in range(n):
        espacios_antes = " " * random.randint(0, 5)
        espacios_despues = " " * random.randint(0, 5)
        valores.append(f"{espacios_antes}{random.randint(-100, 100)}{espacios_despues}")
    return ",".join(valores)


def linea_comas_extra():
    """Linea con comas al inicio, al final, o consecutivas."""
    n = random.randint(1, 8)
    nums = [str(random.randint(0, 50)) for _ in range(n)]
    base = ",".join(nums)
    variante = random.choice(["inicio", "final", "consecutivas", "ambos"])
    if variante == "inicio":
        return "," + base
    elif variante == "final":
        return base + ","
    elif variante == "consecutivas":
        pos = random.randint(0, len(nums) - 1)
        nums[pos] = ""
        return ",".join(nums)
    else:
        return "," + base + ","


def linea_ceros():
    """Linea con varios ceros."""
    n = random.randint(2, 10)
    return ",".join(["0"] * n)


def linea_negativos():
    """Linea con solo numeros negativos."""
    n = random.randint(2, 10)
    nums = [str(random.randint(-500, -1)) for _ in range(n)]
    return ",".join(nums)


def linea_decimal_sin_entera():
    """Linea con valores como .5, -.3"""
    n = random.randint(1, 5)
    vals = []
    for _ in range(n):
        signo = random.choice(["", "-"])
        dec = random.randint(1, 99)
        vals.append(f"{signo}.{dec}")
    return ",".join(vals)


def linea_numeros_grandes():
    """Linea con numeros muy grandes."""
    n = random.randint(1, 5)
    nums = [str(random.randint(-1000000, 1000000)) for _ in range(n)]
    return ",".join(nums)


def linea_simbolos_moneda():
    """Linea con simbolos de moneda como $100, USD50."""
    prefijos = ["$", "USD", "MXN", "#", "€"]
    n = random.randint(1, 5)
    vals = []
    for _ in range(n):
        p = random.choice(prefijos)
        vals.append(f"{p}{random.randint(1, 999)}")
    return ",".join(vals)


def linea_muchos_elementos():
    """Linea con muchos elementos (100-500)."""
    n = random.randint(100, 500)
    nums = [str(random.randint(-10, 10)) for _ in range(n)]
    return ",".join(nums)


# Generadores con sus pesos (probabilidad relativa)
GENERADORES = [
    (linea_vacia, 5),
    (linea_solo_espacios, 3),
    (linea_numeros_enteros, 20),
    (linea_un_elemento, 8),
    (linea_decimales, 12),
    (linea_caracteres_basura, 10),
    (linea_solo_letras, 5),
    (linea_espacios_extra, 8),
    (linea_comas_extra, 6),
    (linea_ceros, 3),
    (linea_negativos, 5),
    (linea_decimal_sin_entera, 4),
    (linea_numeros_grandes, 4),
    (linea_simbolos_moneda, 4),
    (linea_muchos_elementos, 3),
]


def generar_entrada(num_lineas, seed=None):
    """Genera una lista de lineas de entrada aleatorias."""
    if seed is not None:
        random.seed(seed)

    generadores, pesos = zip(*GENERADORES)
    lineas = []
    for _ in range(num_lineas):
        gen = random.choices(generadores, weights=pesos, k=1)[0]
        lineas.append(gen())
    return lineas


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python3 {sys.argv[0]} <num_lineas> [archivo_salida] [--seed N]", file=sys.stderr)
        sys.exit(1)

    num_lineas = int(sys.argv[1])
    archivo_salida = None
    seed = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--seed" and i + 1 < len(args):
            seed = int(args[i + 1])
            i += 2
        else:
            archivo_salida = args[i]
            i += 1

    lineas = generar_entrada(num_lineas, seed)
    texto = "\n".join(lineas) + "\n"

    if archivo_salida:
        with open(archivo_salida, "w") as f:
            f.write(texto)
        print(f"Generadas {num_lineas} lineas en '{archivo_salida}'", file=sys.stderr)
    else:
        sys.stdout.write(texto)


if __name__ == "__main__":
    main()
