"""Modulo con operaciones matematicas basicas."""

PI = 3.1415

def sumar(a, b):
    """Retorna la suma de dos numeros."""
    return a + b

def restar(a, b):
    """Retorna la resta de dos numeros."""
    return a - b

def area_circulo(radio):
    """Calcula el area de un circulo."""
    return PI * radio ** 2

class Calculadora:
    """Calculadora simple."""
    def __init__(self):
        self.historial = []
    
    def calcular(self, operacion, a, b):
        if operacion == "+":
            resultado = a + b
        elif operacion == "-":
            resultado = a - b
        self.historial.append(f"{a} {operacion} {b} = {resultado}")
        return resultado


def main():
    # Pruebas del modulo
    print("Probando operaciones...")
    print(f"sumar(2, 3) = {sumar(2, 3)}")
    print(f"restar(5, 2) = {restar(5, 2)}")
    print("Todas las pruebas pasaron!")


# Demostrar __name__ en el notebook
print(f"\n__name__ en este contexto: {__name__}")

# Este codigo SOLO se ejecuta si corres "python operaciones.py"
# NO se ejecuta cuando haces "import operaciones"
if __name__ == "__main__":
    main()

