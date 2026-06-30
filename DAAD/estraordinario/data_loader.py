"""
  Cargar archivos locales 
"""

import os
import json
import pandas as pd


class DataLoader:
  

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

        """
        self._validate_file(filepath)

        # pd.read_csv: lee CSV y devuelve DataFrame en una sola línea
        # sep=',' es el valor por defecto, no es necesario especificarlo
        df = pd.read_csv(filepath, encoding='utf-8')

        # Guardamos metadatos de la última carga
        self.last_loaded_source = os.path.basename(filepath)
        self.last_loaded_type = "CSV"

        return df

    def load_tsv(self, filepath: str) -> pd.DataFrame:
        """
        Lee un archivo TSV y lo convierte en DataFrame.

        """
        self._validate_file(filepath)

        # El único cambio vs load_csv: sep='\\t' (tabulador)
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')

        self.last_loaded_source = os.path.basename(filepath)
        self.last_loaded_type = "TSV"

        return df

    def load_json(self, filepath: str) -> pd.DataFrame:
        """
        Lee un archivo JSON y lo convierte en DataFrame.

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

    def _validate_file(self, filepath: str) -> None:
        
        if not filepath:
            raise ValueError("La ruta del archivo no puede estar vacía.")
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"No se encontró el archivo: {filepath}"
            )
