# 🔬 DataAnalyzer — Pipeline Multifuente de Datos

Proyecto universitario para la materia **Desarrollo de Aplicaciones para Análisis de Datos**.  
Aplicación de escritorio en Python que integra CSV, TSV, JSON, PostgreSQL y Web Scraping en un solo pipeline de análisis.

---

## ⚡ Instalación y ejecución rápida

### 1. Instalar dependencias Python

```bash
pip install pandas psycopg2-binary requests beautifulsoup4
```

> `tkinter` ya viene incluido con Python en Windows y Mac.  
> En Linux (Ubuntu/Debian): `sudo apt install python3-tk`

### 2. Configurar PostgreSQL (opcional)

Si quieres usar la fuente PostgreSQL:

```bash
# En la terminal de PostgreSQL
psql -U postgres -f sql/setup.sql
```

O manualmente en pgAdmin: abrir `sql/setup.sql` y ejecutarlo.

### 3. Ejecutar la aplicación

```bash
python main.py
```

---

## 📁 Estructura del proyecto

```
DataAnalyzerApp/
│
├── main.py               # Punto de entrada — ejecutar esto
├── gui.py                # Interfaz gráfica (MainWindow, DBDialog)
├── data_loader.py        # Carga CSV, TSV y JSON → DataFrame
├── database_manager.py   # Conexión y consultas PostgreSQL
├── web_scraper.py        # Extracción de datos web
├── data_analyzer.py      # Análisis Exploratorio de Datos (EDA)
│
├── data/
│   ├── estudiantes.csv   # Datos de ejemplo para CSV
│   ├── profesores.tsv    # Datos de ejemplo para TSV
│   └── cursos.json       # Datos de ejemplo para JSON
│
└── sql/
    └── setup.sql         # Script completo de base de datos
```

---

## 🖱️ Cómo usar cada fuente de datos

| Botón | Qué hace | Archivo de prueba |
|---|---|---|
| 📄 Cargar CSV | Abre explorador de archivos | `data/estudiantes.csv` |
| 📋 Cargar TSV | Abre explorador de archivos | `data/profesores.tsv` |
| {…} Cargar JSON | Abre explorador de archivos | `data/cursos.json` |
| 🐘 Consultar PostgreSQL | Abre ventana de conexión | Ver parámetros abajo |
| 🌐 Web Scraping | Extrae libros automáticamente | books.toscrape.com |
| 📊 Mostrar Análisis | EDA del DataFrame activo | — |

### Parámetros PostgreSQL por defecto
- Host: `localhost`
- Base de datos: `universidad`
- Usuario: `postgres`
- Puerto: `5432`
- Consulta: `SELECT * FROM estudiantes LIMIT 50;`

---

## 🛠️ Tecnologías utilizadas

- **Python 3.9+** — lenguaje base
- **pandas** — manipulación de datos y DataFrames
- **psycopg2** — conector PostgreSQL
- **requests** — peticiones HTTP
- **BeautifulSoup4** — análisis de HTML
- **Tkinter** — interfaz gráfica (incluido en Python)
- **PostgreSQL** — base de datos relacional
