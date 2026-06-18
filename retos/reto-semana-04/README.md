Reto Semana 04 - Inventario Modular

Descripción

Sistema de gestión de inventario desarrollado en Python utilizando una arquitectura modular basada en paquetes y clases.

El programa carga información de productos desde un archivo CSV, valida los datos, identifica productos que requieren reabastecimiento y genera un reporte de inventario.

Estructura del proyecto

```text
reto-semana-04/
main
 models/
   __init__.py
   producto.py

 utils/
    __init__.py
    io.py
    validators.py

 data/
   inventario.csv

outputs/
   reporte_inventario.csv
.gitignore
 README.md