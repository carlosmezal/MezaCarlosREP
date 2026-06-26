"""
╔══════════════════════════════════════════════════════════════╗
║  web_scraper.py — Módulo de Web Scraping                     ║
╚══════════════════════════════════════════════════════════════╝

RESPONSABILIDAD:
  Extraer datos estructurados de páginas web públicas usando
  peticiones HTTP y análisis del árbol HTML.

TECNOLOGÍAS:
  requests      : realiza peticiones HTTP (GET, POST, etc.)
  BeautifulSoup : analiza y navega la estructura HTML
  pandas        : almacena los datos extraídos en DataFrames

SITIO OBJETIVO:
  books.toscrape.com — sitio diseñado ESPECÍFICAMENTE para
  practicar web scraping. Es completamente legal de scrapear.
  Contiene un catálogo de ~1,000 libros ficticios.

PIPELINE DE WEB SCRAPING:
  URL  →  requests.get()  →  HTML crudo
       →  BeautifulSoup()  →  árbol navegable
       →  find_all()       →  lista de elementos
       →  extracción        →  lista de dicts
       →  pd.DataFrame()   →  DataFrame
"""

import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


class WebScraper:
    """
    Clase para extraer información de páginas web públicas.

    ── Cómo funciona requests ────────────────────────────────────
    requests es la biblioteca HTTP más popular de Python.
    Simplifica enormemente las peticiones web:

      response = requests.get(url)
        ↓
      Envía: GET /ruta HTTP/1.1\\nHost: sitio.com\\n...
        ↓
      Recibe: HTTP/1.1 200 OK\\n...\\n<html>...</html>

    Atributos importantes del objeto response:
      response.status_code  → código HTTP (200=OK, 404=No encontrado)
      response.text         → contenido HTML como string
      response.content      → contenido como bytes
      response.encoding     → codificación detectada (utf-8, latin-1...)
      response.headers      → cabeceras HTTP de respuesta

    ── Cómo funciona BeautifulSoup ──────────────────────────────
    BeautifulSoup analiza el texto HTML y construye un árbol
    de objetos navegables similar al DOM del navegador:

      <html>
        <body>
          <article class="producto">
            <h3><a title="Libro X">...</a></h3>
            <p class="precio">£12.99</p>
          </article>
        </body>
      </html>

    soup.find('article')              → primer <article>
    soup.find_all('p', class_='precio') → todos los <p class="precio">
    elemento['class']                 → lista de clases CSS
    elemento['title']                 → atributo title
    elemento.text                     → texto visible

    Atributos
    ---------
    pages   : int   Número de páginas a scrapear (1 página = 20 libros)
    headers : dict  Cabeceras HTTP para simular un navegador real
    data    : list  Lista de dicts con los libros extraídos
    """

    # URL base del catálogo de books.toscrape.com
    BASE_URL = "https://books.toscrape.com/catalogue/"

    # Las calificaciones están como palabras en las clases CSS.
    # Este diccionario las convierte a números.
    RATING_MAP = {
        "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
    }

    def __init__(self, pages: int = 2):
        """
        Parámetros
        ----------
        pages : int
            Páginas a scrapear (default=2). Cada página tiene 20 libros.
            Máximo recomendado: 5 (para no sobrecargar el servidor).
        """
        self.pages = max(1, min(pages, 10))   # Limitar entre 1 y 10
        self.data: list = []

        # User-Agent: le dice al servidor qué navegador somos.
        # Sin esto, algunos sitios bloquean las peticiones de scripts.
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    # ─────────────────────────────────────────────────────────────── #
    #  Paso 1: Descargar HTML                                          #
    # ─────────────────────────────────────────────────────────────── #
    def _fetch_page(self, url: str) -> BeautifulSoup:
        """
        Descarga el HTML de una URL y lo convierte en objeto BeautifulSoup.

        Este es un método privado (prefijo '_'). Solo lo usan los otros
        métodos de esta clase, no el código externo.

        Parámetros
        ----------
        url : str   URL completa de la página

        Retorna
        -------
        BeautifulSoup   Árbol HTML navegable

        Excepciones
        -----------
        requests.exceptions.ConnectionError : sin conexión a internet
        requests.exceptions.Timeout         : servidor no respondió
        requests.exceptions.HTTPError       : error 4xx o 5xx del servidor

        ── Detalle del proceso ───────────────────────────────────────
        1. requests.get(url, headers=..., timeout=15)
           → Abre conexión TCP al servidor
           → Envía petición HTTP GET con las cabeceras especificadas
           → timeout=15 → si no responde en 15s, lanza Timeout

        2. response.raise_for_status()
           → Si status_code >= 400 lanza HTTPError automáticamente
           → 200 OK → no hace nada
           → 404 Not Found → lanza HTTPError

        3. BeautifulSoup(response.text, 'html.parser')
           → Parsea el HTML string y construye el árbol de objetos
           → 'html.parser' es el parser incluido en Python estándar
           → Alternativa: 'lxml' (más rápido, requiere instalación)
        """
        response = requests.get(url, headers=self.headers, timeout=15)
        # Si el servidor devuelve error (4xx, 5xx), lanza excepción
        response.raise_for_status()

        # Construir árbol HTML navegable
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    # ─────────────────────────────────────────────────────────────── #
    #  Paso 2: Extraer datos del HTML                                  #
    # ─────────────────────────────────────────────────────────────── #
    def _parse_books(self, soup: BeautifulSoup) -> list:
        """
        Extrae información de libros del árbol BeautifulSoup.

        Estructura HTML de books.toscrape.com (simplificada):
        ─────────────────────────────────────────────────────
        <article class="product_pod">
            <h3>
              <a title="Nombre completo del libro" href="...">...</a>
            </h3>
            <div class="product_price">
              <p class="price_color">£12.99</p>
              <p class="availability">In stock</p>
            </div>
            <p class="star-rating Three">  ← Three = 3 estrellas
        </article>
        ─────────────────────────────────────────────────────

        Parámetros
        ----------
        soup : BeautifulSoup   Árbol HTML de una página de catálogo

        Retorna
        -------
        list[dict]   Lista con un dict por libro
        """
        libros = []

        # find_all(tag, class_=...) retorna una lista de TODOS los
        # elementos que coincidan. Cada artículo es un libro.
        articulos = soup.find_all('article', class_='product_pod')

        for articulo in articulos:
            try:
                # ── Título ──────────────────────────────────────────── #
                # El título completo está en el atributo 'title' del <a>
                # (el texto visible está truncado)
                titulo_tag = articulo.find('h3').find('a')
                titulo = titulo_tag.get('title', 'Sin título')

                # ── Precio ──────────────────────────────────────────── #
                precio_tag = articulo.find('p', class_='price_color')
                precio_texto = precio_tag.text.strip()
                # re.sub elimina todo lo que NO sea dígito o punto
                # Así manejamos: '£', 'Â£', '€' y otros símbolos
                precio_limpio = re.sub(r'[^\d.]', '', precio_texto)
                precio = float(precio_limpio) if precio_limpio else 0.0

                # ── Calificación ─────────────────────────────────────── #
                # La calificación está como clase CSS: "star-rating Three"
                # tag['class'] devuelve lista: ['star-rating', 'Three']
                rating_tag = articulo.find('p', class_='star-rating')
                clases = rating_tag.get('class', [])
                # La segunda clase CSS es la calificación en texto
                rating_texto = clases[1] if len(clases) > 1 else "Zero"
                rating = self.RATING_MAP.get(rating_texto, 0)

                # ── Disponibilidad ───────────────────────────────────── #
                disp_tag = articulo.find('p', class_='availability')
                disponibilidad = disp_tag.text.strip() if disp_tag else "N/A"

                libros.append({
                    'titulo':          titulo,
                    'precio_gbp':      precio,
                    'calificacion':    rating,
                    'disponibilidad':  disponibilidad
                })

            except (AttributeError, ValueError):
                # Si un elemento no tiene la estructura esperada, lo omitimos
                continue

        return libros

    # ─────────────────────────────────────────────────────────────── #
    #  Método público principal                                        #
    # ─────────────────────────────────────────────────────────────── #
    def scrape(self) -> pd.DataFrame:
        """
        Orquesta el scraping de múltiples páginas.

        Itera sobre las páginas configuradas, descarga el HTML de cada
        una, extrae los libros y los acumula en una lista que al final
        convierte en DataFrame.

        Retorna
        -------
        pd.DataFrame
            Columnas: titulo, precio_gbp, calificacion, disponibilidad
            Filas: un libro por fila (20 × pages libros aprox.)

        Excepciones
        -----------
        ValueError : si no se pudieron extraer datos (sin conexión, etc.)
        """
        self.data = []   # Resetear lista antes de scrapear

        for num_pagina in range(1, self.pages + 1):
            # Construir URL de la página: page-1.html, page-2.html...
            url = f"{self.BASE_URL}page-{num_pagina}.html"

            # Paso 1: Descargar HTML
            soup = self._fetch_page(url)

            # Paso 2: Extraer libros de esta página
            libros_pagina = self._parse_books(soup)

            # Acumular en la lista general
            self.data.extend(libros_pagina)

        if not self.data:
            raise ValueError(
                "No se extrajeron datos. "
                "Verifica la conexión a internet."
            )

        # Paso 3: Convertir lista de dicts → DataFrame
        df = pd.DataFrame(self.data)

        # Agregar columna de número de página para referencia
        items_por_pagina = len(self.data) // self.pages if self.pages > 0 else 20
        df.insert(
            0, 'pagina',
            [(i // items_por_pagina) + 1 for i in range(len(df))]
        )

        return df

    def get_items_count(self) -> int:
        """Retorna el número de ítems extraídos en el último scraping."""
        return len(self.data)