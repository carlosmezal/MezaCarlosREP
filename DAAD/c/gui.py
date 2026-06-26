"""
╔══════════════════════════════════════════════════════════════╗
║  gui.py — Interfaz Gráfica (Tkinter)                         ║
╚══════════════════════════════════════════════════════════════╝

RESPONSABILIDAD:
  Manejar toda la interfaz gráfica: ventana, botones, tabla,
  área de análisis y eventos del usuario.

PATRÓN DE DISEÑO:
  MVC simplificado (Model-View-Controller):
  ┌─────────────────────────────────────────────────────┐
  │  Model      : DataLoader, DatabaseManager, WebScraper│
  │               DataAnalyzer                          │
  │  View       : widgets de Tkinter (botones, tabla...) │
  │  Controller : métodos _on_*() que manejan eventos   │
  └─────────────────────────────────────────────────────┘

COMPONENTES TKINTER USADOS:
  tk.Tk()         → ventana principal de la aplicación
  tk.Frame        → contenedor rectangular para agrupar widgets
  ttk.Button      → botón con estilo moderno
  ttk.Treeview    → tabla con filas y columnas (para DataFrames)
  tk.Text         → área de texto multilínea con scroll
  ttk.Scrollbar   → barra de desplazamiento
  tk.Label        → texto estático
  ttk.Entry       → campo de texto para entrada del usuario
  tk.Toplevel     → ventana emergente (modal)
  filedialog      → diálogo del SO para seleccionar archivos
  messagebox      → ventanas de alerta / confirmación / error

LAYOUT (distribución de la ventana):
  ┌──────────────────────────────────────────────────────────┐
  │  HEADER: título de la aplicación                         │
  ├──────────────┬───────────────────────────────────────────┤
  │  SIDEBAR:    │  TABLA: ttk.Treeview con DataFrames        │
  │  Botones de  │  (área superior con scroll)               │
  │  fuentes de  ├───────────────────────────────────────────┤
  │  datos       │  LOG: Text widget con análisis y mensajes  │
  │  + Análisis  │  (área inferior con scroll)               │
  ├──────────────┴───────────────────────────────────────────┤
  │  STATUSBAR: mensajes de estado del sistema               │
  └──────────────────────────────────────────────────────────┘
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import threading

from data_loader import DataLoader
from database_manager import DatabaseManager
from web_scraper import WebScraper
from data_analyzer import DataAnalyzer


# ══════════════════════════════════════════════════════════════════ #
#  CLASE PRINCIPAL: MainWindow                                       #
# ══════════════════════════════════════════════════════════════════ #
class MainWindow:
    """
    Ventana principal de la aplicación DataAnalyzer.

    Esta clase es responsable de:
      - Crear y configurar la ventana principal (tk.Tk)
      - Construir todos los widgets (botones, tabla, log)
      - Manejar los eventos del usuario (_on_* methods)
      - Coordinar los módulos de datos (DataLoader, etc.)
      - Actualizar la tabla y el log con los resultados

    Atributos
    ---------
    root        : tk.Tk          Ventana raíz de Tkinter
    loader      : DataLoader     Para cargar CSV/TSV/JSON
    current_df  : pd.DataFrame   DataFrame actualmente visible
    tree        : ttk.Treeview   Tabla donde se muestran los datos
    txt_log     : tk.Text        Área de log y análisis
    lbl_status  : tk.Label       Barra de estado inferior
    """

    # ── Configuración de la aplicación ──────────────────────────── #
    TITLE    = "🔬  DataAnalyzer — Pipeline Multifuente de Datos"
    GEOMETRY = "1250x740"

    # ── Paleta de colores ────────────────────────────────────────── #
    C_BG       = "#1a1b2e"   # Fondo principal oscuro
    C_SIDEBAR  = "#16213e"   # Panel lateral
    C_HEADER   = "#0f3460"   # Encabezado
    C_BTN      = "#533483"   # Botón normal (morado)
    C_BTN_HOV  = "#7b52ab"   # Botón hover
    C_BTN_GRN  = "#1b6ca8"   # Botón acción positiva (azul)
    C_BTN_CLR  = "#374151"   # Botón limpiar (gris)
    C_TEXT     = "#e2e8f0"   # Texto principal
    C_SUB      = "#94a3b8"   # Texto secundario
    C_ACCENT   = "#c084fc"   # Color acento (lila)
    C_OK       = "#10b981"   # Verde éxito
    C_ERR      = "#ef4444"   # Rojo error
    C_WARN     = "#f59e0b"   # Amarillo advertencia
    C_TBL_HDR  = "#1e3a5f"   # Encabezado de tabla
    C_ROW_A    = "#1a1b2e"   # Fila impar
    C_ROW_B    = "#1e2039"   # Fila par
    C_LOG_BG   = "#0d0d1a"   # Fondo del área de log

    def __init__(self):
        """Inicializa la aplicación, crea la ventana y construye la UI."""
        # ── Modelos de datos ─────────────────────────────────────── #
        self.loader     = DataLoader()
        self.current_df = None   # DataFrame actualmente visible en tabla

        # ── Ventana principal ────────────────────────────────────── #
        # tk.Tk() crea la ventana raíz. Solo puede haber UNA por app.
        self.root = tk.Tk()
        self.root.title(self.TITLE)
        self.root.geometry(self.GEOMETRY)
        self.root.configure(bg=self.C_BG)
        self.root.minsize(900, 600)

        # Configurar el estilo ttk (widgets modernos)
        self._setup_styles()

        # Construir toda la interfaz
        self._build_ui()

    # ================================================================ #
    #  CONFIGURACIÓN DE ESTILOS TTK                                    #
    # ================================================================ #
    def _setup_styles(self):
        """
        Configura estilos personalizados para widgets ttk.

        ttk.Style permite cambiar la apariencia de widgets modernos.
        theme_use('clam') activa el tema 'clam' que tiene mejor
        soporte para personalización de colores en Windows y Linux.

        La sintaxis es: style.configure("NombreWidget", propiedad=valor)
        Los nombres de estilo siguen el patrón: "Nombre.Tipo" o "Tipo"
        """
        style = ttk.Style()
        style.theme_use('clam')

        # Estilo del Treeview (tabla de datos)
        style.configure(
            "Treeview",
            background=self.C_ROW_A,
            foreground=self.C_TEXT,
            fieldbackground=self.C_ROW_A,
            rowheight=26,
            font=("Consolas", 9)
        )
        # Encabezado del Treeview
        style.configure(
            "Treeview.Heading",
            background=self.C_TBL_HDR,
            foreground=self.C_ACCENT,
            font=("Segoe UI", 9, "bold"),
            relief="flat"
        )
        # Fila seleccionada
        style.map(
            "Treeview",
            background=[("selected", "#4a1d96")],
            foreground=[("selected", "#ffffff")]
        )

        # Scrollbars
        style.configure(
            "Vertical.TScrollbar",
            background=self.C_SIDEBAR,
            troughcolor=self.C_BG,
            arrowcolor=self.C_SUB
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=self.C_SIDEBAR,
            troughcolor=self.C_BG,
            arrowcolor=self.C_SUB
        )

        # Separador
        style.configure(
            "TSeparator",
            background=self.C_SUB
        )

    # ================================================================ #
    #  CONSTRUCCIÓN DE LA INTERFAZ                                     #
    # ================================================================ #
    def _build_ui(self):
        """Llama a los constructores de cada sección de la interfaz."""
        self._build_header()    # Barra superior con título
        self._build_body()      # Sidebar + área de datos
        self._build_statusbar() # Barra inferior de estado

    # ── Encabezado ──────────────────────────────────────────────── #
    def _build_header(self):
        """
        Barra superior con el título de la aplicación.

        tk.Frame es el contenedor básico de Tkinter.
          bg       → color de fondo
          height   → altura fija en píxeles
        pack(fill=tk.X) → estira el frame horizontalmente
        pack_propagate(False) → evita que el frame se encoja al contenido
        """
        header = tk.Frame(self.root, bg=self.C_HEADER, height=52)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🔬  DataAnalyzer  —  Pipeline Multifuente de Datos",
            font=("Segoe UI", 14, "bold"),
            bg=self.C_HEADER,
            fg="#dbeafe"
        ).pack(side=tk.LEFT, padx=18, pady=10)

        tk.Label(
            header,
            text="CSV  ·  TSV  ·  JSON  ·  PostgreSQL  ·  Web Scraping",
            font=("Segoe UI", 9),
            bg=self.C_HEADER,
            fg="#93c5fd"
        ).pack(side=tk.RIGHT, padx=18, pady=16)

    # ── Cuerpo: sidebar + área principal ────────────────────────── #
    def _build_body(self):
        """Contenedor principal que divide sidebar y área de datos."""
        body = tk.Frame(self.root, bg=self.C_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self._build_sidebar(body)     # Panel izquierdo de botones
        self._build_main_area(body)   # Panel derecho de datos

    # ── Panel lateral de botones ─────────────────────────────────── #
    def _build_sidebar(self, parent):
        """
        Panel izquierdo con botones de carga de datos y análisis.

        pack(side=tk.LEFT, fill=tk.Y) → anclar a la izquierda
        y estirar verticalmente para ocupar toda la altura.
        """
        sidebar = tk.Frame(parent, bg=self.C_SIDEBAR, width=195)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        sidebar.pack_propagate(False)  # Mantener ancho fijo

        # ── Sección: Fuentes de datos ──────────────────────────── #
        tk.Label(
            sidebar,
            text="  FUENTES DE DATOS",
            font=("Segoe UI", 8, "bold"),
            bg=self.C_SIDEBAR, fg=self.C_SUB, anchor=tk.W
        ).pack(fill=tk.X, pady=(18, 4), padx=8)

        # Definición de los botones de fuentes de datos
        fuentes = [
            ("📄   Cargar CSV",         self._on_load_csv,      self.C_BTN),
            ("📋   Cargar TSV",         self._on_load_tsv,      self.C_BTN),
            ("{…}  Cargar JSON",         self._on_load_json,     self.C_BTN),
            ("🐘   Consultar PostgreSQL", self._on_query_postgres, self.C_BTN),
            ("🌐   Web Scraping",        self._on_scrape,        self.C_BTN),
        ]

        for texto, cmd, color in fuentes:
            self._make_button(sidebar, texto, cmd, color)

        # ── Separador visual ─────────────────────────────────────── #
        ttk.Separator(sidebar, orient='horizontal').pack(
            fill=tk.X, padx=10, pady=10
        )

        # ── Sección: Herramientas ────────────────────────────────── #
        tk.Label(
            sidebar,
            text="  HERRAMIENTAS",
            font=("Segoe UI", 8, "bold"),
            bg=self.C_SIDEBAR, fg=self.C_SUB, anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 4), padx=8)

        self._make_button(sidebar, "📊   Mostrar Análisis (EDA)",
                          self._on_analyze, "#1b6ca8")
        self._make_button(sidebar, "🗑️   Limpiar todo",
                          self._on_clear, self.C_BTN_CLR)

        # ── Indicador de fuente activa ───────────────────────────── #
        ttk.Separator(sidebar, orient='horizontal').pack(
            fill=tk.X, padx=10, pady=10
        )

        tk.Label(
            sidebar, text="  Fuente activa:",
            font=("Segoe UI", 8),
            bg=self.C_SIDEBAR, fg=self.C_SUB, anchor=tk.W
        ).pack(fill=tk.X, padx=8)

        # Esta label se actualiza cada vez que se carga una fuente
        self.lbl_source = tk.Label(
            sidebar, text="—",
            font=("Segoe UI", 8, "bold"),
            bg=self.C_SIDEBAR, fg=self.C_ACCENT,
            wraplength=175, anchor=tk.W, justify=tk.LEFT
        )
        self.lbl_source.pack(fill=tk.X, padx=8, pady=4)

    def _make_button(self, parent, text, command, color):
        """
        Crea un botón con estilo consistente y lo agrega al parent.

        tk.Button:
          text     → texto visible en el botón
          command  → función Python a ejecutar al hacer clic
          bg/fg    → colores de fondo y texto
          relief   → estilo del borde (flat=sin borde)
          cursor   → cursor del mouse al pasar sobre el botón
          anchor   → alineación del texto (W=izquierda)
        pack(fill=tk.X) → el botón se estira horizontalmente
        """
        btn = tk.Button(
            parent, text=text, command=command,
            bg=color, fg="white",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#7b52ab",
            activeforeground="white",
            padx=10, pady=7,
            anchor=tk.W, width=22
        )
        btn.pack(pady=2, padx=8, fill=tk.X)
        return btn

    # ── Área principal: tabla + log ──────────────────────────────── #
    def _build_main_area(self, parent):
        """
        Área derecha dividida verticalmente en:
          - Parte superior: tabla Treeview con los datos
          - Parte inferior: log de análisis y mensajes

        tk.PanedWindow crea un área divisible: el usuario puede
        arrastrar el divisor para cambiar las proporciones.
        orient=tk.VERTICAL → divide arriba/abajo
        """
        paned = tk.PanedWindow(
            parent, orient=tk.VERTICAL,
            bg="#2a2a3e", sashwidth=5,
            sashrelief=tk.FLAT
        )
        paned.pack(fill=tk.BOTH, expand=True)

        self._build_table_section(paned)   # Sección de tabla (superior)
        self._build_log_section(paned)     # Sección de log (inferior)

    # ── Sección de tabla de datos ────────────────────────────────── #
    def _build_table_section(self, paned):
        """
        Construye el área de tabla con ttk.Treeview para mostrar DataFrames.

        ttk.Treeview es el widget de tabla/árbol de Tkinter.
        Para usarlo como tabla simple, se configura con show='headings'
        (oculta la columna de árbol y solo muestra los encabezados).

        El Treeview se conecta a dos Scrollbars (horizontal y vertical)
        mediante los parámetros yscrollcommand y xscrollcommand.
        """
        frame = tk.Frame(paned, bg=self.C_BG)
        paned.add(frame, height=420, minsize=180)

        # ── Cabecera de la sección de tabla ── #
        top_bar = tk.Frame(frame, bg=self.C_BG)
        top_bar.pack(fill=tk.X, padx=4, pady=(4, 2))

        self.lbl_table_title = tk.Label(
            top_bar, text="Datos cargados",
            font=("Segoe UI", 11, "bold"),
            bg=self.C_BG, fg=self.C_TEXT
        )
        self.lbl_table_title.pack(side=tk.LEFT)

        self.lbl_count = tk.Label(
            top_bar, text="Sin datos",
            font=("Segoe UI", 9),
            bg=self.C_BG, fg=self.C_SUB
        )
        self.lbl_count.pack(side=tk.RIGHT)

        # ── Contenedor del Treeview ── #
        tbl_frame = tk.Frame(frame, bg=self.C_BG)
        tbl_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        # Scrollbars
        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",
                            style="Vertical.TScrollbar")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal",
                            style="Horizontal.TScrollbar")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview principal (tabla de datos)
        # show='headings' → solo mostrar encabezados, no columna de árbol
        # selectmode='browse' → seleccionar solo una fila a la vez
        self.tree = ttk.Treeview(
            tbl_frame,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode='browse'
        )
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Conectar scrollbars al Treeview
        # .set se llama automáticamente cuando el Treeview hace scroll
        # .yview / .xview controlan la posición del Treeview desde el scrollbar
        vsb.configure(command=self.tree.yview)
        hsb.configure(command=self.tree.xview)

        # Tags para filas alternas (zebra striping)
        self.tree.tag_configure("oddrow",  background=self.C_ROW_A)
        self.tree.tag_configure("evenrow", background=self.C_ROW_B)

    # ── Sección de log / análisis ────────────────────────────────── #
    def _build_log_section(self, paned):
        """
        Construye el área de texto para logs y resultados de análisis.

        tk.Text es un widget de texto multilínea que:
        - Soporta etiquetas (tags) para dar formato al texto
        - Puede ser de solo lectura (state=tk.DISABLED)
        - Permite colorear partes del texto con tags

        El widget está en modo DISABLED por defecto para que el usuario
        no pueda editarlo. Para escribir en él hay que habilitarlo
        temporalmente, insertar el texto y deshabilitarlo de nuevo.
        """
        frame = tk.Frame(paned, bg=self.C_BG)
        paned.add(frame, height=200, minsize=80)

        tk.Label(
            frame, text="  Análisis  &  Mensajes del Sistema",
            font=("Segoe UI", 9, "bold"),
            bg="#11111f", fg=self.C_TEXT, anchor=tk.W
        ).pack(fill=tk.X)

        log_container = tk.Frame(frame, bg=self.C_BG)
        log_container.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        log_vsb = ttk.Scrollbar(log_container, style="Vertical.TScrollbar")
        log_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        log_hsb = ttk.Scrollbar(log_container, orient="horizontal",
                                style="Horizontal.TScrollbar")
        log_hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Text widget: fondo oscuro, fuente monoespaciada para alinear texto
        self.txt_log = tk.Text(
            log_container,
            bg=self.C_LOG_BG,
            fg=self.C_TEXT,
            font=("Consolas", 9),
            wrap=tk.NONE,
            yscrollcommand=log_vsb.set,
            xscrollcommand=log_hsb.set,
            state=tk.DISABLED,     # Solo lectura
            borderwidth=0,
            insertbackground="white",
            selectbackground="#4a1d96"
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        log_vsb.configure(command=self.txt_log.yview)
        log_hsb.configure(command=self.txt_log.xview)

        # ── Tags de color para el texto del log ── #
        # Los tags permiten colorear partes del texto
        self.txt_log.tag_configure("ok",      foreground=self.C_OK)
        self.txt_log.tag_configure("err",     foreground=self.C_ERR)
        self.txt_log.tag_configure("warn",    foreground=self.C_WARN)
        self.txt_log.tag_configure("info",    foreground="#93c5fd")
        self.txt_log.tag_configure("accent",  foreground=self.C_ACCENT)
        self.txt_log.tag_configure("header",  foreground="#c084fc",
                                   font=("Consolas", 9, "bold"))

    # ── Barra de estado ──────────────────────────────────────────── #
    def _build_statusbar(self):
        """Barra inferior con mensajes de estado breves."""
        bar = tk.Frame(self.root, bg="#0d0d1a", height=24)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self.lbl_status = tk.Label(
            bar, text="  Listo. Selecciona una fuente de datos.",
            font=("Segoe UI", 8),
            bg="#0d0d1a", fg=self.C_SUB, anchor=tk.W
        )
        self.lbl_status.pack(side=tk.LEFT, padx=8, pady=3)

    # ================================================================ #
    #  UTILIDADES DE UI                                                 #
    # ================================================================ #
    def _set_status(self, msg: str):
        """
        Actualiza el mensaje de la barra de estado.

        root.update_idletasks() fuerza a Tkinter a procesar
        actualizaciones de UI pendientes inmediatamente.
        Sin esto, el mensaje no aparecería hasta terminar el proceso.
        """
        self.lbl_status.configure(text=f"  {msg}")
        self.root.update_idletasks()

    def _log(self, msg: str, tag: str = ""):
        """
        Escribe un mensaje en el área de log con color opcional.

        Proceso para escribir en un Text widget de solo lectura:
        1. Habilitar: txt_log.configure(state=tk.NORMAL)
        2. Insertar:  txt_log.insert(tk.END, texto, tag)
        3. Deshabilitar: txt_log.configure(state=tk.DISABLED)
        4. Auto-scroll: txt_log.see(tk.END)

        tk.END es una constante que representa el final del texto.
        """
        self.txt_log.configure(state=tk.NORMAL)
        if tag:
            self.txt_log.insert(tk.END, msg + "\n", tag)
        else:
            self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.configure(state=tk.DISABLED)
        self.txt_log.see(tk.END)   # Auto-scroll al fondo

    def _clear_log(self):
        """Borra todo el contenido del área de log."""
        self.txt_log.configure(state=tk.NORMAL)
        # "1.0" = línea 1, caracter 0 → inicio del texto
        # tk.END                       → final del texto
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.configure(state=tk.DISABLED)

    def _update_table(self, df: pd.DataFrame, title: str = ""):
        """
        Carga un DataFrame en el Treeview para visualizarlo como tabla.

        Proceso:
        1. Guardar referencia al DataFrame actual
        2. Actualizar etiquetas informativas
        3. Limpiar la tabla anterior
        4. Configurar las nuevas columnas
        5. Insertar filas (máx. 1000 por rendimiento)

        Parámetros
        ----------
        df    : pd.DataFrame   Datos a mostrar
        title : str            Título descriptivo (fuente de datos)
        """
        self.current_df = df

        # ── Actualizar etiquetas ── #
        self.lbl_table_title.configure(text=title or "Datos cargados")
        self.lbl_count.configure(
            text=f"  {len(df):,} registros  ×  {len(df.columns)} columnas"
        )
        # Mostrar nombre de la fuente en el sidebar
        nombre_fuente = title.split(": ", 1)[-1] if ": " in title else title
        self.lbl_source.configure(text=nombre_fuente or "—")

        # ── Limpiar tabla ── #
        self.tree.delete(*self.tree.get_children())

        # ── Configurar columnas ── #
        # Las columnas se definen por sus nombres (identificadores únicos)
        cols = [str(c) for c in df.columns]
        self.tree["columns"] = cols
        self.tree["show"] = "headings"

        for col in cols:
            # heading: configura el texto del encabezado
            self.tree.heading(col, text=col, anchor=tk.W)
            # column: configura el ancho y comportamiento de la columna
            ancho = max(80, min(int(len(col) * 9) + 30, 220))
            self.tree.column(col, width=ancho, minwidth=60, stretch=True)

        # ── Insertar filas ── #
        # Limitamos a 1000 filas para mantener la UI fluida
        MAX_FILAS = 1000
        df_vista = df.head(MAX_FILAS)

        for i in range(len(df_vista)):
            fila = df_vista.iloc[i]
            # Convertir cada valor a string; NaN → cadena vacía
            # pd.isna() detecta NaN, None, y NaT (datetime nulo)
            valores = [
                "" if pd.isna(v) else str(v)
                for v in fila
            ]
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=valores, tags=(tag,))

        if len(df) > MAX_FILAS:
            self._log(
                f"⚠  Mostrando primeras {MAX_FILAS:,} filas de {len(df):,} totales.",
                "warn"
            )

    # ================================================================ #
    #  MANEJADORES DE EVENTOS (_on_* methods)                          #
    # ================================================================ #

    # ── Cargar CSV ─────────────────────────────────────────────── #
    def _on_load_csv(self):
        """
        Evento: usuario hace clic en 'Cargar CSV'.

        filedialog.askopenfilename() abre el diálogo de selección de
        archivos del sistema operativo y retorna la ruta seleccionada.
        Si el usuario cancela, retorna una cadena vacía.

        filetypes=[(...)] filtra qué tipos de archivos se muestran.
        """
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos", "*.*")]
        )
        if not ruta:
            return   # Usuario canceló el diálogo

        try:
            self._set_status("Cargando archivo CSV...")
            df = self.loader.load_csv(ruta)
            self._update_table(df, f"CSV: {self.loader.last_loaded_source}")
            self._clear_log()
            self._log(f"✓  CSV cargado: {ruta}", "ok")
            self._log(f"   {len(df):,} filas  ×  {len(df.columns)} columnas", "info")
            self._set_status(f"✓ CSV cargado: {self.loader.last_loaded_source}")

        except Exception as e:
            messagebox.showerror("Error al cargar CSV", str(e))
            self._log(f"✗  Error al cargar CSV: {e}", "err")
            self._set_status("Error al cargar CSV.")

    # ── Cargar TSV ─────────────────────────────────────────────── #
    def _on_load_tsv(self):
        """Evento: usuario hace clic en 'Cargar TSV'."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo TSV",
            filetypes=[("Archivos TSV", "*.tsv"), ("Todos", "*.*")]
        )
        if not ruta:
            return

        try:
            self._set_status("Cargando archivo TSV...")
            df = self.loader.load_tsv(ruta)
            self._update_table(df, f"TSV: {self.loader.last_loaded_source}")
            self._clear_log()
            self._log(f"✓  TSV cargado: {ruta}", "ok")
            self._log(f"   {len(df):,} filas  ×  {len(df.columns)} columnas", "info")
            self._set_status(f"✓ TSV cargado: {self.loader.last_loaded_source}")

        except Exception as e:
            messagebox.showerror("Error al cargar TSV", str(e))
            self._log(f"✗  Error al cargar TSV: {e}", "err")
            self._set_status("Error al cargar TSV.")

    # ── Cargar JSON ────────────────────────────────────────────── #
    def _on_load_json(self):
        """Evento: usuario hace clic en 'Cargar JSON'."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo JSON",
            filetypes=[("Archivos JSON", "*.json"), ("Todos", "*.*")]
        )
        if not ruta:
            return

        try:
            self._set_status("Cargando archivo JSON...")
            df = self.loader.load_json(ruta)
            self._update_table(df, f"JSON: {self.loader.last_loaded_source}")
            self._clear_log()
            self._log(f"✓  JSON cargado: {ruta}", "ok")
            self._log(f"   {len(df):,} registros  ×  {len(df.columns)} columnas", "info")
            self._set_status(f"✓ JSON cargado: {self.loader.last_loaded_source}")

        except Exception as e:
            messagebox.showerror("Error al cargar JSON", str(e))
            self._log(f"✗  Error al cargar JSON: {e}", "err")
            self._set_status("Error al cargar JSON.")

    # ── Consultar PostgreSQL ───────────────────────────────────── #
    def _on_query_postgres(self):
        """
        Evento: usuario hace clic en 'Consultar PostgreSQL'.
        Abre el diálogo de conexión a la base de datos.
        """
        DBDialog(self.root, callback=self._handle_db_result)

    def _handle_db_result(self, host, database, user, password, port, query):
        """
        Callback que recibe los parámetros del DBDialog y ejecuta la consulta.

        Este método es llamado por DBDialog cuando el usuario hace clic
        en 'Conectar y Ejecutar'. Recibe todos los parámetros de conexión.
        """
        try:
            self._set_status("Conectando a PostgreSQL...")
            self._clear_log()
            self._log(f"⏳  Conectando a {host}:{port} / {database}...", "info")
            self.root.update_idletasks()

            # Crear instancia de DatabaseManager y conectar
            db = DatabaseManager(host, database, user, password, int(port))
            db.connect()
            self._log("✓  Conexión establecida.", "ok")

            # Ejecutar la consulta SQL
            self._set_status("Ejecutando consulta SQL...")
            self._log(f"   Ejecutando: {query[:60]}...", "info")
            df = db.execute_query(query)
            db.disconnect()

            # Mostrar resultados en tabla
            self._update_table(df, f"PostgreSQL: {database}")
            self._log(f"✓  Consulta ejecutada: {len(df):,} registros retornados.", "ok")
            self._set_status(f"✓ PostgreSQL: {len(df):,} registros cargados.")

        except Exception as e:
            messagebox.showerror("Error de PostgreSQL", str(e))
            self._log(f"✗  Error: {e}", "err")
            self._set_status("Error en la conexión a PostgreSQL.")

    # ── Web Scraping ───────────────────────────────────────────── #
    def _on_scrape(self):
        """
        Evento: usuario hace clic en 'Web Scraping'.

        El web scraping hace peticiones HTTP que pueden tardar varios
        segundos. Si lo ejecutamos en el hilo principal de Tkinter,
        la ventana se CONGELA (no responde a eventos) hasta que termina.

        Solución: ejecutar el scraping en un HILO SECUNDARIO (Thread)
        mientras el hilo principal sigue manejando la UI.

        ── Importante sobre threading en Tkinter ─────────────────────
        Tkinter NO es thread-safe. No se pueden actualizar widgets
        directamente desde un hilo secundario.
        
        La solución es usar root.after(delay_ms, callback):
        - Agenda la ejecución del callback en el hilo principal
        - delay=0 significa "lo antes posible"
        - Es la forma correcta de comunicar el hilo secundario con Tkinter
        """
        self._clear_log()
        self._log("⏳  Iniciando web scraping...", "info")
        self._log("   Objetivo: books.toscrape.com (2 páginas × 20 libros)", "info")
        self._set_status("⏳ Realizando web scraping, espera...")
        self.root.update_idletasks()

        def ejecutar_scraping():
            """Función que corre en el hilo secundario."""
            try:
                scraper = WebScraper(pages=2)
                df = scraper.scrape()
                # Programar actualización de UI en el hilo principal
                self.root.after(0, lambda: self._on_scraping_completado(df))
            except Exception as e:
                # Programar manejo de error en el hilo principal
                self.root.after(0, lambda: self._on_scraping_error(str(e)))

        # daemon=True → el hilo se cierra si la aplicación se cierra
        hilo = threading.Thread(target=ejecutar_scraping, daemon=True)
        hilo.start()

    def _on_scraping_completado(self, df: pd.DataFrame):
        """Callback en el hilo principal cuando el scraping termina bien."""
        self._update_table(df, "Web Scraping: books.toscrape.com")
        self._clear_log()
        self._log("✓  Web scraping completado exitosamente.", "ok")
        self._log(f"   {len(df):,} libros extraídos de books.toscrape.com", "info")
        self._log("   Columnas: pagina, titulo, precio_gbp, calificacion, disponibilidad", "info")
        self._set_status(f"✓ Web scraping: {len(df):,} libros extraídos.")

    def _on_scraping_error(self, msg: str):
        """Callback en el hilo principal cuando el scraping falla."""
        messagebox.showerror("Error de Web Scraping", msg)
        self._log(f"✗  Error en web scraping: {msg}", "err")
        self._set_status("Error en web scraping.")

    # ── Análisis EDA ───────────────────────────────────────────── #
    def _on_analyze(self):
        """
        Evento: usuario hace clic en 'Mostrar Análisis (EDA)'.
        Crea un DataAnalyzer con el DataFrame actual y muestra el reporte.
        """
        if self.current_df is None:
            messagebox.showwarning(
                "Sin datos",
                "Primero carga datos desde alguna fuente de datos."
            )
            return

        try:
            analyzer = DataAnalyzer(self.current_df)
            reporte = analyzer.get_full_summary()
            self._clear_log()
            self._log(reporte, "info")
            self._set_status("✓ Análisis EDA completado.")
        except Exception as e:
            messagebox.showerror("Error en Análisis", str(e))
            self._log(f"✗  Error en análisis: {e}", "err")

    # ── Limpiar ────────────────────────────────────────────────── #
    def _on_clear(self):
        """Limpia la tabla, el log y resetea el estado."""
        self.current_df = None

        # Vaciar Treeview
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []

        # Resetear etiquetas
        self.lbl_table_title.configure(text="Datos cargados")
        self.lbl_count.configure(text="Sin datos")
        self.lbl_source.configure(text="—")

        self._clear_log()
        self._log("🗑️  Tabla y análisis limpiados.", "warn")
        self._log("   Listo para cargar nuevos datos.", "info")
        self._set_status("Listo.")

    # ================================================================ #
    #  ARRANQUE DE LA APLICACIÓN                                       #
    # ================================================================ #
    def run(self):
        """
        Inicia el bucle principal de Tkinter.

        root.mainloop() es el corazón de cualquier app Tkinter:
        - Entra en un bucle infinito esperando eventos
        - Cuando el usuario hace clic → llama al command del botón
        - Cuando el usuario escribe → actualiza el Entry
        - Cuando hay cambios → redibuja la ventana
        - Cuando se cierra la ventana → termina el bucle y retorna

        Sin mainloop(), la ventana se cerraría inmediatamente.
        """
        # Mensaje de bienvenida en el log
        self._log("🚀  Aplicación iniciada correctamente.", "ok")
        self._log("   Selecciona una fuente de datos del panel izquierdo.", "info")
        self._log("   CSV · TSV · JSON → usa el explorador de archivos.", "info")
        self._log("   PostgreSQL       → ingresa parámetros de conexión.", "info")
        self._log("   Web Scraping     → extrae libros de books.toscrape.com", "info")
        self._log("─" * 55, "")

        # Iniciar el bucle de eventos
        self.root.mainloop()


# ══════════════════════════════════════════════════════════════════ #
#  DIÁLOGO DE CONEXIÓN A POSTGRESQL                                  #
# ══════════════════════════════════════════════════════════════════ #
class DBDialog:
    """
    Ventana emergente (diálogo modal) para configurar la conexión PostgreSQL.

    tk.Toplevel crea una ventana secundaria independiente.
    .transient(parent) → la ventana es "hija" de la principal
    .grab_set()        → hace la ventana MODAL (bloquea la principal
                         hasta que este diálogo se cierre)
    .resizable(F, F)   → no se puede redimensionar

    El diálogo recibe un callback que llama cuando el usuario confirma.
    Este patrón permite que el diálogo no necesite conocer a MainWindow.
    """

    # Valores por defecto en los campos del formulario
    DEFAULTS = {
        "host":     "localhost",
        "database": "universidad",
        "user":     "postgres",
        "password": "",
        "port":     "5432",
        "query":    "SELECT * FROM estudiantes LIMIT 50;"
    }

    def __init__(self, parent: tk.Tk, callback):
        """
        Parámetros
        ----------
        parent   : tk.Tk       Ventana padre (MainWindow.root)
        callback : callable    Función a llamar con los parámetros:
                               callback(host, db, user, pwd, port, query)
        """
        self.callback = callback

        # Crear ventana emergente
        self.win = tk.Toplevel(parent)
        self.win.title("Conexión a PostgreSQL")
        self.win.geometry("440x400")
        self.win.configure(bg="#1a1b2e")
        self.win.resizable(False, False)
        self.win.transient(parent)   # Hija de la ventana principal
        self.win.grab_set()          # Modal: bloquea la ventana principal

        # Centrar la ventana en la pantalla
        self.win.update_idletasks()
        x = parent.winfo_x() + parent.winfo_width()  // 2 - 220
        y = parent.winfo_y() + parent.winfo_height() // 2 - 200
        self.win.geometry(f"440x400+{x}+{y}")

        self._build()

    def _build(self):
        """Construye los widgets del formulario de conexión."""
        main = tk.Frame(self.win, bg="#1a1b2e", padx=22, pady=18)
        main.pack(fill=tk.BOTH, expand=True)

        # Título del diálogo
        tk.Label(
            main, text="🐘  Conectar a PostgreSQL",
            font=("Segoe UI", 13, "bold"),
            bg="#1a1b2e", fg="#e2e8f0"
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 16))

        # Definición de campos del formulario
        campos = [
            ("Host:",           "host",     False),
            ("Base de datos:",  "database", False),
            ("Usuario:",        "user",     False),
            ("Contraseña:",     "password", True),   # show='*'
            ("Puerto:",         "port",     False),
        ]

        self.entries = {}

        for i, (etiqueta, clave, ocultar) in enumerate(campos, start=1):
            # Etiqueta del campo
            tk.Label(
                main, text=etiqueta,
                font=("Segoe UI", 9),
                bg="#1a1b2e", fg="#94a3b8"
            ).grid(row=i, column=0, sticky=tk.W, pady=4)

            # Campo de entrada
            entry = ttk.Entry(main, width=30)
            entry.insert(0, self.DEFAULTS[clave])
            if ocultar:
                entry.configure(show="*")   # Ocultar contraseña
            entry.grid(row=i, column=1, sticky=tk.EW, padx=(10, 0), pady=4)
            self.entries[clave] = entry

        # Campo de consulta SQL (multilínea)
        fila_query = len(campos) + 1

        tk.Label(
            main, text="Consulta SQL:",
            font=("Segoe UI", 9),
            bg="#1a1b2e", fg="#94a3b8"
        ).grid(row=fila_query, column=0, sticky=tk.NW, pady=(10, 0))

        self.txt_query = tk.Text(
            main, width=30, height=3,
            font=("Consolas", 9),
            bg="#0d0d1a", fg="#e2e8f0",
            insertbackground="white",
            wrap=tk.WORD
        )
        self.txt_query.insert("1.0", self.DEFAULTS["query"])
        self.txt_query.grid(
            row=fila_query, column=1,
            sticky=tk.EW, padx=(10, 0), pady=(10, 0)
        )

        # Botón de acción
        tk.Button(
            main,
            text="  🔗  Conectar y Ejecutar Consulta  ",
            command=self._on_confirm,
            bg="#533483", fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            activebackground="#7b52ab",
            padx=12, pady=8
        ).grid(
            row=fila_query + 1, column=0, columnspan=2,
            pady=(16, 0), sticky=tk.EW
        )

        main.columnconfigure(1, weight=1)

    def _on_confirm(self):
        """Lee los campos y ejecuta el callback con los parámetros."""
        query = self.txt_query.get("1.0", tk.END).strip()

        if not query:
            messagebox.showwarning(
                "Campo vacío",
                "Ingresa una consulta SQL.",
                parent=self.win
            )
            return

        # Obtener valores de todos los entries
        params = {k: e.get().strip() for k, e in self.entries.items()}

        # Cerrar el diálogo antes de ejecutar
        self.win.destroy()

        # Llamar al callback de MainWindow con los parámetros
        self.callback(
            params["host"],
            params["database"],
            params["user"],
            params["password"],
            params["port"],
            query
        )