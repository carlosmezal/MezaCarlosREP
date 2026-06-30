

import requests
from bs4 import BeautifulSoup
import pandas as pd


class WebScraper:
    """
    Extrae datos de Pokémon usando la PokéAPI y BeautifulSoup.

    """

    API_URL = "https://pokeapi.co/api/v2/pokemon/{}"

    # IDs de Pokémon famosos a consultar
    POKEMON_IDS = [
        1, 2, 3, 4, 5, 6, 7, 8, 9,        # Kanto starters
        25, 26,                             # Pikachu, Raichu
        39, 52, 54, 63, 66, 94,            # Clásicos
        113, 130, 131, 132, 133, 143,      # Iconicos
        144, 145, 146, 149, 150, 151,      # Legendarios Gen 1
        196, 197, 245, 249, 250,           # Gen 2
        282, 330, 350, 384,                # Gen 3
        448, 483, 484, 487,                # Gen 4
        644, 646,                          # Gen 5
    ]

    def __init__(self, limit: int = 20):
        """
        Parámetros
        ----------
        limit : int
            Cuántos Pokémon consultar (default 20, máx = len(POKEMON_IDS)).
            Más Pokémon = más tiempo de carga (1 petición HTTP por Pokémon).
        """
        self.limit = max(1, min(limit, len(self.POKEMON_IDS)))
        self.headers = {
            "User-Agent": "DataAnalyzer/1.0 (proyecto universitario)"
        }
        self.data: list = []

    # ─────────────────────────────────────────────────────────── #
    #  Paso 1: Obtener datos JSON de un Pokémon                   #
    # ─────────────────────────────────────────────────────────── #
    def _fetch_pokemon(self, pokemon_id: int) -> dict:
        """
        Consulta la PokéAPI y retorna los datos de un Pokémon.


        """
        url = self.API_URL.format(pokemon_id)
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()

        data = response.json()   # JSON → dict Python

        # Extraer tipos (puede haber 1 o 2)
        tipos = [t["type"]["name"].capitalize() for t in data["types"]]
        tipo1 = tipos[0] if len(tipos) > 0 else ""
        tipo2 = tipos[1] if len(tipos) > 1 else ""

        # Convertir lista de stats a dict {nombre: valor}
        stats = {
            s["stat"]["name"]: s["base_stat"]
            for s in data["stats"]
        }

        return {
            "numero":          data["id"],
            "nombre":          data["name"].capitalize(),
            "tipo1":           tipo1,
            "tipo2":           tipo2,
            "hp":              stats.get("hp", 0),
            "ataque":          stats.get("attack", 0),
            "defensa":         stats.get("defense", 0),
            "sp_ataque":       stats.get("special-attack", 0),
            "sp_defensa":      stats.get("special-defense", 0),
            "velocidad":       stats.get("speed", 0),
            "exp_base":        data.get("base_experience", 0),
            "total_stats":     sum(stats.values()),
        }

    # ─────────────────────────────────────────────────────────── #
    #  Paso 2: Convertir dicts a tabla HTML                       #
    # ─────────────────────────────────────────────────────────── #
    def _build_html_table(self, pokemon_list: list) -> str:
        """
        Construye una tabla HTML con los datos de los Pokémon.

        Esto es necesario para que BeautifulSoup tenga HTML que parsear.

        Retorna
        -------
        str : string con HTML completo de la tabla
        """
        if not pokemon_list:
            return "<table><tbody></tbody></table>"

        columnas = list(pokemon_list[0].keys())

        # Encabezados <th>
        headers_html = "".join(f"<th>{col}</th>" for col in columnas)

        # Filas <tr><td>...</td></tr>
        filas_html = ""
        for p in pokemon_list:
            celdas = "".join(f"<td>{p[col]}</td>" for col in columnas)
            filas_html += f"<tr>{celdas}</tr>"

        return f"""
        <html><body>
          <table id="pokedex">
            <thead><tr>{headers_html}</tr></thead>
            <tbody>{filas_html}</tbody>
          </table>
        </body></html>
        """

    # ─────────────────────────────────────────────────────────── #
    #  Paso 3: Parsear la tabla HTML con BeautifulSoup            #
    # ─────────────────────────────────────────────────────────── #
    def _parse_html_table(self, html: str) -> list:
        """
        Usa BeautifulSoup para extraer datos de la tabla HTML.

        ── Cómo funciona este parsing ────────────────────────────
        soup.find('table', id='pokedex') → encuentra la tabla
        thead tr th                       → nombres de columnas
        tbody tr                          → filas de datos
        td.text.strip()                   → valor de cada celda

        Esto demuestra el uso correcto de BeautifulSoup para
        navegar la estructura HTML y extraer datos de celdas.
        """
        soup = BeautifulSoup(html, "html.parser")
        tabla = soup.find("table", id="pokedex")

        # Extraer nombres de columnas del <thead>
        columnas = [
            th.text.strip()
            for th in tabla.find("thead").find_all("th")
        ]

        # Extraer filas del <tbody>
        resultado = []
        for fila in tabla.find("tbody").find_all("tr"):
            celdas = [td.text.strip() for td in fila.find_all("td")]
            if celdas:
                # Zip columnas con valores → dict
                resultado.append(dict(zip(columnas, celdas)))

        return resultado

    # ─────────────────────────────────────────────────────────── #
    #  Método público principal                                   #
    # ─────────────────────────────────────────────────────────── #
    def scrape(self) -> pd.DataFrame:
        """
        Orquesta todo el proceso: API → HTML → BeautifulSoup → DataFrame.

       
        """
        self.data = []
        ids_a_consultar = self.POKEMON_IDS[:self.limit]

        # ── Paso 1: Consultar la API por cada Pokémon ──────── #
        for pokemon_id in ids_a_consultar:
            try:
                pokemon = self._fetch_pokemon(pokemon_id)
                self.data.append(pokemon)
            except Exception:
                # Si un Pokémon falla, continuamos con el siguiente
                continue

        if not self.data:
            raise ValueError(
                "No se pudo conectar a la PokéAPI.\n"
                "Verifica tu conexión a internet: https://pokeapi.co"
            )

        # ── Paso 2: Construir tabla HTML con los datos ─────── #
        html = self._build_html_table(self.data)

        # ── Paso 3: Parsear con BeautifulSoup ─────────────── #
        registros = self._parse_html_table(html)

        # ── Paso 4: Convertir a DataFrame ─────────────────── #
        df = pd.DataFrame(registros)

        # Convertir columnas numéricas a sus tipos correctos
        cols_numericas = [
            "numero", "hp", "ataque", "defensa",
            "sp_ataque", "sp_defensa", "velocidad",
            "exp_base", "total_stats"
        ]
        for col in cols_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def get_items_count(self) -> int:
        """Retorna el número de Pokémon obtenidos en el último scraping."""
        return len(self.data)
