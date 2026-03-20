
# Importar modulo completo del paquete
from utils import matematicas
a, b=1, 2

r1 =matematicas.sumar(a, b)
print(f"{a} + {b} = {r1}")

# Importar funcion especifica
from utils.matematicas import sumar
r2 = sumar(a, b)
print(f"{a} + {b} = {r2}")

# Si __init__.py expone las funciones:
from utils import sumar, validar_email
r3 = sumar(a, b)
print(f"{a} + {b} = {r3}")
