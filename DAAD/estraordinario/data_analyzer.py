

import pandas as pd


class DataAnalyzer:
   

    def __init__(self, df: pd.DataFrame):
        
        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                f"Se esperaba un pandas DataFrame, "
                f"se recibió: {type(df).__name__}"
            )
        if df.empty:
            raise ValueError("El DataFrame está vacío (0 filas o 0 columnas).")

        self.df = df   # Almacenamos el DataFrame

    #  Métricas                               #
    def get_shape(self) -> dict:
        """
        Retorna las dimensiones del DataFrame.

        """
        filas, cols = self.df.shape
        return {"registros": filas, "columnas": cols}

    def get_columns(self) -> list:
        """
        Retorna los nombres de las columnas.

        """
        return list(self.df.columns)

    def get_dtypes(self) -> dict:
        """
        Retorna el tipo de dato de cada columna.

        """
        return {col: str(dtype) for col, dtype in self.df.dtypes.items()}

    # ─────────────────────────────────────────────────────────────── #
    #  Análisis de valores nulos (NaN)                                 #
    # ─────────────────────────────────────────────────────────────── #
    def get_null_counts(self) -> dict:
        """
        Retorna la cantidad de valores nulos (NaN) por columna.

        ── Cómo funciona ────────────────────────────────────────────
        df.isnull()     → DataFrame booleano: True donde hay NaN
                          (mismo tamaño que df)
        .sum()          → suma los True de cada columna
                          (True=1, False=0)
        .to_dict()      → convierte Series a dict Python

        Ejemplo:
          df:
            nombre  edad
            "Ana"   21
            NaN     22    ← NaN en nombre
            "Luis"  NaN   ← NaN en edad

          df.isnull():
            nombre  edad
            False   False
            True    False
            False   True

          .sum() → {"nombre": 1, "edad": 1}

        Retorna
        -------
        dict : {columna: cantidad_de_nulos}
        """
        return self.df.isnull().sum().to_dict()

    def get_null_percentages(self) -> dict:
        """
        Retorna el porcentaje de valores nulos por columna.

        Retorna
        -------
        dict : {columna: porcentaje_nulos_redondeado}
        """
        total_filas = len(self.df)
        conteos = self.get_null_counts()
        return {
            col: round((conteo / total_filas) * 100, 2)
            for col, conteo in conteos.items()
        }

    # ─────────────────────────────────────────────────────────────── #
    #  Estadísticas descriptivas                                       #
    # ─────────────────────────────────────────────────────────────── #
    def get_descriptive_stats(self) -> str:
        """
        Retorna las estadísticas descriptivas del DataFrame.

        df.describe() calcula para cada columna numérica:
          count  → número de valores NO nulos
          mean   → media aritmética: Σx / n
          std    → desviación estándar: dispersión de los datos
          min    → valor mínimo
          25%    → 1er cuartil: 25% de datos están por debajo
          50%    → mediana: valor central (divide datos en mitades)
          75%    → 3er cuartil: 75% de datos están por debajo
          max    → valor máximo

        include='all' añade columnas de tipo object (texto):
          count   → valores no nulos
          unique  → valores únicos
          top     → valor más frecuente
          freq    → frecuencia del valor más frecuente

        Retorna
        -------
        str : tabla formateada de estadísticas
        """
        return self.df.describe(include='all').to_string()

    def get_numeric_stats(self) -> pd.DataFrame:
        """
        Retorna estadísticas solo de columnas numéricas como DataFrame.
        Útil cuando se quiere el resultado como DataFrame, no como string.
        """
        return self.df.describe()

    # ─────────────────────────────────────────────────────────────── #
    #  Resumen completo                                                 #
    # ─────────────────────────────────────────────────────────────── #
    def get_full_summary(self) -> str:
        """
        Genera un reporte completo de EDA en formato texto.

        Combina toda la información relevante en un solo reporte
        formateado, listo para mostrar en la interfaz.

        Retorna
        -------
        str : Reporte completo de EDA con secciones claramente delimitadas.
        """
        shape = self.get_shape()
        dtypes = self.get_dtypes()
        nulls = self.get_null_counts()
        null_pct = self.get_null_percentages()

        lineas = [
            "═" * 58,
            "   ANÁLISIS EXPLORATORIO DE DATOS  (EDA)",
            "═" * 58,
            f"   Registros totales : {shape['registros']:,}",
            f"   Columnas          : {shape['columnas']}",
            "",
            "─" * 58,
            f"   {'COLUMNA':<24} {'TIPO':<12} {'NULOS':>6}  {'%':>6}",
            "─" * 58,
        ]

        # Una línea por columna con tipo, nulos y porcentaje
        for col in self.get_columns():
            tipo = dtypes.get(col, "?")
            n_nulos = nulls.get(col, 0)
            pct = null_pct.get(col, 0.0)

            # Indicador visual de calidad de la columna
            if pct == 0:
                indicador = "✓"
            elif pct < 10:
                indicador = "~"
            else:
                indicador = "✗"

            lineas.append(
                f"   {indicador} {col:<22} {tipo:<12} "
                f"{n_nulos:>6}  {pct:>5.1f}%"
            )

        # Total de valores nulos en todo el DataFrame
        total_nulos = sum(nulls.values())
        total_celdas = shape['registros'] * shape['columnas']
        pct_total = round((total_nulos / total_celdas) * 100, 2)

        lineas += [
            "─" * 58,
            f"   Total nulos: {total_nulos:,} / {total_celdas:,} "
            f"celdas ({pct_total}%)",
            "",
            "─" * 58,
            "   ESTADÍSTICAS DESCRIPTIVAS",
            "─" * 58,
            self.get_descriptive_stats(),
            "═" * 58,
        ]

        return "\n".join(lineas)

    # ─────────────────────────────────────────────────────────────── #
    #  Métodos adicionales de utilidad                                 #
    # ─────────────────────────────────────────────────────────────── #
    def get_head(self, n: int = 5) -> pd.DataFrame:
        """
        Retorna las primeras n filas del DataFrame.

        df.head(n) es el método más usado para previsualizar datos.
        Por defecto n=5 (las primeras 5 filas).
        """
        return self.df.head(n)

    def get_value_counts(self, column: str) -> pd.Series:
        """
        Retorna la frecuencia de cada valor único en una columna.

        Muy útil para columnas categóricas (carrera, estado, etc.)

        df[col].value_counts() cuenta cuántas veces aparece cada valor
        y los ordena de mayor a menor frecuencia.

        Parámetros
        ----------
        column : str   Nombre de la columna a analizar.

        Retorna
        -------
        pd.Series : índice = valores únicos, datos = frecuencias
        """
        if column not in self.df.columns:
            raise ValueError(
                f"La columna '{column}' no existe. "
                f"Columnas disponibles: {list(self.df.columns)}"
            )
        return self.df[column].value_counts()

    def get_correlation_matrix(self) -> pd.DataFrame:
        """
        Retorna la matriz de correlación de columnas numéricas.

        La correlación mide la relación lineal entre dos variables:
          1.0  → correlación perfecta positiva
          0.0  → sin correlación lineal
         -1.0  → correlación perfecta negativa

        df.select_dtypes(include='number') → solo columnas numéricas
        .corr() → calcula la matriz de correlación de Pearson
        """
        numericas = self.df.select_dtypes(include='number')
        if numericas.empty:
            raise ValueError("No hay columnas numéricas para calcular correlación.")
        return numericas.corr()
