#!/usr/bin/env python3
"""
visualizer.py
-------------
Interfaz grafica avanzada (Tkinter + matplotlib) para exploracion, analisis,
benchmarking y pruebas del problema de Cobertura de Vertices (Vertex Cover).

Caracteristicas principales:
  1. Modo Visual y Modo Analitico con Umbral Inteligente:
     - Grafos pequenos/medianos (<= umbral, ej. 35 nodos): Trazado del grafo con
       resaltado de cobertura, router IDs y conexiones.
     - Grafos grandes (> umbral): Activa automaticamente el Modo Analitico para
       evitar saturacion visual, mostrando dashboards comparativos de tamanio |C|,
       tiempos de ejecucion (ms) y memoria pico (KiB).
  2. Ejecucion Integrada de Pruebas y Experimentos (sin necesidad de consola):
     - Boton y dialogo interactivo para ejecutar la suite pytest (58 pruebas).
     - Boton y dialogo para ejecutar la suite experimental completa de benchmarking.
     - Visualizador emergente del analisis teorico de complejidad formal (Avance 6).
     - Visor directo de los graficos analiticos de la Entrega 2 (Avance 7).
  3. Carga rapida de instancias predefinidas (example_small, network_backbone_18)
     y generadores parametricos de redes Erdos-Renyi y Barabasi-Albert.
  4. Medicion instrumentada en tiempo real de tiempo de CPU y memoria pico (KiB).
"""

from __future__ import annotations

import os
import random
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from src import viz
from src.graph import Graph, InvalidInstanceError
from src.solver import VertexCoverSolver, ALGORITHMS_REGISTRY
from src.verify import approximation_ratio, is_vertex_cover
from src.complexity import get_complexity_table_str

ROOT_DIR = Path(__file__).resolve().parent
INSTANCES_DIR = ROOT_DIR / "data" / "instances"
RESULTS_DIR = ROOT_DIR / "experiments" / "results"

MODELS = {
    "Erdos-Renyi G(n, p)": "er",
    "Barabasi-Albert (backbone)": "ba",
}
LAYOUTS = {
    "Spring (fuerza)": "spring",
    "Circular": "circular",
    "Kamada-Kawai": "kamada",
    "Shell (anillos)": "shell",
}
ALGO_KEYS = list(ALGORITHMS_REGISTRY.keys())
EXACT_KEYS = {"exact", "ilp"}
MAX_BRUTEFORCE = 20


class AsyncCommandDialog(tk.Toplevel):
    """Ventana de dialogo para ejecutar comandos largos (pytest, benchmark) en segundo plano."""

    def __init__(self, parent: tk.Tk, title: str, cmd: list[str], success_msg: str, on_finish=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("860x520")
        self.minsize(700, 400)
        self.transient(parent)

        self.cmd = cmd
        self.success_msg = success_msg
        self.on_finish = on_finish

        top_frame = ttk.Frame(self, padding=(10, 8))
        top_frame.pack(fill="x")

        self.status_var = tk.StringVar(value="Iniciando ejecucion...")
        self.status_label = ttk.Label(top_frame, textvariable=self.status_var, font=("Segoe UI", 10, "bold"))
        self.status_label.pack(side="left")

        self.prog = ttk.Progressbar(top_frame, mode="indeterminate", length=200)
        self.prog.pack(side="right", padx=10)
        self.prog.start(10)

        # Consola de salida estilizada
        console_frame = ttk.Frame(self, padding=(10, 0))
        console_frame.pack(fill="both", expand=True)

        self.txt = tk.Text(
            console_frame,
            bg="#181824",
            fg="#d8dee9",
            insertbackground="white",
            font=("Consolas", 9),
            wrap="none",
        )
        self.txt.pack(side="left", fill="both", expand=True)

        sb_y = ttk.Scrollbar(console_frame, orient="vertical", command=self.txt.yview)
        sb_y.pack(side="right", fill="y")
        self.txt.configure(yscrollcommand=sb_y.set)

        bot_frame = ttk.Frame(self, padding=(10, 8))
        bot_frame.pack(fill="x")

        self.btn_close = ttk.Button(bot_frame, text="Cerrar", state="disabled", command=self.destroy)
        self.btn_close.pack(side="right")

        threading.Thread(target=self._run_process, daemon=True).start()

    def _append_text(self, text: str):
        self.txt.insert("end", text)
        self.txt.see("end")

    def _run_process(self):
        start_time = time.time()
        try:
            proc = subprocess.Popen(
                self.cmd,
                cwd=str(ROOT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            for line in proc.stdout:
                self.after(0, self._append_text, line)
            proc.wait()
            elapsed = time.time() - start_time

            if proc.returncode == 0:
                final_status = f"{self.success_msg} (Tiempo: {elapsed:.2f} s)"
                color = "#008800"
            else:
                final_status = f"Finalizo con codigo de error {proc.returncode} (Tiempo: {elapsed:.2f} s)"
                color = "#cc0000"

            def finish_ui():
                self.prog.stop()
                self.prog.pack_forget()
                self.status_var.set(final_status)
                self.status_label.configure(foreground=color)
                self.btn_close.configure(state="normal")
                if self.on_finish:
                    self.on_finish(proc.returncode)

            self.after(0, finish_ui)
        except Exception as exc:
            def error_ui():
                self.prog.stop()
                self.prog.pack_forget()
                self.status_var.set(f"Error al ejecutar: {exc}")
                self.status_label.configure(foreground="#cc0000")
                self.btn_close.configure(state="normal")

            self.after(0, error_ui)


class VertexCoverApp:
    """Ventana principal del visualizador y entorno de pruebas de Vertex Cover."""

    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Vertex Cover IDS - Entorno Visual y Experimental (Avances 1 al 7)")
        root.geometry("1260x780")
        root.minsize(1050, 680)

        self.graph: Graph | None = None
        self.instance_name = "(sin instancia)"
        self.positions = None
        self.layout_seed = 1
        self.results: dict[str, dict] = {}
        self.optimal_size: int | None = None

        # Umbral configurable para evitar grafos saturados
        self.threshold_var = tk.IntVar(value=35)
        self.smart_mode_var = tk.BooleanVar(value=True)

        self._build_menu()
        self._build_ui()
        self._load_preset("example_small.json")

    # ------------------------------------------------------------------
    # Barra de Menus Superior
    # ------------------------------------------------------------------
    def _build_menu(self):
        menubar = tk.Menu(self.root)

        # Menu Archivo
        m_file = tk.Menu(menubar, tearoff=False)
        m_file.add_command(label="Cargar instancia JSON...", command=self._load_json)
        m_file.add_separator()
        m_file.add_command(label="Cargar Ejemplo (6 routers)", command=lambda: self._load_preset("example_small.json"))
        m_file.add_command(label="Cargar Backbone (18 routers)", command=lambda: self._load_preset("network_backbone_18.json"))
        m_file.add_separator()
        m_file.add_command(label="Guardar vista actual en PNG...", command=self._save_png)
        m_file.add_command(label="Exportar grafo actual a JSON...", command=self._save_json)
        m_file.add_separator()
        m_file.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=m_file)

        # Menu Algoritmos
        m_algos = tk.Menu(menubar, tearoff=False)
        m_algos.add_command(label="Ejecutar seleccionados", command=self._run_algorithms)
        m_algos.add_command(label="Marcar todos", command=lambda: self._set_all_algos(True))
        m_algos.add_command(label="Desmarcar todos", command=lambda: self._set_all_algos(False))
        menubar.add_cascade(label="Algoritmos", menu=m_algos)

        # Menu Pruebas y Experimentos (Avance 6 y 7)
        m_tools = tk.Menu(menubar, tearoff=False)
        m_tools.add_command(label="Ejecutar Bateria pytest (58 pruebas)...", command=self._run_pytest_dialog)
        m_tools.add_command(label="Ejecutar Benchmark Experimental...", command=self._run_benchmark_dialog)
        m_tools.add_separator()
        m_tools.add_command(label="Ver Analisis de Complejidad (Avance 6)", command=self._show_complexity_dialog)
        m_tools.add_command(label="Ver Graficos Guardados Entrega 2 (Avance 7)", command=self._show_plots_dialog)
        menubar.add_cascade(label="Pruebas y Experimentos", menu=m_tools)

        # Menu Ayuda
        m_help = tk.Menu(menubar, tearoff=False)
        m_help.add_command(label="Bitacora del Proyecto...", command=self._show_bitacora_dialog)
        m_help.add_command(label="Acerca del Proyecto (Grupo 1)", command=self._show_about_dialog)
        menubar.add_cascade(label="Ayuda", menu=m_help)

        self.root.config(menu=menubar)

    # ------------------------------------------------------------------
    # Construccion de la Interfaz
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(self.root, padding=(10, 8))
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)

        plot_panel = ttk.Frame(self.root, padding=(0, 8, 8, 8))
        plot_panel.grid(row=0, column=1, sticky="nsew")
        plot_panel.rowconfigure(0, weight=1)
        plot_panel.columnconfigure(0, weight=1)

        # Pestanias en el panel izquierdo
        self.notebook = ttk.Notebook(left_panel, width=390)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        tab_inst = ttk.Frame(self.notebook, padding=8)
        tab_algos = ttk.Frame(self.notebook, padding=8)
        tab_tools = ttk.Frame(self.notebook, padding=8)

        self.notebook.add(tab_inst, text=" 1. Instancia ")
        self.notebook.add(tab_algos, text=" 2. Algoritmos ")
        self.notebook.add(tab_tools, text=" 3. Pruebas & Tests ")

        self._build_tab_instance(tab_inst)
        self._build_tab_algorithms(tab_algos)
        self._build_tab_tools(tab_tools)
        self._build_plot_canvas(plot_panel)

    def _build_tab_instance(self, parent: ttk.Frame):
        parent.columnconfigure(0, weight=1)
        r = 0

        # Presets rapidos
        lbl_p = ttk.Label(parent, text="Instancias Predefinidas", font=("Segoe UI", 9, "bold"))
        lbl_p.grid(row=r, column=0, sticky="w", pady=(0, 2))
        r += 1

        f_presets = ttk.Frame(parent)
        f_presets.grid(row=r, column=0, sticky="ew", pady=(0, 6))
        f_presets.columnconfigure(0, weight=1)
        f_presets.columnconfigure(1, weight=1)
        ttk.Button(f_presets, text="Ejemplo 6 Nodos", command=lambda: self._load_preset("example_small.json")).grid(
            row=0, column=0, sticky="ew", padx=(0, 2)
        )
        ttk.Button(f_presets, text="Backbone 18 Nodos", command=lambda: self._load_preset("network_backbone_18.json")).grid(
            row=0, column=1, sticky="ew", padx=(2, 0)
        )
        r += 1

        ttk.Button(parent, text="Abrir Archivo JSON...", command=self._load_json).grid(
            row=r, column=0, sticky="ew", pady=(0, 6)
        )
        r += 1

        self.instance_label = ttk.Label(parent, text="Instancia: -", foreground="#004488", font=("Segoe UI", 9, "bold"))
        self.instance_label.grid(row=r, column=0, sticky="w", pady=(0, 6))
        r += 1

        ttk.Separator(parent).grid(row=r, column=0, sticky="ew", pady=4)
        r += 1

        # Generador aleatorio
        gen = ttk.LabelFrame(parent, text="Generador de Redes Aleatorias", padding=8)
        gen.grid(row=r, column=0, sticky="ew", pady=4)
        gen.columnconfigure(1, weight=1)
        gr = 0

        ttk.Label(gen, text="Modelo:").grid(row=gr, column=0, sticky="w")
        self.model_var = tk.StringVar(value="Erdos-Renyi G(n, p)")
        ttk.Combobox(gen, textvariable=self.model_var, values=list(MODELS), state="readonly", width=20).grid(
            row=gr, column=1, sticky="ew", padx=(4, 0)
        )
        gr += 1

        ttk.Label(gen, text="Nodos n:").grid(row=gr, column=0, sticky="w")
        self.n_var = tk.IntVar(value=14)
        ttk.Spinbox(gen, from_=2, to=300, textvariable=self.n_var, width=10).grid(
            row=gr, column=1, sticky="w", padx=(4, 0), pady=2
        )
        gr += 1

        ttk.Label(gen, text="Prob. p (ER):").grid(row=gr, column=0, sticky="w")
        self.p_var = tk.StringVar(value="0.3")
        ttk.Entry(gen, textvariable=self.p_var, width=10).grid(row=gr, column=1, sticky="w", padx=(4, 0), pady=2)
        gr += 1

        ttk.Label(gen, text="Param m (BA):").grid(row=gr, column=0, sticky="w")
        self.m_var = tk.StringVar(value="2")
        ttk.Entry(gen, textvariable=self.m_var, width=10).grid(row=gr, column=1, sticky="w", padx=(4, 0), pady=2)
        gr += 1

        ttk.Label(gen, text="Semilla:").grid(row=gr, column=0, sticky="w")
        seed_f = ttk.Frame(gen)
        seed_f.grid(row=gr, column=1, sticky="w", padx=(4, 0), pady=2)
        self.seed_var = tk.StringVar(value="42")
        ttk.Entry(seed_f, textvariable=self.seed_var, width=8).pack(side="left")
        ttk.Button(seed_f, text="Azar", width=5, command=self._randomize_seed).pack(side="left", padx=4)
        gr += 1

        ttk.Button(gen, text="Generar Grafo", command=self._generate_random).grid(
            row=gr, column=0, columnspan=2, sticky="ew", pady=(6, 2)
        )
        r += 1

        ttk.Separator(parent).grid(row=r, column=0, sticky="ew", pady=6)
        r += 1

        # Control de Umbral y Saturacion Visual (Requerimiento Clave)
        opt_frame = ttk.LabelFrame(parent, text="Control Visual y Umbral de Saturacion", padding=8)
        opt_frame.grid(row=r, column=0, sticky="ew", pady=4)
        opt_frame.columnconfigure(1, weight=1)
        orow = 0

        ttk.Label(opt_frame, text="Umbral max. nodos:").grid(row=orow, column=0, sticky="w")
        sp_thr = ttk.Spinbox(opt_frame, from_=10, to=150, textvariable=self.threshold_var, width=8)
        sp_thr.grid(row=orow, column=1, sticky="w", padx=4)
        sp_thr.bind("<FocusOut>", lambda _: self._draw())
        sp_thr.bind("<Return>", lambda _: self._draw())
        orow += 1

        chk_mode = ttk.Checkbutton(
            opt_frame,
            text="Modo Analitico auto (si n > umbral)",
            variable=self.smart_mode_var,
            command=self._draw,
        )
        chk_mode.grid(row=orow, column=0, columnspan=2, sticky="w", pady=(4, 2))
        orow += 1

        self.show_labels_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opt_frame, text="Mostrar etiquetas de nodos", variable=self.show_labels_var, command=self._draw
        ).grid(row=orow, column=0, columnspan=2, sticky="w")
        orow += 1

        ttk.Label(opt_frame, text="Disposicion:").grid(row=orow, column=0, sticky="w", pady=(4, 0))
        self.layout_var = tk.StringVar(value="Spring (fuerza)")
        cb_lay = ttk.Combobox(opt_frame, textvariable=self.layout_var, values=list(LAYOUTS), state="readonly")
        cb_lay.grid(row=orow, column=1, sticky="ew", pady=(4, 0))
        cb_lay.bind("<<ComboboxSelected>>", lambda _: self._rearrange())
        orow += 1

        f_lay_btn = ttk.Frame(opt_frame)
        f_lay_btn.grid(row=orow, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        f_lay_btn.columnconfigure(0, weight=1)
        f_lay_btn.columnconfigure(1, weight=1)
        ttk.Button(f_lay_btn, text="Rearreglar", command=self._rearrange).grid(row=0, column=0, sticky="ew", padx=(0, 2))
        ttk.Button(f_lay_btn, text="Guardar PNG", command=self._save_png).grid(row=0, column=1, sticky="ew", padx=(2, 0))

    def _build_tab_algorithms(self, parent: ttk.Frame):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(4, weight=1)
        r = 0

        lbl = ttk.Label(parent, text="Seleccionar Algoritmos a Comparar", font=("Segoe UI", 9, "bold"))
        lbl.grid(row=r, column=0, sticky="w", pady=(0, 4))
        r += 1

        self.algo_vars: dict[str, tk.BooleanVar] = {}
        defaults = {"greedy", "greedy_pq", "matching", "ilp"}
        for key in ALGO_KEYS:
            name = ALGORITHMS_REGISTRY[key][0]
            var = tk.BooleanVar(value=(key in defaults))
            self.algo_vars[key] = var
            ttk.Checkbutton(parent, text=name, variable=var).grid(row=r, column=0, sticky="w", pady=1)
            r += 1

        btn_run = ttk.Button(parent, text="▶ Ejecutar Algoritmos", command=self._run_algorithms)
        btn_run.grid(row=r, column=0, sticky="ew", pady=(8, 6))
        r += 1

        # Selector de cobertura visual
        f_cov = ttk.Frame(parent)
        f_cov.grid(row=r, column=0, sticky="ew", pady=(0, 6))
        f_cov.columnconfigure(1, weight=1)
        ttk.Label(f_cov, text="Ver cobertura:").grid(row=0, column=0, sticky="w")
        self.show_var = tk.StringVar(value="")
        self.show_box = ttk.Combobox(f_cov, textvariable=self.show_var, values=[], state="readonly")
        self.show_box.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        self.show_box.bind("<<ComboboxSelected>>", lambda _e: self._draw())
        r += 1

        # Panel de Resultados y Metricas Detalladas
        ttk.Label(parent, text="Resultados y Metricas Instrumentadas", font=("Segoe UI", 9, "bold")).grid(
            row=r, column=0, sticky="w", pady=(4, 2)
        )
        r += 1

        stats_frame = ttk.Frame(parent)
        stats_frame.grid(row=r, column=0, sticky="nsew")
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)

        self.stats = tk.Text(stats_frame, width=46, wrap="none", font=("Consolas", 8), bg="#ffffff")
        self.stats.grid(row=0, column=0, sticky="nsew")
        sb_y = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats.yview)
        sb_y.grid(row=0, column=1, sticky="ns")
        sb_x = ttk.Scrollbar(stats_frame, orient="horizontal", command=self.stats.xview)
        sb_x.grid(row=1, column=0, sticky="ew")
        self.stats.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        r += 1

        btn_copy = ttk.Button(parent, text="Exportar Metricas a TXT...", command=self._export_metrics)
        btn_copy.grid(row=r, column=0, sticky="ew", pady=(4, 0))

    def _build_tab_tools(self, parent: ttk.Frame):
        parent.columnconfigure(0, weight=1)
        r = 0

        ttk.Label(parent, text="Herramientas y Pruebas Integradas", font=("Segoe UI", 10, "bold")).grid(
            row=r, column=0, sticky="w", pady=(0, 8)
        )
        r += 1

        # Grupo Pytest
        lf_pytest = ttk.LabelFrame(parent, text="Pruebas Automatizadas (Avance 6)", padding=8)
        lf_pytest.grid(row=r, column=0, sticky="ew", pady=4)
        lf_pytest.columnconfigure(0, weight=1)
        ttk.Label(
            lf_pytest,
            text="Ejecuta la bateria de 58 pruebas automatizadas\n(casos limite, adversarios, heap e ILP).",
            wraplength=340,
        ).pack(anchor="w", pady=(0, 4))
        ttk.Button(lf_pytest, text="🧪 Correr Suite pytest (58 pruebas)", command=self._run_pytest_dialog).pack(
            fill="x"
        )
        r += 1

        # Grupo Benchmark
        lf_bench = ttk.LabelFrame(parent, text="Protocolo Experimental (Avance 7)", padding=8)
        lf_bench.grid(row=r, column=0, sticky="ew", pady=4)
        lf_bench.columnconfigure(0, weight=1)
        ttk.Label(
            lf_bench,
            text="Ejecuta el benchmark experimental completo sobre\nredes ER y BA, generando CSV y graficos PNG.",
            wraplength=340,
        ).pack(anchor="w", pady=(0, 4))
        ttk.Button(lf_bench, text="⚡ Ejecutar Benchmark Completo", command=self._run_benchmark_dialog).pack(fill="x")
        r += 1

        # Grupo Consultas Rapidas
        lf_views = ttk.LabelFrame(parent, text="Analisis y Reportes Visuales", padding=8)
        lf_views.grid(row=r, column=0, sticky="ew", pady=4)
        lf_views.columnconfigure(0, weight=1)

        ttk.Button(lf_views, text="📊 Ver Analisis de Complejidad (Av. 6)", command=self._show_complexity_dialog).pack(
            fill="x", pady=2
        )
        ttk.Button(lf_views, text="📈 Abrir Graficos Entrega 2 (Av. 7)", command=self._show_plots_dialog).pack(
            fill="x", pady=2
        )
        ttk.Button(lf_views, text="📝 Ver Bitacora de Aprendizaje", command=self._show_bitacora_dialog).pack(
            fill="x", pady=2
        )
        r += 1

        # Info de estado
        self.status_var = tk.StringVar(value="Listo.")
        lbl_st = ttk.Label(parent, textvariable=self.status_var, foreground="#007700", wraplength=360, font=("Segoe UI", 9))
        lbl_st.grid(row=r, column=0, sticky="w", pady=(12, 0))

    def _build_plot_canvas(self, parent: ttk.Frame):
        self.fig = Figure(figsize=(7.5, 6.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        toolbar = NavigationToolbar2Tk(self.canvas, parent, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=1, column=0, sticky="ew")

    # ------------------------------------------------------------------
    # Control de Algoritmos y Utilidades
    # ------------------------------------------------------------------
    def _set_all_algos(self, state: bool):
        for var in self.algo_vars.values():
            var.set(state)

    def _parse_seed(self):
        text = self.seed_var.get().strip()
        return None if text == "" else int(text)

    def _randomize_seed(self):
        self.seed_var.set(str(random.randint(0, 10**6)))

    def _layout(self) -> str:
        return LAYOUTS.get(self.layout_var.get(), "spring")

    def _set_status(self, text: str):
        self.status_var.set(text)
        self.root.update_idletasks()

    def _set_stats(self, text: str):
        self.stats.configure(state="normal")
        self.stats.delete("1.0", "end")
        self.stats.insert("1.0", text)
        self.stats.configure(state="disabled")

    # ------------------------------------------------------------------
    # Carga y Generacion de Instancias
    # ------------------------------------------------------------------
    def _load_preset(self, filename: str):
        path = INSTANCES_DIR / filename
        if not path.exists():
            messagebox.showerror("Error", f"No se encontro el archivo preset: {path}")
            return
        try:
            self._set_graph(Graph.from_json(path), filename)
        except Exception as exc:
            messagebox.showerror("Error al cargar preset", str(exc))

    def _load_json(self):
        path = filedialog.askopenfilename(
            title="Elegir instancia JSON",
            initialdir=str(INSTANCES_DIR),
            filetypes=[("Instancias JSON", "*.json"), ("Todos los archivos", "*.*")],
        )
        if not path:
            return
        try:
            g = Graph.from_json(path)
            self._set_graph(g, Path(path).name)
        except Exception as exc:
            messagebox.showerror("No se pudo cargar", str(exc))

    def _generate_random(self):
        try:
            n = int(self.n_var.get())
            seed = self._parse_seed()
            model = MODELS[self.model_var.get()]
            if model == "er":
                p = float(self.p_var.get())
                if not 0.0 <= p <= 1.0:
                    raise ValueError("p debe estar entre 0 y 1.")
                g = Graph.random_graph(n=n, p=p, seed=seed)
                name = f"G(n={n}, p={p}), seed={seed}"
            else:
                m = int(self.m_var.get())
                if not 1 <= m < n:
                    raise ValueError("Se requiere 1 <= m < n.")
                g = Graph.barabasi_albert(n=n, m=m, seed=seed)
                name = f"Barabasi-Albert(n={n}, m={m}), seed={seed}"
        except Exception as exc:
            messagebox.showerror("Parametros invalidos", str(exc))
            return
        self._set_graph(g, name)

    def _set_graph(self, graph: Graph, name: str):
        self.graph = graph
        self.instance_name = name
        self.results = {}
        self.optimal_size = None
        self.layout_seed = random.randint(1, 10**6)

        # Solo calcular layout completo si esta dentro del umbral o si se desactiva modo analitico
        umbral = self.threshold_var.get()
        if graph.num_vertices() <= umbral or not self.smart_mode_var.get():
            self.positions = viz.compute_layout(graph, seed=self.layout_seed, layout=self._layout())
        else:
            self.positions = None

        self.show_box.configure(values=[])
        self.show_var.set("")
        self.instance_label.configure(
            text=f"{name} (|V|={graph.num_vertices()}, |E|={graph.num_edges()}, d={graph.density():.3f})"
        )
        self._fill_stats_placeholder()
        self._draw()
        self._set_status(f"Cargado: {name} (|V|={graph.num_vertices()}, |E|={graph.num_edges()})")

    def _fill_stats_placeholder(self):
        if self.graph is None:
            self._set_stats("")
            return
        g = self.graph
        umbral = self.threshold_var.get()
        modo_analitico = g.num_vertices() > umbral and self.smart_mode_var.get()
        aviso_modo = " [MODO ANALITICO ACTIVO]" if modo_analitico else " [MODO VISUAL DE GRAFO]"

        self._set_stats(
            f"Instancia : {self.instance_name}{aviso_modo}\n"
            f"Vertices  : {g.num_vertices()}\n"
            f"Aristas   : {g.num_edges()}\n"
            f"Densidad  : {g.density():.4f}\n\n"
            f"Umbral visual: {umbral} vertices.\n"
            "Ejecuta los algoritmos para ver metricas y graficos comparativos."
        )

    # ------------------------------------------------------------------
    # Resolucion y Mediciones Instrumentadas
    # ------------------------------------------------------------------
    def _run_algorithms(self):
        if self.graph is None:
            messagebox.showwarning("Sin grafo", "Primero genera o carga una instancia.")
            return

        selected_keys = [k for k in ALGO_KEYS if self.algo_vars[k].get()]
        if not selected_keys:
            messagebox.showwarning("Sin seleccion", "Selecciona al menos un algoritmo en la pestania Algoritmos.")
            return

        n = self.graph.num_vertices()
        solver = VertexCoverSolver(self.graph)
        self.results = {}
        self.optimal_size = None
        self._set_status("Ejecutando algoritmos...")

        for key in selected_keys:
            label = ALGORITHMS_REGISTRY[key][0]
            if key == "exact" and n > MAX_BRUTEFORCE:
                self.results[key] = {"label": label, "skipped": True}
                continue

            try:
                # Usar solver.solve() para garantizar medicion estandar de tiempo y memoria
                res = solver.solve(key)
                self.results[key] = res
            except Exception as exc:
                self.results[key] = {"label": label, "error": str(exc)}

        # Determinar optimo de referencia
        for key in ("exact", "ilp"):
            res = self.results.get(key)
            if res and res.get("valid"):
                sz = res["size"]
                if self.optimal_size is None or sz < self.optimal_size:
                    self.optimal_size = sz

        displayable = [ALGORITHMS_REGISTRY[k][0] for k in selected_keys if self.results.get(k, {}).get("cover") is not None]
        self.show_box.configure(values=displayable)
        if displayable:
            self.show_var.set(displayable[0])

        self._fill_stats()
        self._draw()
        self._set_status(f"Listo: {len(displayable)} algoritmo(s) completados.")

    def _fill_stats(self):
        if self.graph is None:
            return
        g = self.graph
        lines = [
            f"Instancia : {self.instance_name}",
            f"Vertices  : {g.num_vertices()}   Aristas: {g.num_edges()}   Densidad: {g.density():.4f}",
            "",
            f"{'Algoritmo':<26}{'Tam':>5}{'Val':>5}{'Tiempo(ms)':>12}{'Mem(KiB)':>10}{'Ratio':>8}",
            "-" * 68,
        ]

        for key in ALGO_KEYS:
            res = self.results.get(key)
            if res is None:
                continue
            name = res.get("label", ALGORITHMS_REGISTRY[key][0])[:25]
            if res.get("skipped"):
                lines.append(f"{name:<26}{'-':>5}{'OMIT':>5}{'-':>12}{'-':>10}  (n > 20)")
                continue
            if res.get("error"):
                lines.append(f"{name:<26}{'-':>5}{'ERR':>5}{'-':>12}{'-':>10}  {res['error'][:15]}")
                continue

            ratio_txt = "-"
            if self.optimal_size is not None and self.optimal_size > 0:
                ratio_txt = f"{approximation_ratio(res['size'], self.optimal_size):.2f}x"

            lines.append(
                f"{name:<26}{res['size']:>5}"
                f"{'SI' if res['valid'] else 'NO':>5}"
                f"{res['time_ms']:>12.3f}"
                f"{res['memory_kib']:>10.2f}"
                f"{ratio_txt:>8}"
            )

        if self.optimal_size is not None:
            lines.append("-" * 68)
            lines.append(f"Optimo exacto de referencia: {self.optimal_size} vertices.")

        self._set_stats("\n".join(lines))

    # ------------------------------------------------------------------
    # Renderizado: Modo Grafo vs. Modo Analitico por Umbral
    # ------------------------------------------------------------------
    def _rearrange(self):
        if self.graph is None:
            return
        umbral = self.threshold_var.get()
        if self.graph.num_vertices() <= umbral or not self.smart_mode_var.get():
            self.layout_seed = random.randint(1, 10**6)
            self.positions = viz.compute_layout(self.graph, seed=self.layout_seed, layout=self._layout())
        self._draw()

    def _draw(self):
        if self.graph is None:
            return

        n = self.graph.num_vertices()
        umbral = self.threshold_var.get()
        modo_analitico = n > umbral and self.smart_mode_var.get()

        self.fig.clf()

        if modo_analitico:
            self._draw_analytical_dashboard()
        else:
            self._draw_graph_topology()

        self.canvas.draw_idle()

    def _draw_graph_topology(self):
        """Dibuja la red con nodos, aristas y cobertura resaltada."""
        ax = self.fig.add_subplot(111)

        # Buscar cobertura seleccionada
        selected_label = self.show_var.get()
        cover = None
        for res in self.results.values():
            if res.get("label") == selected_label and "cover" in res:
                cover = res["cover"]
                break

        title = f"{self.instance_name}   |V|={self.graph.num_vertices()}  |E|={self.graph.num_edges()}"
        if cover is not None:
            title += f"\nCobertura mostrada: {selected_label}  ({len(cover)} vertices)"

        if self.positions is None:
            self.positions = viz.compute_layout(self.graph, seed=self.layout_seed, layout=self._layout())

        viz.draw_graph(
            ax,
            self.graph,
            cover=cover,
            positions=self.positions,
            title=title,
            show_labels=self.show_labels_var.get(),
        )

    def _draw_analytical_dashboard(self):
        """
        Dibuja un dashboard analitico comparativo en el canvas cuando el grafo
        supera el umbral de nodos, evitando saturacion visual y facilitando el analisis.
        """
        valid_results = [r for r in self.results.values() if "size" in r]

        if not valid_results:
            # Mensaje informativo cuando aun no se han corrido los algoritmos
            ax = self.fig.add_subplot(111)
            ax.axis("off")
            g = self.graph
            n = g.num_vertices()
            m = g.num_edges()
            d = g.density()
            umbral = self.threshold_var.get()

            info_text = (
                f"MODO ANALITICO AUTOMATICO ACTIVADO\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"• Instancia Actual : {self.instance_name}\n"
                f"• Vertices (|V|)   : {n}\n"
                f"• Aristas (|E|)    : {m}\n"
                f"• Densidad         : {d:.4f}\n"
                f"• Umbral Visual    : {umbral} vertices\n\n"
                f"El grafo supera el umbral visual de {umbral} nodos. Para evitar la\n"
                f"saturacion grafica (maraña ilegible de aristas) y acelerar la interfaz,\n"
                f"el trazado de red ha sido sustituido por este panel analitico.\n\n"
                f"👉 Haz clic en '▶ Ejecutar Algoritmos' en la pestania '2. Algoritmos'\n"
                f"   para generar aqui los graficos comparativos de:\n"
                f"   1. Eficiencia de Cobertura (Tamanio |C|)\n"
                f"   2. Escalabilidad Temporal (ms)\n"
                f"   3. Consumo de Memoria Pico (KiB)"
            )
            ax.text(
                0.5,
                0.5,
                info_text,
                ha="center",
                va="center",
                fontsize=11,
                fontfamily="monospace",
                bbox=dict(boxstyle="round,pad=1.2", facecolor="#f8fafc", edgecolor="#94a3b8", lw=1.5),
            )
            return

        # Dashboard con 3 graficos comparativos
        labels = [r["label"].replace(" (2-aprox)", "").replace(" (cola de prioridad)", " Heap") for r in valid_results]
        sizes = [r["size"] for r in valid_results]
        times = [max(r["time_ms"], 0.001) for r in valid_results]
        mems = [r.get("memory_kib", 0.0) for r in valid_results]

        palette = ["#22c55e", "#06b6d4", "#3b82f6", "#ef4444", "#a855f7"]
        colors = [palette[i % len(palette)] for i in range(len(labels))]

        # Panel 1: Tamanio de Cobertura
        ax1 = self.fig.add_subplot(1, 3, 1)
        bars1 = ax1.bar(labels, sizes, color=colors, width=0.55)
        ax1.set_title("Tamanio de Cobertura |C|", fontsize=10, fontweight="bold")
        ax1.set_ylabel("Numero de Routers (IDS)")
        if self.optimal_size is not None:
            ax1.axhline(self.optimal_size, color="red", linestyle="--", label=f"Optimo ({self.optimal_size})")
            ax1.legend(loc="upper right", fontsize=8)
        for b in bars1:
            ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.1, f"{int(b.get_height())}", ha="center", fontsize=9)
        ax1.tick_params(axis="x", rotation=30)
        ax1.grid(axis="y", linestyle=":", alpha=0.6)

        # Panel 2: Tiempos de Ejecucion (ms)
        ax2 = self.fig.add_subplot(1, 3, 2)
        bars2 = ax2.bar(labels, times, color=colors, width=0.55)
        ax2.set_title("Tiempo de Ejecucion (ms)", fontsize=10, fontweight="bold")
        ax2.set_ylabel("Milisegundos (escala log)")
        ax2.set_yscale("log")
        for b in bars2:
            h = b.get_height()
            ax2.text(b.get_x() + b.get_width() / 2, h * 1.15, f"{h:.2f}", ha="center", fontsize=8)
        ax2.tick_params(axis="x", rotation=30)
        ax2.grid(axis="y", linestyle=":", which="both", alpha=0.6)

        # Panel 3: Consumo de Memoria (KiB)
        ax3 = self.fig.add_subplot(1, 3, 3)
        bars3 = ax3.bar(labels, mems, color=colors, width=0.55)
        ax3.set_title("Memoria Pico (KiB)", fontsize=10, fontweight="bold")
        ax3.set_ylabel("KiB (tracemalloc)")
        for b in bars3:
            ax3.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.1, f"{b.get_height():.1f}", ha="center", fontsize=8)
        ax3.tick_params(axis="x", rotation=30)
        ax3.grid(axis="y", linestyle=":", alpha=0.6)

        self.fig.suptitle(
            f"Dashboard Analitico: {self.instance_name} (|V|={self.graph.num_vertices()}, |E|={self.graph.num_edges()})",
            fontsize=12,
            fontweight="bold",
            y=0.98,
        )
        self.fig.tight_layout(rect=[0, 0, 1, 0.94])

    # ------------------------------------------------------------------
    # Dialogos Integrados (pytest, benchmark, complejidad)
    # ------------------------------------------------------------------
    def _run_pytest_dialog(self):
        cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
        AsyncCommandDialog(
            self.root,
            title="Bateria de Pruebas Automatizadas (pytest) - Avance 6",
            cmd=cmd,
            success_msg="[OK] Suite de pruebas completada con exito (58/58 pasadas)",
        )

    def _run_benchmark_dialog(self):
        cmd = [sys.executable, "-m", "experiments.benchmark"]

        def on_bench_finish(code):
            if code == 0:
                self._set_status("Benchmark completado exitosamente. Archivos CSV y PNG generados.")
                messagebox.showinfo(
                    "Benchmark Completado",
                    "La ejecucion experimental finalizo con exito.\n"
                    f"Resultados guardados en: {RESULTS_DIR}\n\n"
                    "Puedes abrir los graficos desde el menu o con el boton 'Graficos Entrega 2'.",
                )

        AsyncCommandDialog(
            self.root,
            title="Protocolo Experimental de Benchmarking - Avance 7",
            cmd=cmd,
            success_msg="[OK] Experimento y generacion de graficos completados",
            on_finish=on_bench_finish,
        )

    def _show_complexity_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Analisis Teorico de Complejidad y Operaciones Dominantes (Avance 6)")
        win.geometry("960x440")
        win.transient(self.root)

        txt = tk.Text(win, font=("Consolas", 9), wrap="none", bg="#ffffff")
        txt.insert("1.0", get_complexity_table_str())
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=10, pady=10)

    def _show_plots_dialog(self):
        plot_path = RESULTS_DIR / "panel_consolidado_entrega2.png"
        if not plot_path.exists():
            plot_path = RESULTS_DIR / "experimentos_preliminares.png"

        if not plot_path.exists():
            messagebox.showinfo(
                "Graficos no encontrados",
                "Aun no se han generado los graficos del benchmark.\n"
                "Haz clic en '⚡ Ejecutar Benchmark Completo' en la pestania 3.",
            )
            return

        try:
            os.startfile(str(plot_path))
        except Exception as exc:
            messagebox.showerror("Error al abrir imagen", str(exc))

    def _show_bitacora_dialog(self):
        bitacora_path = ROOT_DIR / "docs" / "bitacora.md"
        if not bitacora_path.exists():
            messagebox.showinfo("Bitacora", "No se encontro docs/bitacora.md")
            return

        win = tk.Toplevel(self.root)
        win.title("Bitacora de Aprendizaje Continuo (Sesiones 1 a 7)")
        win.geometry("900x550")
        win.transient(self.root)

        txt = tk.Text(win, font=("Segoe UI", 9), wrap="word", bg="#fafafa")
        txt.insert("1.0", bitacora_path.read_text(encoding="utf-8", errors="replace"))
        txt.configure(state="disabled")
        txt.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        sb = ttk.Scrollbar(win, orient="vertical", command=txt.yview)
        sb.pack(side="right", fill="y")
        txt.configure(yscrollcommand=sb.set)

    def _show_about_dialog(self):
        msg = (
            "Proyecto: Ubicacion Optima de IDS mediante Vertex Cover\n"
            "Asignatura: Algoritmos Avanzados (UNSAAC 2026-II)\n\n"
            "Integrantes - Grupo 1:\n"
            "  • Steffano Ricardo Caballero Zegarra\n"
            "  • Adriel Alfredo Llactahuamani Ayala\n"
            "  • Albert Erik Morocco Amanca\n"
            "  • Jean Franco Castilla\n"
            "  • Erik Quispe\n\n"
            "Cobertura de Avances: 1 al 7 (Entrega 2 Completa)\n"
            "Suite de Pruebas: 58 pruebas automatizadas (100% aprobadas)"
        )
        messagebox.showinfo("Acerca del Proyecto", msg)

    # ------------------------------------------------------------------
    # Exportaciones
    # ------------------------------------------------------------------
    def _save_png(self):
        if self.graph is None:
            return
        path = filedialog.asksaveasfilename(
            title="Guardar imagen",
            defaultextension=".png",
            filetypes=[("Imagen PNG", "*.png")],
            initialfile="vista_vertex_cover.png",
        )
        if not path:
            return
        try:
            self.fig.savefig(path, dpi=150, bbox_inches="tight")
            self._set_status(f"Imagen guardada en {path}")
        except Exception as exc:
            messagebox.showerror("Error al guardar", str(exc))

    def _save_json(self):
        if self.graph is None:
            return
        path = filedialog.asksaveasfilename(
            title="Exportar instancia JSON",
            defaultextension=".json",
            filetypes=[("Instancia JSON", "*.json")],
            initialfile="instancia.json",
        )
        if not path:
            return
        try:
            self.graph.save_json(path, name=Path(path).stem, description=self.instance_name)
            self._set_status(f"Instancia guardada en {path}")
        except Exception as exc:
            messagebox.showerror("Error al guardar", str(exc))

    def _export_metrics(self):
        if not self.results:
            messagebox.showwarning("Sin metricas", "Primero ejecuta los algoritmos.")
            return
        path = filedialog.asksaveasfilename(
            title="Exportar reporte de metricas",
            defaultextension=".txt",
            filetypes=[("Archivo de Texto", "*.txt"), ("CSV", "*.csv")],
            initialfile="metricas_ejecucion.txt",
        )
        if not path:
            return
        try:
            Path(path).write_text(self.stats.get("1.0", "end"), encoding="utf-8")
            self._set_status(f"Metricas exportadas a {path}")
        except Exception as exc:
            messagebox.showerror("Error al exportar", str(exc))


def main():
    root = tk.Tk()
    VertexCoverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
