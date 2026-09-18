import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageTk

from src.semana02_entrenamiento import load_model, predict_single
from src.semana03_taxonomia import classify_class
from src.semana04_busqueda import ESTADO_INICIAL, H, TRATAMIENTOS, diagnose_recovery
from src.semana05_sistema_hibrido import answer as hybrid_answer

PREVIEW_W = 340
PREVIEW_H = 340

FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

CONSULTAS_POR_CATEGORIA = {
    "Enfermedades fungicas": "La planta presenta manchas amarillas y signos de hongos en las hojas.",
    "Enfermedades bacterianas": "La planta tiene manchas acuosas con halo amarillo y exudados.",
    "Enfermedades virales": "Las hojas muestran patron de mosaico y amarillamiento.",
    "Plagas": "Veo insectos o acaros en las hojas de mi planta.",
    "Plantas sanas": "Mi planta esta sana, con hojas verdes y sin manchas.",
    "Sin clasificar": "La planta presenta manchas amarillas en las hojas.",
}

# ---------------------------------------------------------------------------
# Paleta de colores
# ---------------------------------------------------------------------------
COLOR_BG = "#f4f6f5"          # fondo general
COLOR_CARD = "#ffffff"        # fondo de tarjetas
COLOR_PRIMARY = "#2e7d32"     # verde principal
COLOR_PRIMARY_DARK = "#1b5e20"
COLOR_PRIMARY_LIGHT = "#e8f5e9"
COLOR_ACCENT = "#ef6c00"      # advertencia / enfermedad
COLOR_DANGER = "#c62828"      # error
COLOR_TEXT = "#1f2a1f"
COLOR_TEXT_MUTED = "#6b7a6b"
COLOR_BORDER = "#dfe6df"


class RoundedCard(tk.Frame):
    """Tarjeta simple con borde sutil para simular elevación."""

    def __init__(self, parent, **kwargs):
        outer = kwargs.pop("padding", 16)
        super().__init__(parent, bg=COLOR_BORDER)
        self.inner = tk.Frame(self, bg=COLOR_CARD)
        self.inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.body = tk.Frame(self.inner, bg=COLOR_CARD, padx=outer, pady=outer)
        self.body.pack(fill="both", expand=True)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PlantAI · Detección de enfermedades en plantas")
        self.geometry("1000x760")
        self.minsize(880, 640)
        self.configure(bg=COLOR_BG)

        self.image_path = None
        self._preview_img = None
        self.model = None
        self.class_map = None

        self._setup_styles()
        self._build_ui()

        self._set_status("Cargando modelo…", COLOR_TEXT_MUTED)
        self.after(150, self._load_model)

    # ------------------------------------------------------------------
    # Estilos
    # ------------------------------------------------------------------
    def _setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Primary.TButton",
            background=COLOR_PRIMARY,
            foreground="white",
            font=(FONT_FAMILY, 11, "bold"),
            padding=(18, 10),
            borderwidth=0,
            focusthickness=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", COLOR_PRIMARY_DARK), ("disabled", "#a5b8a5")],
            foreground=[("disabled", "#e6ece6")],
        )

        style.configure(
            "Secondary.TButton",
            background="#ffffff",
            foreground=COLOR_PRIMARY_DARK,
            font=(FONT_FAMILY, 10, "bold"),
            padding=(14, 9),
            borderwidth=1,
            relief="solid",
        )
        style.map(
            "Secondary.TButton",
            background=[("active", COLOR_PRIMARY_LIGHT)],
            bordercolor=[("!disabled", COLOR_PRIMARY)],
        )

        style.configure(
            "Plant.Horizontal.TProgressbar",
            troughcolor=COLOR_PRIMARY_LIGHT,
            background=COLOR_PRIMARY,
            bordercolor=COLOR_PRIMARY_LIGHT,
            lightcolor=COLOR_PRIMARY,
            darkcolor=COLOR_PRIMARY,
            thickness=6,
        )

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        # ---------- Encabezado ----------
        header = tk.Frame(self, bg=COLOR_PRIMARY, height=78)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title_box = tk.Frame(header, bg=COLOR_PRIMARY)
        title_box.pack(side="left", padx=24, fill="y")
        tk.Label(
            title_box, text="🌿 PlantAI", bg=COLOR_PRIMARY, fg="white",
            font=(FONT_FAMILY, 20, "bold"), anchor="w",
        ).pack(anchor="w", pady=(14, 0))
        tk.Label(
            title_box, text="Detección de enfermedades en plantas con IA",
            bg=COLOR_PRIMARY, fg=COLOR_PRIMARY_LIGHT, font=(FONT_FAMILY, 10),
        ).pack(anchor="w")

        self.model_badge = tk.Label(
            header, text="●  Cargando modelo…", bg=COLOR_PRIMARY, fg="#ffe082",
            font=(FONT_FAMILY, 9, "bold"),
        )
        self.model_badge.pack(side="right", padx=24)

        # ---------- Cuerpo ----------
        body = tk.Frame(self, bg=COLOR_BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # ----- Columna izquierda: imagen -----
        left_card = RoundedCard(body, padding=16)
        left_card.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        tk.Label(
            left_card.body, text="Imagen de la planta", bg=COLOR_CARD, fg=COLOR_TEXT,
            font=(FONT_FAMILY, 12, "bold"),
        ).pack(anchor="w")

        self.preview_frame = tk.Frame(
            left_card.body, bg="#eef2ee", width=PREVIEW_W, height=PREVIEW_H,
            highlightbackground=COLOR_BORDER, highlightthickness=1,
        )
        self.preview_frame.pack(pady=(12, 12))
        self.preview_frame.pack_propagate(False)

        self.preview_label = tk.Label(
            self.preview_frame, text="Sin imagen\nseleccionada", bg="#eef2ee",
            fg=COLOR_TEXT_MUTED, font=(FONT_FAMILY, 11), justify="center",
        )
        self.preview_label.pack(expand=True)

        self.file_label = tk.Label(
            left_card.body, text="Ningún archivo seleccionado", bg=COLOR_CARD,
            fg=COLOR_TEXT_MUTED, font=(FONT_FAMILY, 8), wraplength=PREVIEW_W, justify="left",
        )
        self.file_label.pack(anchor="w", pady=(0, 14))

        ttk.Button(
            left_card.body, text="📁  Seleccionar imagen", style="Secondary.TButton",
            command=self._select_image,
        ).pack(fill="x", pady=(0, 8))

        self.diagnose_btn = ttk.Button(
            left_card.body, text="🔍  Diagnosticar", style="Primary.TButton",
            command=self._on_diagnose,
        )
        self.diagnose_btn.pack(fill="x")

        self.progress = ttk.Progressbar(
            left_card.body, mode="indeterminate", style="Plant.Horizontal.TProgressbar",
        )

        # ----- Columna derecha: resultados -----
        right_card = RoundedCard(body, padding=0)
        right_card.grid(row=0, column=1, sticky="nsew")
        right_card.body.pack_configure(padx=0, pady=0)

        results_header = tk.Frame(right_card.body, bg=COLOR_CARD, padx=18, pady=14)
        results_header.pack(fill="x")
        tk.Label(
            results_header, text="Resultados del diagnóstico", bg=COLOR_CARD, fg=COLOR_TEXT,
            font=(FONT_FAMILY, 12, "bold"),
        ).pack(anchor="w")
        tk.Frame(right_card.body, bg=COLOR_BORDER, height=1).pack(fill="x")

        # ----- Asistente textual (semana 05): consulta en lenguaje natural -----
        ttk.Separator(right_card.body, orient="horizontal").pack(fill="x")

        assistant = tk.Frame(right_card.body, bg=COLOR_CARD, padx=18, pady=12)
        assistant.pack(fill="x", side="bottom")

        row = tk.Frame(assistant, bg=COLOR_CARD)
        row.pack(fill="x")

        tk.Label(
            row, text="🧪  Síntomas visibles:",
            bg=COLOR_CARD, fg=COLOR_TEXT, font=(FONT_FAMILY, 10, "bold"),
        ).pack(side="left", padx=(0, 8))

        self.consulta_entry = ttk.Entry(row, font=(FONT_FAMILY, 10))
        self.consulta_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.consulta_entry.bind("<Return>", lambda e: self._on_diagnose())

        tk.Label(
            assistant, text="Los síntomas visibles se usan al presionar \"Diagnosticar\": "
                            "el sistema extrae las palabras clave.",
            bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, font=(FONT_FAMILY, 9),
            anchor="w", justify="left",
        ).pack(anchor="w", pady=(8, 0))

        text_frame = tk.Frame(right_card.body, bg=COLOR_CARD, padx=18, pady=14)
        text_frame.pack(fill="both", expand=True)

        self.results_text = tk.Text(
            text_frame, wrap="word", font=(FONT_FAMILY, 10), state="disabled",
            bg=COLOR_CARD, fg=COLOR_TEXT, relief="flat", bd=0, padx=4, pady=4,
        )
        scroll = ttk.Scrollbar(text_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.results_text.pack(side="left", fill="both", expand=True)

        self._configure_text_tags()
        self._show_placeholder()

        # ---------- Barra de estado ----------
        status_bar = tk.Frame(self, bg="#eef2ee", height=30)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        self.status_label = tk.Label(
            status_bar, text="", bg="#eef2ee", fg=COLOR_TEXT_MUTED,
            font=(FONT_FAMILY, 9), anchor="w", padx=16,
        )
        self.status_label.pack(side="left", fill="y")

    def _configure_text_tags(self):
        t = self.results_text
        t.tag_configure("h1", font=(FONT_FAMILY, 13, "bold"), foreground=COLOR_PRIMARY_DARK,
                         spacing1=10, spacing3=6)
        t.tag_configure("h2", font=(FONT_FAMILY, 11, "bold"), foreground=COLOR_PRIMARY,
                         spacing1=14, spacing3=4)
        t.tag_configure("label", font=(FONT_FAMILY, 10, "bold"), foreground=COLOR_TEXT)
        t.tag_configure("value", font=(FONT_FAMILY, 10), foreground=COLOR_TEXT)
        t.tag_configure("muted", font=(FONT_FAMILY, 9), foreground=COLOR_TEXT_MUTED)
        t.tag_configure("mono", font=(FONT_MONO, 9), foreground=COLOR_TEXT)
        t.tag_configure("healthy", font=(FONT_FAMILY, 11, "bold"), foreground=COLOR_PRIMARY_DARK)
        t.tag_configure("warning", font=(FONT_FAMILY, 10, "bold"), foreground=COLOR_ACCENT)
        t.tag_configure("danger", font=(FONT_FAMILY, 10, "bold"), foreground=COLOR_DANGER)
        t.tag_configure("step", font=(FONT_FAMILY, 10), foreground=COLOR_TEXT, lmargin1=16, lmargin2=16)
        t.tag_configure("divider", foreground=COLOR_BORDER)

    def _show_placeholder(self):
        self._clear_results()
        t = self.results_text
        t.config(state="normal")
        t.insert("end", "👋  Selecciona una imagen y/o escribe una consulta, luego presiona ", "muted")
        t.insert("end", "Diagnosticar", "label")
        t.insert("end", " para ver el análisis completo aquí.\n\n", "muted")
        t.insert("end", "💡  Sin foto también obtienes una solución: el sistema híbrido ", "muted")
        t.insert("end", "analiza el texto por palabras clave y reglas", "value")
        t.insert("end", " y sugiere el tratamiento + la ruta A*.", "muted")
        t.config(state="disabled")

    # ------------------------------------------------------------------
    # Carga del modelo
    # ------------------------------------------------------------------
    def _load_model(self):
        try:
            self.model, self.class_map = load_model()
            self._set_status("Modelo cargado correctamente. Selecciona una imagen para comenzar.", COLOR_PRIMARY_DARK)
            self.model_badge.config(text="●  Modelo listo", fg="#c8e6c9")
        except Exception as e:
            self._set_status(f"Error cargando el modelo: {e}", COLOR_DANGER)
            self.model_badge.config(text="●  Error al cargar modelo", fg="#ffab91")

    # ------------------------------------------------------------------
    # Selección de imagen
    # ------------------------------------------------------------------
    def _select_image(self):
        path = filedialog.askopenfilename(
            title="Selecciona una foto de tu planta",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp")],
        )
        if not path:
            return
        self.image_path = path
        short_name = path.replace("\\", "/").split("/")[-1]
        self.file_label.config(text=short_name)
        self._show_preview(path)
        self.diagnose_btn.config(state="normal")
        self._show_placeholder()
        self._set_status("Imagen cargada. Lista para diagnosticar.", COLOR_TEXT_MUTED)

    def _show_preview(self, path):
        try:
            img = Image.open(path)
            img = img.convert("RGB")
            img.thumbnail((PREVIEW_W - 8, PREVIEW_H - 8), Image.LANCZOS)
            self._preview_img = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self._preview_img, text="", bg=COLOR_CARD)
            self.preview_frame.config(bg=COLOR_CARD)
        except Exception as e:
            self.preview_label.config(image="", text=f"Error al leer\nla imagen", bg="#eef2ee")
            self._set_status(f"Error al leer la imagen: {e}", COLOR_DANGER)

    # ------------------------------------------------------------------
    # Utilidades de texto / estado
    # ------------------------------------------------------------------
    def _set_status(self, text, color=COLOR_TEXT_MUTED):
        self.status_label.config(text=text, fg=color)

    def _clear_results(self):
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.config(state="disabled")

    def _insert(self, text, tag=None):
        self.results_text.config(state="normal")
        if tag:
            self.results_text.insert("end", text, tag)
        else:
            self.results_text.insert("end", text)
        self.results_text.config(state="disabled")
        self.results_text.see("end")

    def _divider(self):
        self._insert("─" * 56 + "\n", "divider")

    # ------------------------------------------------------------------
    # Diagnóstico (en hilo aparte para no congelar la UI)
    # ------------------------------------------------------------------
    def _on_diagnose(self):
        texto = self.consulta_entry.get().strip()

        if not self.image_path and not texto:
            messagebox.showwarning(
                "Sin información",
                "Selecciona una imagen y/o escribe una consulta en lenguaje natural "
                "para obtener una solución.",
            )
            return

        if not self.image_path:
            self._run_text_solution(texto)
            return

        if self.model is None:
            if texto:
                self._run_text_solution(texto)
            else:
                messagebox.showwarning(
                    "Modelo no disponible", "El modelo no se cargó correctamente."
                )
            return

        self._clear_results()
        self.diagnose_btn.config(state="disabled")
        self.progress.pack(fill="x", pady=(10, 0))
        self.progress.start(12)
        self._set_status("Diagnosticando…", COLOR_PRIMARY_DARK)

        thread = threading.Thread(target=self._run_diagnosis, args=(self.image_path,), daemon=True)
        thread.start()

    def _run_text_solution(self, texto):
        self._clear_results()
        self._set_status("Analizando consulta y proponiendo solución (sin imagen)…", COLOR_PRIMARY_DARK)
        try:
            data = hybrid_answer(texto)
            self._render_text_solution(data)
            self._set_status("Solución sugerida lista.", COLOR_PRIMARY_DARK)
        except Exception as e:
            self._insert("⚠  Ocurrió un error al analizar la consulta\n\n", "danger")
            self._insert(str(e) + "\n", "value")
            self._set_status("No pudo completarse el análisis.", COLOR_DANGER)

    def _run_diagnosis(self, image_path):
        try:
            data = self._analyze(image_path)
            self.after(0, lambda: self._on_diagnosis_success(data))
        except Exception as e:
            self.after(0, lambda: self._on_diagnosis_error(e))

    def _on_diagnosis_success(self, data):
        self.progress.stop()
        self.progress.pack_forget()
        self.diagnose_btn.config(state="normal")
        self._render_report(data)
        self._set_status("Diagnóstico completado.", COLOR_PRIMARY_DARK)

    def _on_diagnosis_error(self, error):
        self.progress.stop()
        self.progress.pack_forget()
        self.diagnose_btn.config(state="normal")
        self._insert("⚠  Ocurrió un error durante el diagnóstico\n\n", "danger")
        self._insert(str(error) + "\n", "value")
        self._set_status("El diagnóstico no pudo completarse.", COLOR_DANGER)
        messagebox.showerror("Error", str(error))

    # ------------------------------------------------------------------
    # Lógica de análisis (idéntica a la original, solo reestructurada)
    # ------------------------------------------------------------------
    def _analyze(self, image_path):
        with Image.open(image_path) as img:
            w, h = img.size

        class_pred, confidence = predict_single(self.model, self.class_map, image_path)
        category = classify_class(class_pred)
        plan, total, expanded, cat = diagnose_recovery(class_pred)

        consulta = self.consulta_entry.get().strip()
        if not consulta:
            consulta = CONSULTAS_POR_CATEGORIA.get(cat, CONSULTAS_POR_CATEGORIA["Sin clasificar"])

        return {
            "size": (w, h),
            "class_pred": class_pred,
            "confidence": confidence,
            "category": category,
            "plan": plan,
            "total": total,
            "expanded": expanded,
            "cat": cat,
            "consulta": consulta,
            "hibrido": hybrid_answer(consulta),
        }

    def _route_string(self, plan):
        recorrido = "inicio"
        for origen, accion, step, nxt in plan:
            recorrido += f" → {accion} (+{step}) → {nxt}"
        return recorrido

    # ------------------------------------------------------------------
    # Render del reporte enriquecido
    # ------------------------------------------------------------------
    def _render_report(self, data):
        self._clear_results()

        is_healthy = data["cat"] == "Plantas sanas"

        # --- Encabezado con veredicto ---
        icon = "✅" if is_healthy else "🩺"
        tag = "healthy" if is_healthy else "warning"
        self._insert(f"{icon}  ", None)
        self._insert(f"{data['class_pred']}\n", tag)
        self._insert(f"Confianza del modelo: {data['confidence']:.1%}\n\n", "muted")

        # --- Paso 1 ---
        self._insert("1. Preprocesamiento de imagen\n", "h2")
        w, h = data["size"]
        self._insert(f"   Tamaño original:  {w}×{h} px (RGB)\n", "step")
        self._insert("   Redimensionado:   64×64 → 12,288 características\n", "step")

        # --- Paso 2 ---
        self._insert("\n2. Clasificación\n", "h2")
        self._insert("   Modelo:      ", "step")
        self._insert("StandardScaler + LogisticRegression\n", "value")
        self._insert("   Clase:       ", "step")
        self._insert(f"{data['class_pred']}\n", "label")
        self._insert("   Confianza:   ", "step")
        self._insert(f"{data['confidence']:.1%}\n", "label")

        # --- Paso 3 ---
        self._insert("\n3. Taxonomía\n", "h2")
        self._insert("   Categoría:   ", "step")
        self._insert(f"{data['category']}\n", "label")

        # --- Paso 4 ---
        self._insert("\n4. Plan de recuperación\n", "h2")

        if is_healthy:
            self._insert("   🌱  La planta está sana. No se requiere tratamiento.\n", "healthy")
        else:
            cat = data["cat"]
            grafo = TRATAMIENTOS.get(cat, TRATAMIENTOS["Sin clasificar"])

            self._insert(f"   Grafo de tratamientos ({cat})\n", "label")
            for estado, acciones in grafo.items():
                for accion, nxt, step in acciones:
                    self._insert(
                        f"     {estado:<20s} —{accion}→  {nxt}   (+{step})\n", "mono"
                    )

            self._insert("\n   Recorrido A*\n", "label")
            plan = data["plan"]
            if plan:
                recorrido = "     inicio"
                for origen, accion, step, nxt in plan:
                    recorrido += f" → {accion} (+{step}) → {nxt}"
                self._insert(recorrido + "\n", "mono")

            if plan is None:
                self._insert("\n   ⚠  Meta inalcanzable: no hay cura para enfermedades virales.\n", "danger")
                self._insert("   Plan disponible: solo contención y manejo.\n", "value")
            else:
                self._insert(
                    f"\n   Costo total: {data['total']}    Nodos expandidos: {data['expanded']}\n\n",
                    "muted",
                )
                for i, (origen, accion, step, nxt) in enumerate(plan, start=1):
                    self._insert(f"   {i}. ", "label")
                    self._insert(f"{accion}", "value")
                    self._insert(f"   (+{step})\n", "muted")

        # --- Recorrido y búsqueda de rutas (integración del análisis textual) ---
        hib = data["hibrido"]
        self._insert("\n   Recorrido y búsqueda de rutas (A*)\n", "label")
        self._insert("   Describción de sintomas: ", "step")
        self._insert(f"\"{data['consulta']}\"\n", "value")
        self._insert("   Palabras clave extraídas:    ", "step")
        self._insert((", ".join(hib["palabras_clave"]) or "ninguna") + "\n", "value")
        self._insert("   Reglas activadas: ", "step")
        self._insert((", ".join(hib["reglas"]) or "ninguna") + "\n", "value")

        self._insert("\n   Búsqueda y cálculo de rutas:\n", "step")
        if is_healthy:
            self._insert(
                "     Meta 'healthy' ya alcanzada: no hay ruta que calcular (plan vacío).\n",
                "muted",
            )
        elif plan:
            inicio = ESTADO_INICIAL
            g_acum = 0
            self._insert(f"     {inicio:<22s} g=0  h={H[inicio]}  f={H[inicio]}\n", "mono")
            for origen, accion, step, nxt in plan:
                g_acum += step
                self._insert(
                    f"     --{accion} (+{step})--> {nxt:<18s} g={g_acum}  h={H[nxt]}  "
                    f"f={g_acum + H[nxt]}\n",
                    "mono",
                )
            self._insert(
                f"     Costo total: {data['total']}   Nodos expandidos: {data['expanded']}\n",
                "muted",
            )
        else:
            self._insert(
                "     Meta 'healthy' inalcanzable (caso viral): solo contención y manejo.\n",
                "danger",
            )

    def _render_text_solution(self, d):
        self._clear_results()

        self._insert("🤖  Sistema híbrido · solución sin imagen\n", "h1")
        self._insert(f'Consulta: "{d["consulta"]}"\n\n', "value")

        self._insert("1. Palabras clave extraídas\n", "h2")
        if d["palabras_clave"]:
            for term in d["palabras_clave"]:
                self._insert(f"   • {term}\n", "step")
        else:
            self._insert("   Ninguna palabra clave del dominio detectada.\n", "muted")

        self._insert("\n2. Reglas activadas\n", "h2")
        self._insert("   " + (", ".join(d["reglas"]) or "ninguna") + "\n", "label")
        self._insert("   Categoría: " + (d["categoria"] or "sin clasificar") + "\n", "value")

        self._insert("\n3. ¿Aplica el algoritmo A*?\n", "h2")
        if d["aplica_astar"]:
            self._insert("✅  SÍ aplica para búsqueda/cálculo de rutas o caminos\n", "healthy")
        else:
            self._insert("❌  No aplica\n", "warning")
        self._insert("   " + " ".join(d["razones"]) + "\n", "muted")

        self._insert("\n4. Solución sugerida\n", "h2")
        self._insert("   " + d["solucion"] + "\n", "value")

        if d["ruta"]:
            self._insert("\n5. Ruta A* calculada (recorrido de tratamientos)\n", "h2")
            ruta = d["ruta"]
            if ruta["plan"] is None:
                self._insert(
                    "   ⚠  Meta 'healthy' inalcanzable: solo existe plan de contención.\n",
                    "danger",
                )
            else:
                inicio = ESTADO_INICIAL
                g_acum = 0
                self._insert(f"   {inicio:<22s} g=0  h={H[inicio]}  f={H[inicio]}\n", "mono")
                for origen, accion, step, nxt in ruta["plan"]:
                    g_acum += step
                    self._insert(
                        f"   --{accion} (+{step})--> {nxt:<18s} g={g_acum}  h={H[nxt]}  "
                        f"f={g_acum + H[nxt]}\n",
                        "mono",
                    )
                self._insert(
                    f"   Costo total: {ruta['total']}   Nodos expandidos: {ruta['expanded']}\n",
                    "muted",
                )
        elif d["categoria"] == "Plantas sanas":
            self._insert("\n5. Ruta A*\n", "h2")
            self._insert("   Meta ya alcanzada: no hay recorrido que calcular (plan vacío).\n", "muted")

        self._insert("\nCasos de uso de A* (rutas/caminos)\n", "h2")
        if d["casos"]:
            for caso in d["casos"]:
                self._insert(f"   • {caso['titulo']}\n", "label")
                self._insert(f"       {caso['detalle']}\n", "step")
        else:
            self._insert("   Sin casos determinados.\n", "muted")

        self._insert("\nExplicación\n", "h2")
        self._insert(d["explicacion"] + "\n", "value")
        self._divider()
        self._insert("Análisis completado ✔\n", "muted")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()