"""
╔══════════════════════════════════════════════════════════════╗
║  data_loader.py — Módulo de Carga de Archivos Locales        ║
╚══════════════════════════════════════════════════════════════╝

RESPONSABILIDAD:
  Cargar archivos locales (CSV, TSV, JSON) y convertirlos en
  pandas DataFrames listos para analizar o visualizar.

PRINCIPIO OOP APLICADO:
  Responsabilidad Única (Single Responsibility Principle - SRP):
  Esta clase SOLO se encarga de leer archivos. No analiza, no
  grafica, no guarda. Solo carga y convierte.

CONCEPTOS CLAVE:
  - pandas.read_csv()   : lee CSV y TSV directamente a DataFrame
  - json.load()         : parsea JSON a dict/list de Python
  - pd.DataFrame()      : crea DataFrame desde lista de dicts
"""

import os
import json
import pandas as pd


class DataLoader:
    """
    Clase para cargar archivos de datos locales a pandas DataFrames.

    Soporta tres formatos:
      - CSV  (Comma-Separated Values)   → separador: ','
      - TSV  (Tab-Separated Values)     → separador: '\\t'
      - JSON (JavaScript Object Notation)

    Atributos
    ---------
    last_loaded_source : str
        Nombre del último archivo cargado (útil para el UI).
    last_loaded_type : str
        Tipo del último archivo ('CSV', 'TSV' o 'JSON').
    """

    def __init__(self):
        """Inicializa con atributos de seguimiento vacíos."""
        self.last_loaded_source: str = ""
        self.last_loaded_type: str = ""

    # ─────────────────────────────────────────────────────────────── #
    #  CSV                                                             #
    # ─────────────────────────────────────────────────────────────── #
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        Lee un archivo CSV y lo convierte en DataFrame.

        Parámetros
        ----------
        filepath : str
            Ruta al archivo .csv (absoluta o relativa).

        Retorna
        -------
        pd.DataFrame
            Cada fila del CSV → una fila del DataFrame.
            Primera fila del CSV → nombres de columnas.

        Excepciones
        -----------
        FileNotFoundError : si el archivo no existe.
        pd.errors.EmptyDataError : si el archivo está vacío.

        ── Cómo funciona pandas.read_csv() ──────────────────────────
        1. Abre el archivo y lee su contenido línea por línea.
        2. La primera línea se interpreta como nombres de columnas
           (parámetro header=0 por defecto).
        3. El resto de líneas se convierten en filas del DataFrame.
        4. pandas infiere automáticamente los tipos de datos:
             "21" → int64, "9.2" → float64, "Ana" → object (str).
        5. encoding='utf-8' asegura que acentos y ñ se lean bien.
        """
        self._validate_file(filepath)

        # pd.read_csv: lee CSV y devuelve DataFrame en una sola línea
        # sep=',' es el valor por defecto, no es necesario especificarlo
        df = pd.read_csv(filepath, encoding='utf-8')

        # Guardamos metadatos de la última carga
        self.last_loaded_source = os.path.basename(filepath)
        self.last_loaded_type = "CSV"

        return df

    # ─────────────────────────────────────────────────────────────── #
    #  TSV                                                             #
    # ─────────────────────────────────────────────────────────────── #
    def load_tsv(self, filepath: str) -> pd.DataFrame:
        """
        Lee un archivo TSV y lo convierte en DataFrame.

        La única diferencia con CSV es el separador:
          - CSV usa  ','  (coma)
          - TSV usa '\\t' (tabulador / Tab)

        pandas es tan flexible que pd.read_csv() puede leer
        cualquier formato separado cambiando solo el parámetro sep:
          sep=','   → CSV
          sep='\\t'  → TSV
          sep=';'   → CSV europeo
          sep='|'   → PSV (Pipe-Separated)

        Parámetros
        ----------
        filepath : str
            Ruta al archivo .tsv

        Retorna
        -------
        pd.DataFrame
        """
        self._validate_file(filepath)

        # El único cambio vs load_csv: sep='\\t' (tabulador)
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')

        self.last_loaded_source = os.path.basename(filepath)
        self.last_loaded_type = "TSV"

        return df

    # ─────────────────────────────────────────────────────────────── #
    #  JSON                                                            #
    # ─────────────────────────────────────────────────────────────── #
    def load_json(self, filepath: str) -> pd.DataFrame:
        """
        Lee un archivo JSON y lo convierte en DataFrame.

        Estructura JSON esperada — lista de objetos:
        [
          {"id": 1, "nombre": "Ana", "edad": 21},
          {"id": 2, "nombre": "Carlos", "edad": 22},
          ...
        ]

        Cada objeto JSON → una fila del DataFrame.
        Las claves del objeto → nombres de columnas.

        También acepta formato con clave raíz:
        {"datos": [...]}  →  toma la lista como registros.

        Parámetros
        ----------
        filepath : str
            Ruta al archivo .json

        Retorna
        -------
        pd.DataFrame

        ── Cómo funciona JSON en Python ─────────────────────────────
        JSON nativo Python:
          Objeto  {}  →  dict
          Array   []  →  list
          String  ""  →  str
          Number      →  int o float
          true/false  →  True/False
          null        →  None

        json.load(archivo) convierte el texto JSON en objetos Python.
        pd.DataFrame(lista_de_dicts) crea un DataFrame donde:
          - Cada diccionario es una fila
          - Las claves del diccionario son las columnas
        """
        self._validate_file(filepath)

        # Abrimos el archivo como texto y lo parseamos con json.load()
        with open(filepath, 'r', encoding='utf-8') as archivo:
            # json.load() lee el archivo y devuelve un objeto Python
            datos = json.load(archivo)

        # Manejar estructura con clave raíz: {"clave": [...datos...]}
        if isinstance(datos, dict):
            # Buscar la primera clave cuyo valor sea una lista
            for clave, valor in datos.items():
                if isinstance(valor, list):
                    datos = valor
                    break

        # pd.DataFrame(lista_de_dicts) → una fila por dict
        # Si hay claves faltantes en algún dict, pandas rellena con NaN
        df = pd.DataFrame(datos)

        self.last_loaded_source = os.path.basename(filepath)
        self.last_loaded_type = "JSON"

        return df

    # ─────────────────────────────────────────────────────────────── #
    #  Método privado de validación                                    #
    # ─────────────────────────────────────────────────────────────── #
    def _validate_file(self, filepath: str) -> None:
        """
        Verifica que el archivo existe antes de intentar cargarlo.

        Los métodos que empiezan con '_' son privados por convención
        en Python (no hay privacidad real, pero indica que no deben
        llamarse desde fuera de la clase).

        Parámetros
        ----------
        filepath : str

        Excepciones
        -----------
        FileNotFoundError : si el archivo no existe.
        ValueError : si la ruta está vacía.
        """
        if not filepath:
            raise ValueError("La ruta del archivo no puede estar vacía.")
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"No se encontró el archivo: {filepath}"
            )
