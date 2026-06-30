"""
gui.py — Interfaz gráfica completa de DataAnalyzer
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import threading

from data_loader     import DataLoader
from database_manager import DatabaseManager
from web_scraper     import WebScraper
from data_analyzer   import DataAnalyzer
from ml_models       import MLManager, ALL_MODELS


# ══════════════════════════════════════════════════════════════════ #
#  VENTANA PRINCIPAL                                                 #
# ══════════════════════════════════════════════════════════════════ #
class MainWindow:

    TITLE    = "🔬  DataAnalyzer — Pipeline Multifuente de Datos"
    GEOMETRY = "1280x800"

    C_BG      = "#1a1b2e"
    C_SIDEBAR = "#16213e"
    C_HEADER  = "#0f3460"
    C_BTN     = "#533483"
    C_BTN_GRN = "#065f46"
    C_BTN_BLU = "#1e3a5f"
    C_BTN_CLR = "#374151"
    C_TEXT    = "#e2e8f0"
    C_SUB     = "#94a3b8"
    C_ACCENT  = "#c084fc"
    C_OK      = "#10b981"
    C_ERR     = "#ef4444"
    C_WARN    = "#f59e0b"
    C_TBL_HDR = "#1e3a5f"
    C_ROW_A   = "#1a1b2e"
    C_ROW_B   = "#1e2039"
    C_LOG_BG  = "#0d0d1a"
    C_WHITE   = "#FFFFFF"

    def __init__(self):
        self.loader       = DataLoader()
        self.ml           = MLManager()
        self.current_df   = None
        self.query_history = []          # Historial de consultas SQL
        self._ml_cancel   = threading.Event()   # Para cancelar ML

        self.root = tk.Tk()
        self.root.title(self.TITLE)
        self.root.geometry(self.GEOMETRY)
        self.root.configure(bg=self.C_BG)
        self.root.minsize(900, 640)

        self._setup_styles()
        self._build_ui()

    # ── Estilos ───────────────────────────────────────────────── #
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview",
            background=self.C_ROW_A, foreground=self.C_TEXT,
            fieldbackground=self.C_ROW_A, rowheight=26,
            font=("Consolas", 9))
        s.configure("Treeview.Heading",
            background=self.C_TBL_HDR, foreground=self.C_ACCENT,
            font=("Segoe UI", 9, "bold"), relief="flat")
        s.map("Treeview",
            background=[("selected", "#4a1d96")],
            foreground=[("selected", "#ffffff")])

    # ── Construcción UI ───────────────────────────────────────── #
    def _build_ui(self):
        self._build_header()
        self._build_body()
        self._build_statusbar()

    def _build_header(self):
        h = tk.Frame(self.root, bg=self.C_HEADER, height=52)
        h.pack(fill=tk.X)
        h.pack_propagate(False)
        tk.Label(h, text="🔬  DataAnalyzer  —  Pipeline Multifuente de Datos",
                 font=("Segoe UI", 14, "bold"), bg=self.C_HEADER, fg="#dbeafe"
                 ).pack(side=tk.LEFT, padx=18, pady=10)
        tk.Label(h, text="CSV · TSV · JSON · PostgreSQL · Web Scraping · ML",
                 font=("Segoe UI", 9), bg=self.C_HEADER, fg="#93c5fd"
                 ).pack(side=tk.RIGHT, padx=18)

    def _build_body(self):
        body = tk.Frame(self.root, bg=self.C_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self._build_sidebar(body)
        self._build_main_area(body)

    # ── Sidebar ───────────────────────────────────────────────── #
    def _build_sidebar(self, parent):
        outer = tk.Frame(parent, bg=self.C_SIDEBAR, width=205)
        outer.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        outer.pack_propagate(False)

        # Canvas + scrollbar para sidebar largo
        canvas = tk.Canvas(outer, bg=self.C_SIDEBAR, highlightthickness=0,
                           width=200)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        sidebar = tk.Frame(canvas, bg=self.C_SIDEBAR)

        canvas.create_window((0, 0), window=sidebar, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        sidebar.bind("<Configure>",
                     lambda e: canvas.configure(
                         scrollregion=canvas.bbox("all")))
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ── FUENTES DE DATOS ─────────── #
        self._sec_label(sidebar, "FUENTES DE DATOS")
        for txt, cmd, col in [
            ("📄   Cargar CSV",          self._on_load_csv,      self.C_BTN),
            ("📋   Cargar TSV",          self._on_load_tsv,      self.C_BTN),
            ("{…}  Cargar JSON",          self._on_load_json,     self.C_BTN),
            ("🐘   Consultar PostgreSQL", self._on_query_postgres, self.C_BTN),
            ("🌐   Web Scraping",         self._on_scrape,         self.C_BTN),
        ]:
            self._btn(sidebar, txt, cmd, col)

        self._sep(sidebar)

        # ── ANÁLISIS ─────────────────── #
        self._sec_label(sidebar, "ANÁLISIS")
        self._btn(sidebar, "📊   Mostrar EDA",    self._on_analyze, "#1b6ca8")
        self._btn(sidebar, "🗑️   Limpiar todo",   self._on_clear,   self.C_BTN_CLR)

        self._sep(sidebar)

        # ── MODELOS ──────────────────── #
        self._sec_label(sidebar, "MODELOS")
        tk.Label(sidebar,
                 text="  Selecciona modelos, un target\n  y entrena individualmente.",
                 font=("Segoe UI", 8), bg=self.C_SIDEBAR, fg=self.C_SUB,
                 justify=tk.LEFT
                 ).pack(fill=tk.X, padx=8, pady=(0, 4))
        self._btn(sidebar, "🎯   Entrenar Modelo(s)", self._on_train_models,
                  "#7c3aed")

        self._sep(sidebar)

        # ── MACHINE LEARNING ─────────── #
        self._sec_label(sidebar, "MACHINE LEARNING")
        self._btn(sidebar, "📊   Comparar Modelos",  self._on_compare_models,
                  self.C_BTN_GRN)
        self._btn(sidebar, "🔵   Clustering + PCA",  self._on_clustering,
                  self.C_BTN_BLU)

        self._sep(sidebar)

        # ── FUENTE ACTIVA ─────────────── #
        tk.Label(sidebar, text="  Fuente activa:",
                 font=("Segoe UI", 8), bg=self.C_SIDEBAR, fg=self.C_SUB,
                 anchor=tk.W).pack(fill=tk.X, padx=8)
        self.lbl_source = tk.Label(sidebar, text="—",
                 font=("Segoe UI", 8, "bold"), bg=self.C_SIDEBAR,
                 fg=self.C_ACCENT, wraplength=175, anchor=tk.W,
                 justify=tk.LEFT)
        self.lbl_source.pack(fill=tk.X, padx=8, pady=(2, 12))

    def _sec_label(self, parent, text):
        tk.Label(parent, text=f"  {text}",
                 font=("Segoe UI", 8, "bold"),
                 bg=self.C_SIDEBAR, fg=self.C_SUB, anchor=tk.W
                 ).pack(fill=tk.X, pady=(14, 4), padx=8)

    def _sep(self, parent):
        ttk.Separator(parent, orient="horizontal").pack(
            fill=tk.X, padx=10, pady=6)

    def _btn(self, parent, text, command, color):
        b = tk.Button(parent, text=text, command=command,
                      bg=color, fg="white", font=("Segoe UI", 9),
                      relief=tk.FLAT, cursor="hand2",
                      activebackground="#7b52ab", activeforeground="white",
                      padx=10, pady=6, anchor=tk.W, width=22)
        b.pack(pady=2, padx=8, fill=tk.X)
        return b

    # ── Área principal ────────────────────────────────────────── #
    def _build_main_area(self, parent):
        paned = tk.PanedWindow(parent, orient=tk.VERTICAL,
                               bg=self.C_BG, sashwidth=5,
                               sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)
        self._build_table_area(paned)
        self._build_log_area(paned)

    def _build_table_area(self, paned):
        frame = tk.Frame(paned, bg=self.C_BG)
        paned.add(frame, height=430, minsize=180)

        top = tk.Frame(frame, bg=self.C_BG)
        top.pack(fill=tk.X, padx=4, pady=(4, 2))

        self.lbl_table_title = tk.Label(top, text="Datos cargados",
            font=("Segoe UI", 11, "bold"), bg=self.C_BG, fg=self.C_TEXT)
        self.lbl_table_title.pack(side=tk.LEFT)

        # Botón cancelar ML (oculto hasta que corra algo)
        self._cancel_frame = tk.Frame(top, bg=self.C_BG)
        self._cancel_frame.pack(side=tk.RIGHT)
        self._cancel_btn = tk.Button(
            self._cancel_frame,
            text="⛔  Cancelar",
            command=self._on_cancel_ml,
            bg=self.C_ERR, fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=8, pady=4
        )
        # No se muestra hasta que corra ML

        self.lbl_count = tk.Label(frame, text="Sin datos",
            font=("Segoe UI", 9), bg=self.C_BG, fg=self.C_SUB)
        self.lbl_count.pack(anchor=tk.W, padx=4)

        tbl_f = tk.Frame(frame, bg=self.C_BG)
        tbl_f.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        vsb = ttk.Scrollbar(tbl_f, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = ttk.Scrollbar(tbl_f, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(tbl_f, show="headings",
                                  yscrollcommand=vsb.set,
                                  xscrollcommand=hsb.set,
                                  selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.configure(command=self.tree.yview)
        hsb.configure(command=self.tree.xview)
        self.tree.tag_configure("oddrow",  background=self.C_ROW_A)
        self.tree.tag_configure("evenrow", background=self.C_ROW_B)

    def _build_log_area(self, paned):
        frame = tk.Frame(paned, bg=self.C_BG)
        paned.add(frame, height=220, minsize=80)

        tk.Label(frame, text="  Análisis & Mensajes del Sistema",
                 font=("Segoe UI", 9, "bold"), bg="#11111f",
                 fg=self.C_TEXT, anchor=tk.W
                 ).pack(fill=tk.X)

        lf = tk.Frame(frame, bg=self.C_BG)
        lf.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        lvsb = ttk.Scrollbar(lf)
        lvsb.pack(side=tk.RIGHT, fill=tk.Y)
        lhsb = ttk.Scrollbar(lf, orient="horizontal")
        lhsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.txt_log = tk.Text(lf, bg=self.C_LOG_BG, fg=self.C_TEXT,
                                font=("Consolas", 9), wrap=tk.NONE,
                                yscrollcommand=lvsb.set,
                                xscrollcommand=lhsb.set,
                                state=tk.DISABLED, borderwidth=0,
                                insertbackground="white",
                                selectbackground="#4a1d96")
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        lvsb.configure(command=self.txt_log.yview)
        lhsb.configure(command=self.txt_log.xview)

        for tag, fg in [
            ("ok", self.C_OK), ("err", self.C_ERR), ("warn", self.C_WARN),
            ("info", "#93c5fd"), ("accent", self.C_ACCENT),
            ("header", "#c084fc"),
        ]:
            self.txt_log.tag_configure(tag, foreground=fg)
        self.txt_log.tag_configure("header", font=("Consolas", 9, "bold"))

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg="#0d0d1a", height=24)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)
        self.lbl_status = tk.Label(bar, text="  Listo.",
            font=("Segoe UI", 8), bg="#0d0d1a", fg=self.C_SUB, anchor=tk.W)
        self.lbl_status.pack(side=tk.LEFT, padx=8, pady=3)

    # ── Utilidades UI ─────────────────────────────────────────── #
    def _set_status(self, msg):
        self.lbl_status.configure(text=f"  {msg}")
        self.root.update_idletasks()

    def _log(self, msg, tag=""):
        self.txt_log.configure(state=tk.NORMAL)
        if tag:
            self.txt_log.insert(tk.END, msg + "\n", tag)
        else:
            self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.configure(state=tk.DISABLED)
        self.txt_log.see(tk.END)

    def _clear_log(self):
        self.txt_log.configure(state=tk.NORMAL)
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.configure(state=tk.DISABLED)

    def _update_table(self, df, title=""):
        self.current_df = df
        self.lbl_table_title.configure(text=title or "Datos cargados")
        self.lbl_count.configure(
            text=f"  {len(df):,} registros  ×  {len(df.columns)} columnas")
        src = title.split(": ", 1)[-1] if ": " in title else title
        self.lbl_source.configure(text=src or "—")

        self.tree.delete(*self.tree.get_children())
        cols = [str(c) for c in df.columns]
        self.tree["columns"] = cols
        self.tree["show"]    = "headings"
        for col in cols:
            self.tree.heading(col, text=col, anchor=tk.W)
            w = max(80, min(int(len(col) * 9) + 30, 220))
            self.tree.column(col, width=w, minwidth=60, stretch=True)

        limit = min(1000, len(df))
        for i in range(limit):
            row    = df.iloc[i]
            values = ["" if pd.isna(v) else str(v) for v in row]
            tag    = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=values, tags=(tag,))

        if len(df) > 1000:
            self._log(f"⚠  Mostrando primeras 1,000 filas de {len(df):,}.", "warn")

    def _show_cancel(self):
        """Muestra el botón cancelar."""
        self._ml_cancel.clear()
        self._cancel_btn.pack(side=tk.RIGHT)

    def _hide_cancel(self):
        """Oculta el botón cancelar."""
        self._cancel_btn.pack_forget()

    def _on_cancel_ml(self):
        self._ml_cancel.set()
        self._log("⛔  Cancelación solicitada — se detendrá al terminar el modelo actual...", "warn")
        self._set_status("Cancelando...")

    # ════════════════════════════════════════════════════════════ #
    #  EVENTOS — FUENTES DE DATOS                                  #
    # ════════════════════════════════════════════════════════════ #
    def _on_load_csv(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")])
        if not ruta: return
        try:
            self._set_status("Cargando CSV...")
            df = self.loader.load_csv(ruta)
            self._update_table(df, f"CSV: {self.loader.last_loaded_source}")
            self._clear_log()
            self._log(f"✓  CSV cargado: {ruta}", "ok")
            self._log(f"   {len(df):,} filas × {len(df.columns)} columnas", "info")
            self._set_status(f"✓ CSV: {self.loader.last_loaded_source}")
        except Exception as e:
            messagebox.showerror("Error CSV", str(e))
            self._log(f"✗  {e}", "err")

    def _on_load_tsv(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo TSV",
            filetypes=[("TSV", "*.tsv"), ("Todos", "*.*")])
        if not ruta: return
        try:
            self._set_status("Cargando TSV...")
            df = self.loader.load_tsv(ruta)
            self._update_table(df, f"TSV: {self.loader.last_loaded_source}")
            self._clear_log()
            self._log(f"✓  TSV cargado: {ruta}", "ok")
            self._log(f"   {len(df):,} filas × {len(df.columns)} columnas", "info")
            self._set_status(f"✓ TSV: {self.loader.last_loaded_source}")
        except Exception as e:
            messagebox.showerror("Error TSV", str(e))
            self._log(f"✗  {e}", "err")

    def _on_load_json(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo JSON",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")])
        if not ruta: return
        try:
            self._set_status("Cargando JSON...")
            df = self.loader.load_json(ruta)
            self._update_table(df, f"JSON: {self.loader.last_loaded_source}")
            self._clear_log()
            self._log(f"✓  JSON cargado: {ruta}", "ok")
            self._log(f"   {len(df):,} registros × {len(df.columns)} columnas", "info")
            self._set_status(f"✓ JSON: {self.loader.last_loaded_source}")
        except Exception as e:
            messagebox.showerror("Error JSON", str(e))
            self._log(f"✗  {e}", "err")

    def _on_query_postgres(self):
        DBDialog(self.root,
                 history=self.query_history,
                 callback=self._handle_db_result)

    def _handle_db_result(self, host, database, user, password, port, query):
        self._set_status("⏳ Conectando a PostgreSQL...")
        self._clear_log()
        self._log(f"⏳  Conectando a {host}:{port}/{database}...", "info")
        self.root.update_idletasks()

        def run():
            try:
                db = DatabaseManager(host, database, user, password, int(port))
                db.connect()
                self.root.after(0, lambda: self._log("✓  Conexión establecida.", "ok"))
                self.root.after(0, lambda: self._set_status("Ejecutando consulta..."))

                df = db.execute_query(query)
                db.disconnect()

                self.root.after(0, lambda: self._db_query_done(df, query, database))
            except Exception as e:
                self.root.after(0, lambda: self._db_query_err(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _db_query_done(self, df, query, database):
        # Guardar en historial (sin duplicados)
        if query not in self.query_history:
            self.query_history.insert(0, query)
        if len(self.query_history) > 20:
            self.query_history.pop()

        self._update_table(df, f"PostgreSQL: {database}")
        self._log(f"✓  {len(df):,} registros retornados.", "ok")
        self._set_status(f"✓ PostgreSQL: {len(df):,} registros.")

    def _db_query_err(self, msg):
        messagebox.showerror("Error PostgreSQL", msg)
        self._log(f"✗  {msg}", "err")
        self._set_status("Error en PostgreSQL.")

    def _on_scrape(self):
        self._clear_log()
        self._log("⏳  Iniciando web scraping...", "info")
        self._set_status("⏳ Web scraping en progreso...")
        self.root.update_idletasks()

        def run():
            try:
                from web_scraper import WebScraper
                scraper = WebScraper(pages=2)
                df = scraper.scrape()
                self.root.after(0, lambda: self._scrape_done(df))
            except Exception as e:
                self.root.after(0, lambda: self._scrape_err(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _scrape_done(self, df):
        self._update_table(df, "Web Scraping")
        self._clear_log()
        self._log(f"✓  {len(df):,} registros extraídos.", "ok")
        self._set_status(f"✓ Scraping: {len(df):,} registros.")

    def _scrape_err(self, msg):
        messagebox.showerror("Error Scraping", msg)
        self._log(f"✗  {msg}", "err")
        self._set_status("Error en scraping.")

    # ── EDA ───────────────────────────────────────────────────── #
    def _on_analyze(self):
        if self.current_df is None:
            messagebox.showwarning("Sin datos", "Primero carga un dataset.")
            return
        try:
            a = DataAnalyzer(self.current_df)
            self._clear_log()
            self._log(a.get_full_summary(), "info")
            self._set_status("✓ EDA completado.")
        except Exception as e:
            messagebox.showerror("Error EDA", str(e))

    def _on_clear(self):
        self.current_df = None
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []
        self.lbl_table_title.configure(text="Datos cargados")
        self.lbl_count.configure(text="Sin datos")
        self.lbl_source.configure(text="—")
        self._clear_log()
        self._log("🗑️  Limpiado.", "warn")
        self._set_status("Listo.")

    # ════════════════════════════════════════════════════════════ #
    #  EVENTOS — MODELOS (entrenamiento individual/múltiple)       #
    # ════════════════════════════════════════════════════════════ #
    def _on_train_models(self):
        if self.current_df is None:
            messagebox.showwarning("Sin datos", "Primero carga un dataset.")
            return
        cands = self.ml.get_target_candidates(self.current_df)
        ModelDialog(self.root,
                    candidatos=cands,
                    mode="train",
                    callback=self._run_train_models)

    def _run_train_models(self, selected_models, target_col):
        self._clear_log()
        self._log(f"⏳  Entrenando {len(selected_models)} modelo(s)...", "info")
        self._log(f"   Target: '{target_col}'", "info")
        self._log(f"   Modelos: {', '.join(selected_models)}", "info")
        self._set_status("⏳ Entrenando modelos...")
        self._show_cancel()
        self.root.update_idletasks()

        df_snap = self.current_df.copy()

        def on_progress(nombre, i, total):
            self.root.after(0, lambda: self._log(
                f"   ▸ ({i}/{total}) Entrenando: {nombre}...", "accent"))

        def run():
            try:
                res, feats, classes, cancelado = self.ml.train_models(
                    df_snap, target_col, selected_models,
                    cancel_check=lambda: self._ml_cancel.is_set(),
                    progress_callback=on_progress
                )
                self.root.after(0, lambda: self._train_done(
                    res, feats, classes, target_col, cancelado))
            except Exception as e:
                self.root.after(0, lambda: self._ml_err(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _train_done(self, resultados, feats, classes, target_col, cancelado):
        self._hide_cancel()
        self._clear_log()

        if cancelado:
            self._log("⛔  Entrenamiento cancelado por el usuario.", "warn")
            self._log(f"   Se completaron {len(resultados)} de los modelos seleccionados.", "info")
        else:
            self._log("✓  Entrenamiento completado.", "ok")

        self._log(f"   Target   : {target_col}", "info")
        self._log(f"   Features : {', '.join(feats)}", "info")
        self._log(f"   Clases   : {', '.join(str(c) for c in classes)}", "info")

        for r in resultados:
            self._log("", "")
            self._log(f"{'─'*50}", "header")
            self._log(f"  🤖  {r['nombre']}", "header")
            self._log(f"{'─'*50}", "header")
            self._log(f"  Accuracy : {r['accuracy']}", "accent")
            self._log(f"  F1 Score : {r['f1']}", "accent")
            self._log(f"  Train    : {r['train']}  |  Test : {r['test']}", "info")
            self._log("", "")
            self._log("  Reporte detallado:", "info")
            self._log(r["report"], "info")

            if r["importances"]:
                self._log("  Importancia de features (top 5):", "info")
                for feat, val in list(r["importances"].items())[:5]:
                    bar = "█" * int(val * 30)
                    self._log(f"   {feat:<22} {bar}  {val:.4f}", "accent")

        # Mostrar tabla resumen en Treeview
        if resultados:
            df_res = pd.DataFrame([{
                "Modelo": r["nombre"],
                "Accuracy": r["accuracy"],
                "F1 Score": r["f1"],
                "Train": r["train"],
                "Test": r["test"],
            } for r in resultados])
            self._update_table(df_res, f"Modelos entrenados (target: {target_col})")

        status = "⛔ Cancelado." if cancelado else f"✓ {len(resultados)} modelo(s) entrenados."
        self._set_status(status)

    # ════════════════════════════════════════════════════════════ #
    #  EVENTOS — MACHINE LEARNING                                  #
    # ════════════════════════════════════════════════════════════ #
    def _on_compare_models(self):
        if self.current_df is None:
            messagebox.showwarning("Sin datos", "Primero carga un dataset.")
            return
        cands = self.ml.get_target_candidates(self.current_df)
        ModelDialog(self.root,
                    candidatos=cands,
                    mode="compare",
                    callback=self._run_compare_models)

    def _run_compare_models(self, selected_models, target_col):
        self._clear_log()
        self._log(f"⏳  Comparando {len(selected_models)} modelos...", "info")
        self._log(f"   Target: '{target_col}'", "info")
        self._set_status("⏳ Comparando modelos...")
        self._show_cancel()
        self.root.update_idletasks()

        df_snap = self.current_df.copy()

        def on_progress(nombre, i, total):
            self.root.after(0, lambda: self._log(
                f"   ▸ ({i}/{total}) Entrenando: {nombre}...", "accent"))

        def run():
            try:
                df_res, feats, classes, mejor, rep, cancelado = self.ml.compare_models(
                    df_snap, target_col, selected_models,
                    cancel_check=lambda: self._ml_cancel.is_set(),
                    progress_callback=on_progress
                )
                self.root.after(0, lambda: self._compare_done(
                    df_res, feats, classes, mejor, rep, target_col, cancelado))
            except Exception as e:
                self.root.after(0, lambda: self._ml_err(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _compare_done(self, df_res, feats, classes, mejor, rep, target_col, cancelado):
        self._hide_cancel()
        self._clear_log()

        if not df_res.empty:
            self._update_table(df_res,
                f"Comparación de modelos (target: {target_col})")

        if cancelado:
            self._log("⛔  Comparación cancelada.", "warn")
            self._log(f"   Se compararon {len(df_res)} modelo(s).", "info")
        else:
            self._log("✓  Comparación completada.", "ok")

        self._log(f"   Target   : {target_col}", "info")
        self._log(f"   Features : {', '.join(feats)}", "info")
        self._log(f"   Clases   : {', '.join(str(c) for c in classes)}", "info")

        if mejor:
            self._log("", "")
            self._log(f"   🏆  Mejor modelo: {mejor}", "accent")
            self._log("", "")
            self._log("─── Reporte del mejor modelo ───", "header")
            self._log(rep, "info")

        self._set_status("⛔ Cancelado." if cancelado else "✓ Comparación completada.")

    def _on_clustering(self):
        if self.current_df is None:
            messagebox.showwarning("Sin datos", "Primero carga un dataset.")
            return
        ClusterDialog(self.root, callback=self._run_clustering)

    def _run_clustering(self, n_clusters):
        self._clear_log()
        self._log(f"⏳  K-Means (K={n_clusters}) + PCA...", "info")
        self._set_status("⏳ Clustering en progreso...")
        self.root.update_idletasks()

        df_snap = self.current_df.copy()

        def run():
            try:
                df_res, var, cols, inercia = self.ml.cluster_and_pca(
                    df_snap, n_clusters)
                self.root.after(0, lambda: self._cluster_done(
                    df_res, var, cols, inercia, n_clusters))
            except Exception as e:
                self.root.after(0, lambda: self._ml_err(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _cluster_done(self, df_res, var, cols, inercia, n_clusters):
        self._update_table(df_res, f"Clustering K-Means K={n_clusters} + PCA")
        self._clear_log()
        self._log("✓  Clustering + PCA completado.", "ok")
        self._log(f"   Clusters  : {n_clusters}", "info")
        self._log(f"   Columnas  : {', '.join(cols)}", "info")
        self._log(f"   Inercia   : {inercia}", "info")
        self._log("", "")
        self._log("── Varianza explicada por PCA ──", "header")
        for i, v in enumerate(var, 1):
            self._log(f"   PCA_{i}: {v}%", "accent")
        self._log(f"   Total: {sum(var)}%", "ok" if sum(var) > 70 else "warn")
        self._log("", "")
        self._log("── Distribución de clusters ──", "header")
        dist = df_res["cluster"].value_counts().sort_index()
        for cl, cnt in dist.items():
            self._log(f"   Cluster {int(cl)}: {cnt} registros", "info")
        self._set_status(f"✓ Clustering K={n_clusters} completado.")

    def _ml_err(self, msg):
        self._hide_cancel()
        messagebox.showerror("Error ML", msg)
        self._log(f"✗  {msg}", "err")
        self._set_status("Error en ML.")

    # ── Arranque ──────────────────────────────────────────────── #
    def run(self):
        self._log("🚀  Aplicación iniciada. Selecciona una fuente de datos.", "ok")
        self._log("   Sección MODELOS       → entrena uno o más modelos con reporte detallado.", "info")
        self._log("   Sección ML            → compara modelos o aplica clustering + PCA.", "info")
        self._log("   PostgreSQL            → recuerda tus consultas anteriores.", "info")
        self._log("─" * 55, "")
        self.root.mainloop()


# ══════════════════════════════════════════════════════════════════ #
#  DIÁLOGO DE SELECCIÓN DE MODELOS                                   #
# ══════════════════════════════════════════════════════════════════ #
class ModelDialog:
    """
    Diálogo con checkboxes para seleccionar modelos y columna target.
    Usado tanto por MODELOS (mode='train') como por COMPARAR (mode='compare').
    """

    DESCRIPTIONS = {
        "Logistic Regression": "Modelo lineal probabilístico (sigmoide)",
        "KNN (k=5)":           "Clasifica por los 5 vecinos más cercanos",
        "SVM (RBF)":           "Hiperplano de máximo margen (kernel RBF)",
        "Random Forest":       "Ensemble de 100 árboles de decisión",
        "Decision Tree":       "Árbol if-then, profundidad máx. 5",
    }

    def __init__(self, parent, candidatos, mode, callback):
        self.callback = callback
        self.mode     = mode

        self.win = tk.Toplevel(parent)
        self.win.title(
            "Entrenar Modelo(s)" if mode == "train" else "Comparar Modelos")
        self.win.geometry("480x420")
        self.win.configure(bg="#1a1b2e")
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        self._center(parent)
        self._build(candidatos)

    def _center(self, parent):
        self.win.update_idletasks()
        x = parent.winfo_x() + parent.winfo_width()  // 2 - 240
        y = parent.winfo_y() + parent.winfo_height() // 2 - 210
        self.win.geometry(f"+{x}+{y}")

    def _build(self, candidatos):
        main = tk.Frame(self.win, bg="#1a1b2e", padx=20, pady=16)
        main.pack(fill=tk.BOTH, expand=True)

        icon = "🎯" if self.mode == "train" else "📊"
        titulo = "Entrenar Modelo(s)" if self.mode == "train" else "Comparar Modelos"
        tk.Label(main, text=f"{icon}  {titulo}",
                 font=("Segoe UI", 13, "bold"),
                 bg="#1a1b2e", fg="#e2e8f0"
                 ).pack(anchor=tk.W, pady=(0, 12))

        # ── Checkboxes de modelos ── #
        tk.Label(main, text="Selecciona los modelos:",
                 font=("Segoe UI", 9, "bold"),
                 bg="#1a1b2e", fg="#94a3b8"
                 ).pack(anchor=tk.W, pady=(0, 4))

        self.checks = {}
        for nombre, desc in self.DESCRIPTIONS.items():
            var = tk.BooleanVar(value=True)
            self.checks[nombre] = var
            row = tk.Frame(main, bg="#1e2039", pady=4)
            row.pack(fill=tk.X, pady=2)
            tk.Checkbutton(
                row, text=f"  {nombre}", variable=var,
                font=("Segoe UI", 10, "bold"),
                bg="#1e2039", fg="#e2e8f0",
                selectcolor="#533483",
                activebackground="#1e2039",
                activeforeground="#c084fc"
            ).pack(side=tk.LEFT)
            tk.Label(row, text=desc, font=("Segoe UI", 8),
                     bg="#1e2039", fg="#64748b"
                     ).pack(side=tk.LEFT, padx=(4, 0))

        # ── Columna target ── #
        tk.Label(main, text="Columna target (variable a predecir):",
                 font=("Segoe UI", 9, "bold"),
                 bg="#1a1b2e", fg="#94a3b8"
                 ).pack(anchor=tk.W, pady=(14, 4))

        self.combo = ttk.Combobox(main, values=candidatos,
                                   state="readonly", width=38)
        if candidatos:
            self.combo.set(candidatos[0])
        self.combo.pack(fill=tk.X, pady=(0, 14))

        # ── Botones ── #
        btns = tk.Frame(main, bg="#1a1b2e")
        btns.pack(fill=tk.X)

        action_color = "#065f46" if self.mode == "train" else "#1b6ca8"
        action_text  = "  🚀  Entrenar  " if self.mode == "train" else "  📊  Comparar  "
        tk.Button(btns, text=action_text, command=self._confirm,
                  bg=action_color, fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, cursor="hand2",
                  padx=12, pady=8
                  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        tk.Button(btns, text="  Cancelar  ", command=self.win.destroy,
                  bg="#374151", fg="white",
                  font=("Segoe UI", 10),
                  relief=tk.FLAT, cursor="hand2",
                  padx=12, pady=8
                  ).pack(side=tk.LEFT)

    def _confirm(self):
        selected = [n for n, v in self.checks.items() if v.get()]
        if not selected:
            messagebox.showwarning("Sin modelos",
                "Selecciona al menos un modelo.", parent=self.win)
            return
        target = self.combo.get().strip()
        if not target:
            messagebox.showwarning("Sin target",
                "Selecciona la columna target.", parent=self.win)
            return
        self.win.destroy()
        self.callback(selected, target)


# ══════════════════════════════════════════════════════════════════ #
#  DIÁLOGO DE CLUSTERING                                             #
# ══════════════════════════════════════════════════════════════════ #
class ClusterDialog:
    def __init__(self, parent, callback):
        self.callback = callback
        self.win = tk.Toplevel(parent)
        self.win.title("Clustering K-Means + PCA")
        self.win.geometry("360x180")
        self.win.configure(bg="#1a1b2e")
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        x = parent.winfo_x() + parent.winfo_width()  // 2 - 180
        y = parent.winfo_y() + parent.winfo_height() // 2 - 90
        self.win.geometry(f"+{x}+{y}")
        self._build()

    def _build(self):
        main = tk.Frame(self.win, bg="#1a1b2e", padx=20, pady=16)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(main, text="🔵  K-Means Clustering + PCA",
                 font=("Segoe UI", 12, "bold"),
                 bg="#1a1b2e", fg="#e2e8f0"
                 ).pack(anchor=tk.W, pady=(0, 10))

        tk.Label(main,
                 text="Agrupa los registros y reduce a 2D con PCA.\n"
                      "Se añaden columnas: cluster, PCA_1, PCA_2.",
                 font=("Segoe UI", 9),
                 bg="#1a1b2e", fg="#94a3b8", justify=tk.LEFT
                 ).pack(anchor=tk.W, pady=(0, 10))

        row = tk.Frame(main, bg="#1a1b2e")
        row.pack(fill=tk.X, pady=(0, 14))

        tk.Label(row, text="Número de clusters (K):",
                 font=("Segoe UI", 9), bg="#1a1b2e", fg="#94a3b8"
                 ).pack(side=tk.LEFT)

        self.spin = tk.Spinbox(row, from_=2, to=10, width=4,
                               font=("Segoe UI", 10), bg="#0d0d1a",
                               fg="#e2e8f0", relief=tk.FLAT)
        self.spin.delete(0, tk.END)
        self.spin.insert(0, "3")
        self.spin.pack(side=tk.LEFT, padx=(10, 0))

        btns = tk.Frame(main, bg="#1a1b2e")
        btns.pack(fill=tk.X)
        tk.Button(btns, text="  Ejecutar  ", command=self._confirm,
                  bg="#1e3a5f", fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, cursor="hand2", padx=10, pady=6
                  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        tk.Button(btns, text="Cancelar", command=self.win.destroy,
                  bg="#374151", fg="white",
                  font=("Segoe UI", 10), relief=tk.FLAT, cursor="hand2",
                  padx=10, pady=6
                  ).pack(side=tk.LEFT)

    def _confirm(self):
        try:
            k = int(self.spin.get())
        except ValueError:
            k = 3
        self.win.destroy()
        self.callback(k)


# ══════════════════════════════════════════════════════════════════ #
#  DIÁLOGO POSTGRESQL (con historial + explorador)                   #
# ══════════════════════════════════════════════════════════════════ #
class DBDialog:
    """
    Diálogo de conexión a PostgreSQL con dos pestañas:
      - Consulta SQL : conexión + historial de queries
      - Explorar BD  : tablas y columnas disponibles
    """

    DEFAULTS = {
        "host": "localhost", "database": "pokedex",
        "user": "postgres",  "password": "", "port": "5432",
    }

    def __init__(self, parent, history, callback):
        self.callback    = callback
        self.history     = history   # lista compartida con MainWindow
        self._db         = None      # conexión temporal para explorar

        self.win = tk.Toplevel(parent)
        self.win.title("Conexión a PostgreSQL")
        self.win.geometry("500x460")
        self.win.configure(bg="#1a1b2e")
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        x = parent.winfo_x() + parent.winfo_width()  // 2 - 250
        y = parent.winfo_y() + parent.winfo_height() // 2 - 230
        self.win.geometry(f"+{x}+{y}")

        self._build()

    def _build(self):
        # ── Campos de conexión (comunes a las dos pestañas) ── #
        top = tk.Frame(self.win, bg="#1a1b2e", padx=18, pady=12)
        top.pack(fill=tk.X)

        tk.Label(top, text="🐘  Conexión a PostgreSQL",
                 font=("Segoe UI", 12, "bold"),
                 bg="#1a1b2e", fg="#e2e8f0"
                 ).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        campos = [
            ("Host:",     "host",     0, 0),
            ("BD:",       "database", 0, 2),
            ("Usuario:",  "user",     1, 0),
            ("Contraseña:","password",1, 2),
            ("Puerto:",   "port",     2, 0),
        ]
        self.entries = {}
        for label, key, r, c in campos:
            tk.Label(top, text=label, font=("Segoe UI", 9),
                     bg="#1a1b2e", fg="#94a3b8"
                     ).grid(row=r, column=c, sticky=tk.W, pady=3, padx=(0, 4))
            e = ttk.Entry(top, width=16)
            e.insert(0, self.DEFAULTS.get(key, ""))
            if key == "password":
                e.configure(show="*")
            e.grid(row=r, column=c+1, sticky=tk.EW, pady=3, padx=(0, 10))
            self.entries[key] = e

        top.columnconfigure(1, weight=1)
        top.columnconfigure(3, weight=1)

        # ── Botón conectar para explorar ── #
        tk.Button(top, text="Conectar para explorar →",
                  command=self._connect_explore,
                  bg="#374151", fg="white",
                  font=("Segoe UI", 8), relief=tk.FLAT, cursor="hand2",
                  padx=6, pady=3
                  ).grid(row=2, column=2, columnspan=2, sticky=tk.E, pady=3)

        ttk.Separator(self.win, orient="horizontal").pack(fill=tk.X, padx=10)

        # ── Notebook (dos pestañas) ── #
        nb = ttk.Notebook(self.win)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Pestaña 1: Consulta SQL
        tab1 = tk.Frame(nb, bg="#1a1b2e")
        nb.add(tab1, text="  Consulta SQL  ")
        self._build_query_tab(tab1)

        # Pestaña 2: Explorar BD
        tab2 = tk.Frame(nb, bg="#1a1b2e")
        nb.add(tab2, text="  Explorar BD  ")
        self._build_explorer_tab(tab2)

    def _build_query_tab(self, parent):
        tk.Label(parent, text="Consulta SQL:",
                 font=("Segoe UI", 9, "bold"),
                 bg="#1a1b2e", fg="#94a3b8"
                 ).pack(anchor=tk.W, padx=10, pady=(8, 2))

        # Historial de consultas
        if self.history:
            tk.Label(parent, text="Historial (selecciona para reusar):",
                     font=("Segoe UI", 8),
                     bg="#1a1b2e", fg="#64748b"
                     ).pack(anchor=tk.W, padx=10)
            self.hist_combo = ttk.Combobox(
                parent, values=self.history, state="readonly", width=58)
            self.hist_combo.pack(fill=tk.X, padx=10, pady=(2, 6))
            self.hist_combo.bind("<<ComboboxSelected>>", self._on_history_select)

        # Área de escritura de la query
        self.txt_query = tk.Text(
            parent, height=4, font=("Consolas", 9),
            bg="#0d0d1a", fg="#e2e8f0",
            insertbackground="white", wrap=tk.WORD)
        self.txt_query.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)

        # Query por defecto
        default_q = self.history[0] if self.history else "SELECT * FROM pokemon ORDER BY numero LIMIT 50;"
        self.txt_query.insert("1.0", default_q)

        # Botones
        btns = tk.Frame(parent, bg="#1a1b2e")
        btns.pack(fill=tk.X, padx=10, pady=(6, 8))
        tk.Button(btns, text="  🚀  Ejecutar consulta  ",
                  command=self._execute_query,
                  bg="#533483", fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, cursor="hand2",
                  padx=10, pady=7
                  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        tk.Button(btns, text="Cancelar",
                  command=self.win.destroy,
                  bg="#374151", fg="white",
                  font=("Segoe UI", 10),
                  relief=tk.FLAT, cursor="hand2",
                  padx=10, pady=7
                  ).pack(side=tk.LEFT)

    def _build_explorer_tab(self, parent):
        tk.Label(parent,
                 text="Presiona 'Conectar para explorar' arriba para ver tablas.",
                 font=("Segoe UI", 9), bg="#1a1b2e", fg="#94a3b8"
                 ).pack(pady=(12, 6))

        paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL,
                               bg="#1a1b2e", sashwidth=4)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Panel tablas
        left = tk.Frame(paned, bg="#1a1b2e")
        paned.add(left, width=180)
        tk.Label(left, text="Tablas", font=("Segoe UI", 9, "bold"),
                 bg="#1a1b2e", fg="#94a3b8").pack(anchor=tk.W)
        self.lst_tables = tk.Listbox(left, bg="#0d0d1a", fg="#e2e8f0",
                                     font=("Consolas", 9),
                                     selectbackground="#533483",
                                     relief=tk.FLAT, borderwidth=0)
        self.lst_tables.pack(fill=tk.BOTH, expand=True)
        self.lst_tables.bind("<<ListboxSelect>>", self._on_table_select)

        # Panel columnas
        right = tk.Frame(paned, bg="#1a1b2e")
        paned.add(right)
        tk.Label(right, text="Columnas", font=("Segoe UI", 9, "bold"),
                 bg="#1a1b2e", fg="#94a3b8").pack(anchor=tk.W)
        self.lst_cols = tk.Listbox(right, bg="#0d0d1a", fg="#e2e8f0",
                                   font=("Consolas", 9),
                                   selectbackground="#533483",
                                   relief=tk.FLAT, borderwidth=0)
        self.lst_cols.pack(fill=tk.BOTH, expand=True)

        # Botón "Usar esta tabla"
        tk.Button(parent,
                  text="↑ Cargar SELECT * de tabla seleccionada",
                  command=self._use_selected_table,
                  bg="#1e3a5f", fg="white",
                  font=("Segoe UI", 9), relief=tk.FLAT, cursor="hand2",
                  padx=8, pady=5
                  ).pack(fill=tk.X, padx=8, pady=(4, 6))

    def _on_history_select(self, event=None):
        """Carga la query del historial en el Text de consulta."""
        sel = self.hist_combo.get()
        if sel:
            self.txt_query.delete("1.0", tk.END)
            self.txt_query.insert("1.0", sel)

    def _connect_explore(self):
        """Conecta y puebla la lista de tablas (en hilo secundario)."""
        # Leer valores ANTES de iniciar el hilo (los widgets siguen vivos aquí)
        params = {k: e.get() for k, e in self.entries.items()}

        self.lst_tables.delete(0, tk.END)
        self.lst_tables.insert(tk.END, "Conectando...")

        def run():
            try:
                db = DatabaseManager(
                    params["host"], params["database"], params["user"],
                    params["password"], int(params["port"] or 5432)
                )
                db.connect()
                tablas = db.get_tables()
                db.disconnect()
                self.win.after(0, lambda: self._explore_done(tablas, params))
            except Exception as e:
                self.win.after(0, lambda: self._explore_err(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _explore_done(self, tablas, params):
        if not self.win.winfo_exists():
            return
        self.lst_tables.delete(0, tk.END)
        for t in tablas:
            self.lst_tables.insert(tk.END, t)
        self._explore_params = params

    def _explore_err(self, msg):
        if not self.win.winfo_exists():
            return
        self.lst_tables.delete(0, tk.END)
        messagebox.showerror("Error de conexión", msg, parent=self.win)

    def _on_table_select(self, event=None):
        """Al seleccionar una tabla, muestra sus columnas (hilo secundario)."""
        sel = self.lst_tables.curselection()
        if not sel:
            return
        tabla = self.lst_tables.get(sel[0])
        if not hasattr(self, "_explore_params"):
            return
        p = self._explore_params

        self.lst_cols.delete(0, tk.END)
        self.lst_cols.insert(tk.END, "Cargando...")

        def run():
            try:
                db = DatabaseManager(
                    p["host"], p["database"], p["user"],
                    p["password"], int(p["port"] or 5432)
                )
                db.connect()
                df_cols = db.execute_query(
                    f"""SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = '{tabla}'
                        ORDER BY ordinal_position;"""
                )
                db.disconnect()
                self.win.after(0, lambda: self._cols_done(df_cols))
            except Exception as e:
                self.win.after(0, lambda: self._cols_err(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _cols_done(self, df_cols):
        if not self.win.winfo_exists():
            return
        self.lst_cols.delete(0, tk.END)
        for _, row in df_cols.iterrows():
            self.lst_cols.insert(tk.END, f"{row['column_name']}  ({row['data_type']})")

    def _cols_err(self, msg):
        if not self.win.winfo_exists():
            return
        self.lst_cols.delete(0, tk.END)
        messagebox.showerror("Error", msg, parent=self.win)

    def _use_selected_table(self):
        """Pone un SELECT * de la tabla seleccionada en el Text de query."""
        sel = self.lst_tables.curselection()
        if not sel:
            messagebox.showwarning("Sin selección",
                "Selecciona una tabla primero.", parent=self.win)
            return
        tabla = self.lst_tables.get(sel[0])
        query = f"SELECT * FROM {tabla} LIMIT 100;"
        self.txt_query.delete("1.0", tk.END)
        self.txt_query.insert("1.0", query)

    def _execute_query(self):
        query = self.txt_query.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Sin consulta",
                "Escribe una consulta SQL.", parent=self.win)
            return
        # IMPORTANTE: leer todos los valores ANTES de destruir la ventana.
        # destroy() elimina los widgets Entry; si se leen después, Tkinter
        # lanza un error silencioso y el callback nunca se ejecuta.
        host     = self.entries["host"].get()
        database = self.entries["database"].get()
        user     = self.entries["user"].get()
        password = self.entries["password"].get()
        port     = self.entries["port"].get()
        self.win.destroy()
        self.callback(host, database, user, password, port, query)
