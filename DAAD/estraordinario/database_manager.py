"""

  Gestiona toda la interacción con PostgreSQL

"""

import pandas as pd
import psycopg2
from psycopg2 import OperationalError


class DatabaseManager:
    """
    Clase para gestionar la conexión y consultas a PostgreSQL.

    """

    def __init__(
        self,
        host: str,
        database: str,
        user: str,
        password: str,
        port: int = 5432
    ):
  
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None   # Sin conexión hasta llamar connect()

    def connect(self) -> bool:
        """
        Establece la conexión con PostgreSQL.

        """
        try:
            # psycopg2.connect() toma los parámetros como keywords
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                connect_timeout=6   # evita que la app se quede colgada
                                    # indefinidamente si el host no responde
            )
            # autocommit=True para consultas SELECT (no necesita commit)
            self.connection.autocommit = True
            return True

        except OperationalError as e:
            # OperationalError = no se pudo conectar al servidor
            raise ConnectionError(
                f"Error al conectar con PostgreSQL:\n"
                f"Host: {self.host}, DB: {self.database}, "
                f"User: {self.user}, Port: {self.port}\n"
                f"Detalle: {e}"
            )

    def disconnect(self):
        """
        Cierra la conexión con PostgreSQL y libera recursos.
        Siempre llamar esto cuando se termina de usar la BD.
        """
        if self.connection and not self.connection.closed:
            self.connection.close()
        self.connection = None

    def is_connected(self) -> bool:
        """
        Verifica si la conexión está activa.

        connection.closed retorna:
          0 → conexión abierta
          1 → conexión cerrada normalmente
          2 → conexión cerrada por error
        """
        return (
            self.connection is not None
            and self.connection.closed == 0
        )

    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL y retorna los resultados como DataFrame.

        
        """
        if not self.is_connected():
            raise ConnectionError(
                "No hay conexión activa. Llama a connect() primero."
            )

        try:
            # pd.read_sql_query: ejecuta SQL y devuelve DataFrame
            df = pd.read_sql_query(query, self.connection)
            return df

        except Exception as e:
            raise RuntimeError(
                f"Error al ejecutar la consulta SQL:\n{query}\nDetalle: {e}"
            )

    def get_tables(self) -> list:
        """
        Retorna los nombres de todas las tablas públicas en la BD.

        """
        df = self.execute_query(query)
        return df['table_name'].tolist()

    def get_row_count(self, table_name: str) -> int:
    
        df = self.execute_query(f"SELECT COUNT(*) AS total FROM {table_name};")
        return int(df['total'].iloc[0])
