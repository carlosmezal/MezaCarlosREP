

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

    def get_null_counts(self) -> dict:
        """
        Retorna la cantidad de valores nulos
        """
        return self.df.isnull().sum().to_dict()

    def get_null_percentages(self) -> dict:
        """
        Retorna el porcentaje de valores nulos
        """
        total_filas = len(self.df)
        conteos = self.get_null_counts()
        return {
            col: round((conteo / total_filas) * 100, 2)
            for col, conteo in conteos.items()
        }

    def get_descriptive_stats(self) -> str:
        """
        Retorna las estadísticas
        """
        return self.df.describe(include='all').to_string()

    def get_numeric_stats(self) -> pd.DataFrame:
        
        return self.df.describe()

    def get_full_summary(self) -> str:
        """
        Genera el reporte EDA
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

    def get_head(self, n: int = 5) -> pd.DataFrame:
        """
        Retorna las primeras n filas
        """
        return self.df.head(n)

    def get_value_counts(self, column: str) -> pd.Series:
        """
        Retorna la frecuencia de cada valor único en una columna.

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

        """
        numericas = self.df.select_dtypes(include='number')
        if numericas.empty:
            raise ValueError("No hay columnas numéricas para calcular correlación.")
        return numericas.corr()
