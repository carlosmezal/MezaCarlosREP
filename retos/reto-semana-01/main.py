import sys

def procesar_linea(linea):
    linea = linea.strip()

    if linea == "":
        return 0

    partes = linea.split(",")
    suma = 0

    for parte in partes:
        parte = parte.strip()

        try:
            numero = int(float(parte))
            suma += numero
        except ValueError:
            pass

    return suma

def main():
    for linea in sys.stdin:
        print(procesar_linea(linea))

if __name__ == "__main__":
    main()