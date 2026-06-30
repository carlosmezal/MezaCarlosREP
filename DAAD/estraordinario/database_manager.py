"""
╔══════════════════════════════════════════════════════════════╗
║  database_manager.py — Módulo de Gestión PostgreSQL          ║
╚══════════════════════════════════════════════════════════════╝

RESPONSABILIDAD:
  Gestionar toda la interacción con PostgreSQL:
  conexión, desconexión, consultas SQL y conversión a DataFrames.

TECNOLOGÍAS:
  psycopg2 : adaptador oficial de PostgreSQL para Python.
             Implementa DB-API 2.0 (PEP 249), el estándar de Python
             para acceso a bases de datos relacionales.
  pandas   : convierte resultados SQL directamente a DataFrames.

FLUJO DE USO:
  1. db = DatabaseManager(host, database, user, password)
  2. db.connect()
  3. df = db.execute_query("SELECT * FROM tabla")
  4. db.disconnect()
"""

import pandas as pd
import psycopg2
from psycopg2 import OperationalError


class DatabaseManager:
    """
    Clase para gestionar la conexión y consultas a PostgreSQL.

    ── Cómo funciona psycopg2 ────────────────────────────────────
    psycopg2 actúa como "puente" entre Python y PostgreSQL:

    1. psycopg2.connect(...)    → abre una conexión TCP al servidor
    2. connection.cursor()      → crea un cursor (canal de comandos)
    3. cursor.execute(sql)      → envía la consulta al servidor
    4. cursor.fetchall()        → descarga los resultados
    5. connection.close()       → cierra la conexión TCP

    pd.read_sql_query(sql, conn) hace los pasos 2-4 automáticamente
    y además convierte los resultados directamente a DataFrame,
    usando los nombres de columnas de PostgreSQL como headers.

    Atributos
    ---------
    host     : str   IP o hostname del servidor ('localhost' = local)
    database : str   Nombre de la base de datos a usar
    user     : str   Usuario de PostgreSQL
    password : str   Contraseña del usuario
    port     : int   Puerto TCP (default PostgreSQL = 5432)
    connection : psycopg2.connection | None
    """

    def __init__(
        self,
        host: str,
        database: str,
        user: str,
        password: str,
        port: int = 5432
    ):
        """
        Inicializa el manager con los parámetros de conexión.
        NO establece la conexión aquí; eso lo hace connect().

        Parámetros
        ----------
        host     : str   Ej: 'localhost' o '192.168.1.10'
        database : str   Ej: 'universidad'
        user     : str   Ej: 'postgres' o 'admin'
        password : str   Contraseña del usuario
        port     : int   Default: 5432
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None   # Sin conexión hasta llamar connect()

    # ─────────────────────────────────────────────────────────────── #
    #  Gestión de conexión                                             #
    # ─────────────────────────────────────────────────────────────── #
    def connect(self) -> bool:
        """
        Establece la conexión con PostgreSQL.

        Retorna
        -------
        bool : True si la conexión fue exitosa.

        Excepciones
        -----------
        ConnectionError : si PostgreSQL no está disponible o
                          las credenciales son incorrectas.

        ── Qué hace psycopg2.connect() ──────────────────────────────
        Internamente realiza:
        1. Resuelve el hostname (ej: 'localhost' → 127.0.0.1)
        2. Abre una conexión TCP al puerto especificado (default 5432)
        3. Envía las credenciales al servidor
        4. PostgreSQL las verifica contra pg_hba.conf
        5. Si son correctas → devuelve un objeto Connection
        6. Si fallan → lanza OperationalError

        El objeto connection representa el "canal abierto" con la BD.
        Debe cerrarse explícitamente con disconnect() cuando se termine.
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

    # ─────────────────────────────────────────────────────────────── #
    #  Consultas SQL                                                   #
    # ─────────────────────────────────────────────────────────────── #
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL y retorna los resultados como DataFrame.

        Parámetros
        ----------
        query : str
            Consulta SQL. Ej: "SELECT * FROM estudiantes LIMIT 50"

        Retorna
        -------
        pd.DataFrame
            Una fila por registro, una columna por campo de la BD.

        Excepciones
        -----------
        ConnectionError : si no hay conexión activa.
        RuntimeError    : si la consulta tiene errores SQL.

        ── Cómo funciona pd.read_sql_query() ────────────────────────
        Esta función de pandas hace todo el trabajo pesado:

        1. Crea un cursor usando la conexión dada
        2. Ejecuta la consulta SQL: cursor.execute(query)
        3. Obtiene los nombres de columnas del cursor
        4. Descarga todos los datos: cursor.fetchall()
        5. Construye el DataFrame con esos datos y nombres
        6. Cierra el cursor

        Es equivalente a hacer esto manualmente:
        ─────────────────────────────────────────
        cursor = connection.cursor()
        cursor.execute(query)
        columnas = [desc[0] for desc in cursor.description]
        filas = cursor.fetchall()
        df = pd.DataFrame(filas, columns=columnas)
        cursor.close()
        ─────────────────────────────────────────
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

        Usa information_schema, un esquema especial de PostgreSQL
        que contiene metadatos sobre la base de datos (tablas,
        columnas, tipos, restricciones, etc.)

        Retorna
        -------
        list[str] : nombres de tablas, ordenados alfabéticamente.
        """
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        df = self.execute_query(query)
        return df['table_name'].tolist()

    def get_row_count(self, table_name: str) -> int:
        """
        Retorna el número de filas de una tabla.

        Parámetros
        ----------
        table_name : str   Nombre de la tabla (sin comillas).

        Retorna
        -------
        int : número de registros.
        """
        df = self.execute_query(f"SELECT COUNT(*) AS total FROM {table_name};")
        return int(df['total'].iloc[0])
