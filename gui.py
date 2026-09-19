"""
PlantAI - Interfaz grafica de diagnostico de enfermedades en plantas.
Conecta los modulos src/semana02..semana07 (clasificacion, taxonomia,
A*, sistema hibrido y automata de validacion).
Stack: Python 3.11 · tkinter / ttk unicamente.
Ejecutar:  python gui.py
"""

import sys
import os

# Permitir importar src/ aunque el script se ejecute desde una subcarpeta
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
while (not os.path.isdir(os.path.join(_PROJECT_ROOT, "src"))
       and os.path.dirname(_PROJECT_ROOT) != _PROJECT_ROOT):
    _PROJECT_ROOT = os.path.dirname(_PROJECT_ROOT)
sys.path.insert(0, _PROJECT_ROOT)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading

# --- Importaciones del pipeline ---
try:
    from src.semana02_entrenamiento import load_model, predict_single, preprocess_single_image
    from src.semana03_taxonomia import classify_class
    from src.semana04_busqueda import diagnose_recovery
    from src.semana05_sistema_hibrido import answer
    from src.semana07_representaciones import (
        validar_secuencia, extraer_vector_hoja, distancia_hoja_sana)
    _PIPELINE_OK = True
except ImportError:
    _PIPELINE_OK = False

# --- Paleta ---
C = {
    "bg_app":     "#0f1f10",   # canvas global
    "bg_sidebar": "#152416",   # sidebar izquierdo
    "bg_card":    "#1c3020",   # tarjetas / paneles
    "bg_main":    "#f5f7f5",   # area de contenido
    "bg_input":   "#eef2ee",   # inputs
    "bg_header":  "#ffffff",   # cabecera de seccion

    "primary":    "#2e7d32",
    "primary_dk": "#1b5e20",
    "primary_lt": "#66bb6a",
    "leaf":       "#43a047",

    "accent":     "#ef6c00",
    "accent_lt":  "#ffcc80",

    "fg_light":   "#f0f4f0",
    "fg_muted":   "#9ab09b",
    "fg_dark":    "#1a2e1b",
    "fg_mid":     "#4a6741",

    "success":    "#388e3c",
    "warning":    "#f57f17",
    "danger":     "#c62828",
    "info":       "#0277bd",

    "border":     "#d8e8d8",
    "divider":    "#263c28",
}

FONT = {
    "display":  ("Segoe UI", 18, "bold"),
    "h1":       ("Segoe UI", 15, "bold"),
    "h2":       ("Segoe UI", 12, "bold"),
    "body":     ("Segoe UI", 10),
    "body_med": ("Segoe UI", 10, "bold"),
    "caption":  ("Segoe UI", 8),
    "mono":     ("Consolas", 9),
    "mono_sm":  ("Consolas", 8),
    "brand":    ("Segoe UI", 16, "bold"),
}


# --- Helpers de widgets personalizados ---

def _darken(hex_color: str) -> str:
    """Oscurece un color hex ~15 %."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = max(0, int(r*0.85)), max(0, int(g*0.85)), max(0, int(b*0.85))
    return f"#{r:02x}{g:02x}{b:02x}"


def _make_pill_button(parent, text, command, bg=None, fg=None,
                      padx=20, pady=8, font=None):
    """Botón con efecto hover, sin borde visible."""
    _bg   = bg   or C["primary"]
    _fg   = fg   or C["fg_light"]
    _font = font or FONT["body_med"]

    btn = tk.Label(
        parent, text=text, font=_font,
        bg=_bg, fg=_fg, cursor="hand2",
        padx=padx, pady=pady,
    )

    def _enter(_):
        btn.config(bg=C["primary_dk"] if bg is None else _darken(bg))

    def _leave(_):
        btn.config(bg=_bg)

    def _click(_):
        command()

    btn.bind("<Enter>", _enter)
    btn.bind("<Leave>", _leave)
    btn.bind("<Button-1>", _click)
    return btn


def _sep(parent, color=None, height=1, padx=0, pady=4):
    """Separador horizontal delgado."""
    f = tk.Frame(parent, bg=color or C["border"], height=height)
    f.pack(fill="x", padx=padx, pady=pady)
    return f


def _tag_chip(parent, text, bg, fg="#fff"):
    """Etiqueta tipo chip/badge."""
    return tk.Label(parent, text=text, font=FONT["caption"],
                    bg=bg, fg=fg, padx=6, pady=2)


# --- Aplicacion principal ---

class App(tk.Tk):
    # --- Init ---
    def __init__(self):
        super().__init__()
        self.title("PlantAI — Detección de Enfermedades")
        self.geometry("1100x720")
        self.minsize(900, 620)
        self.configure(bg=C["bg_app"])

        self._img_path = None
        self._photo_ref = None
        self._thumb_ref = None
        self._model = None
        self._class_map = None
        self._busy = False

        self._load_pipeline()
        self._build_ui()
        self._status("Listo — selecciona una imagen o escribe síntomas.", "info")

    # --- Pipeline ---
    def _load_pipeline(self):
        if _PIPELINE_OK:
            try:
                self._model, self._class_map = load_model()
            except Exception as exc:
                messagebox.showwarning("Pipeline", f"Error al cargar modelo:\n{exc}")

    # --- Construccion de la UI ---
    def _build_ui(self):
        root_pane = tk.PanedWindow(
            self, orient="horizontal",
            bg=C["bg_app"], sashwidth=0, bd=0,
        )
        root_pane.pack(fill="both", expand=True)

        self._build_sidebar(root_pane)
        self._build_main(root_pane)

    # --- Sidebar ---
    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=C["bg_sidebar"], width=210)
        sb.pack_propagate(False)
        parent.add(sb, minsize=210)

        logo_f = tk.Frame(sb, bg=C["bg_sidebar"])
        logo_f.pack(fill="x", padx=20, pady=(28, 6))

        tk.Label(logo_f, text="🌿", font=("Segoe UI Emoji", 26),
                 bg=C["bg_sidebar"], fg=C["primary_lt"]).pack(anchor="w")
        tk.Label(logo_f, text="PlantAI", font=FONT["brand"],
                 bg=C["bg_sidebar"], fg=C["fg_light"]).pack(anchor="w")
        tk.Label(logo_f, text="Diagnóstico Inteligente",
                 font=FONT["caption"], bg=C["bg_sidebar"],
                 fg=C["fg_muted"]).pack(anchor="w")

        _sep(sb, C["divider"], padx=16, pady=8)

        self._build_sidebar_section(sb, "IMAGEN", [
            ("📁  Seleccionar foto", self._select_image),
            ("🔬  Diagnosticar",     self._on_diagnose),
        ])

        _sep(sb, C["divider"], padx=16, pady=8)

        self._build_sidebar_section(sb, "HERRAMIENTAS", [
            ("🗑   Limpiar resultado", self._clear_results),
        ])

        tk.Frame(sb, bg=C["bg_sidebar"]).pack(fill="both", expand=True)

        _sep(sb, C["divider"], padx=16, pady=0)
        footer = tk.Frame(sb, bg=C["bg_sidebar"])
        footer.pack(fill="x", padx=20, pady=14)
        tk.Label(footer, text="v1.0 · IA Agrícola",
                 font=FONT["caption"], bg=C["bg_sidebar"],
                 fg=C["fg_muted"]).pack(anchor="w")
        status_dot = "●" if _PIPELINE_OK else "○"
        dot_color = C["success"] if _PIPELINE_OK else C["danger"]
        tk.Label(footer, text=f"{status_dot} Modelo cargado" if _PIPELINE_OK
                 else f"{status_dot} Modelo no disponible",
                 font=FONT["caption"], bg=C["bg_sidebar"],
                 fg=dot_color).pack(anchor="w", pady=(4, 0))

    def _build_sidebar_section(self, parent, title, items):
        tk.Label(parent, text=title, font=("Segoe UI", 7, "bold"),
                 bg=C["bg_sidebar"], fg=C["fg_muted"],
                 padx=20).pack(anchor="w", pady=(6, 2))

        for label, cmd in items:
            btn = tk.Label(
                parent, text=label, font=FONT["body"],
                bg=C["bg_sidebar"], fg=C["fg_light"],
                anchor="w", padx=20, pady=8, cursor="hand2",
            )
            btn.pack(fill="x")

            def _enter(e, b=btn): b.config(bg=C["bg_card"])
            def _leave(e, b=btn): b.config(bg=C["bg_sidebar"])
            def _click(e, c=cmd): c()
            btn.bind("<Enter>", _enter)
            btn.bind("<Leave>", _leave)
            btn.bind("<Button-1>", _click)

    # --- Area principal ---
    def _build_main(self, parent):
        main = tk.Frame(parent, bg=C["bg_main"])
        parent.add(main)

        self._build_page_header(main)

        content = tk.Frame(main, bg=C["bg_main"])
        content.pack(fill="both", expand=True, padx=16, pady=(0, 0))
        content.columnconfigure(0, weight=0, minsize=280)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        self._build_image_panel(content)
        self._build_result_panel(content)

        self._build_text_query(main)
        self._build_status_bar(main)

    def _build_page_header(self, parent):
        hdr = tk.Frame(parent, bg=C["bg_header"],
                       highlightbackground=C["border"],
                       highlightthickness=1)
        hdr.pack(fill="x", padx=0, pady=0)

        inner = tk.Frame(hdr, bg=C["bg_header"])
        inner.pack(fill="x", padx=20, pady=12)

        tk.Label(inner, text="Panel de Diagnóstico", font=FONT["h1"],
                 bg=C["bg_header"], fg=C["fg_dark"]).pack(side="left")

        chips_f = tk.Frame(inner, bg=C["bg_header"])
        chips_f.pack(side="right")
        for label, color in [
            ("Fungal", "#6a1b9a"), ("Bacterial", "#c62828"),
            ("Viral", "#0277bd"),  ("Plaga", "#e65100"),
            ("Sano ✓", "#2e7d32"),
        ]:
            c = _tag_chip(chips_f, label, color)
            c.pack(side="left", padx=3)

    # --- Panel de imagen ---
    def _build_image_panel(self, parent):
        card = tk.Frame(parent, bg=C["bg_header"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)

        card_hdr = tk.Frame(card, bg=C["primary"], height=4)
        card_hdr.pack(fill="x")

        tk.Label(card, text="Vista Previa", font=FONT["h2"],
                 bg=C["bg_header"], fg=C["fg_dark"],
                 padx=14, pady=10).pack(anchor="w")

        _sep(card, C["border"], padx=0, pady=0)

        self._img_canvas = tk.Canvas(
            card, width=260, height=230,
            bg="#e8f0e8", highlightthickness=0,
        )
        self._img_canvas.pack(padx=14, pady=14)
        self._draw_placeholder()

        _sep(card, C["border"], padx=14, pady=2)

        self._img_meta = tk.Label(
            card, text="Sin imagen seleccionada",
            font=FONT["caption"], bg=C["bg_header"],
            fg=C["fg_mid"], wraplength=240, justify="left",
            padx=14, pady=6,
        )
        self._img_meta.pack(anchor="w")

        btn_f = tk.Frame(card, bg=C["bg_header"])
        btn_f.pack(fill="x", padx=14, pady=(4, 14))

        sel_btn = _make_pill_button(btn_f, "Seleccionar imagen",
                                    self._select_image,
                                    bg=C["primary"], padx=14, pady=7)
        sel_btn.pack(side="left", padx=(0, 6))

        run_btn = _make_pill_button(btn_f, "Diagnosticar",
                                    self._on_diagnose,
                                    bg=C["accent"], padx=14, pady=7)
        run_btn.pack(side="left")

    def _draw_placeholder(self):
        c = self._img_canvas
        c.delete("all")
        c.create_oval(90, 55, 170, 135, outline=C["primary_lt"],
                      width=2, dash=(6, 3))
        c.create_text(130, 152, text="🌿", font=("Segoe UI Emoji", 28),
                      fill=C["primary_lt"])
        c.create_text(130, 195, text="Arrastra o selecciona\nuna imagen",
                      font=FONT["caption"], fill=C["fg_mid"], justify="center")

    # --- Panel de resultados ---
    def _build_result_panel(self, parent):
        card = tk.Frame(parent, bg=C["bg_header"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.grid(row=0, column=1, sticky="nsew", pady=8)
        card.rowconfigure(1, weight=1)
        card.columnconfigure(0, weight=1)

        tk.Frame(card, bg=C["leaf"], height=4).grid(
            row=0, column=0, sticky="ew")

        text_frame = tk.Frame(card, bg=C["bg_header"])
        text_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self._result_text = tk.Text(
            text_frame,
            font=FONT["body"], bg=C["bg_header"], fg=C["fg_dark"],
            relief="flat", wrap="word",
            padx=18, pady=14,
            state="disabled",
            selectbackground=C["primary_lt"],
            insertbackground=C["fg_dark"],
        )
        self._result_text.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(text_frame, orient="vertical",
                            command=self._result_text.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self._result_text.config(yscrollcommand=vsb.set)

        self._configure_text_tags()
        self._show_welcome()

    def _configure_text_tags(self):
        t = self._result_text

        t.tag_configure("h1", font=("Segoe UI", 15, "bold"),
                        foreground=C["fg_dark"], spacing3=4)
        t.tag_configure("h2", font=("Segoe UI", 11, "bold"),
                        foreground=C["primary"], spacing3=3, spacing1=10)
        t.tag_configure("h3", font=("Segoe UI", 10, "bold"),
                        foreground=C["fg_mid"], spacing3=2)

        t.tag_configure("label", font=("Segoe UI", 9, "bold"),
                        foreground=C["fg_mid"])
        t.tag_configure("value", font=("Segoe UI", 10),
                        foreground=C["fg_dark"])

        t.tag_configure("mono", font=("Consolas", 9),
                        foreground="#37474f",
                        background="#f0f4f0", relief="flat",
                        lmargin1=18, lmargin2=18, spacing1=1, spacing3=1)

        t.tag_configure("healthy", font=("Segoe UI", 10, "bold"),
                        foreground=C["success"])
        t.tag_configure("warning", font=("Segoe UI", 10, "bold"),
                        foreground=C["warning"])
        t.tag_configure("danger", font=("Segoe UI", 10, "bold"),
                        foreground=C["danger"])
        t.tag_configure("info", font=("Segoe UI", 10),
                        foreground=C["info"])
        t.tag_configure("accent", font=("Segoe UI", 10, "bold"),
                        foreground=C["accent"])

        t.tag_configure("hr", font=("Segoe UI", 4),
                        foreground=C["border"],
                        spacing1=6, spacing3=6)

    def _show_welcome(self):
        self._txt_write([
            ("h1",    "Bienvenido a PlantAI\n"),
            ("value", "\nSelecciona una imagen de planta para obtener un diagnóstico "
                      "completo con:\n\n"),
            ("label", "  ■  "), ("value", "Clasificación de enfermedad (38 clases)\n"),
            ("label", "  ■  "), ("value", "Taxonomía de categoría (5 tipos)\n"),
            ("label", "  ■  "), ("value", "Plan de recuperación óptimo (A*)\n"),
            ("label", "  ■  "), ("value", "Validación de secuencia (Autómata)\n\n"),
            ("hr",    "─" * 55 + "\n"),
            ("info",  "También puedes describir síntomas en el campo de texto\n"
                      "inferior para obtener recomendaciones sin imagen.\n"),
        ])

    # --- Query de texto ---
    def _build_text_query(self, parent):
        bar = tk.Frame(parent, bg=C["bg_header"],
                       highlightbackground=C["border"],
                       highlightthickness=1)
        bar.pack(fill="x", padx=16, pady=(0, 8))

        inner = tk.Frame(bar, bg=C["bg_header"])
        inner.pack(fill="x", padx=14, pady=10)

        tk.Label(inner, text="💬  Consultar por síntomas:",
                 font=FONT["body_med"], bg=C["bg_header"],
                 fg=C["fg_dark"]).pack(side="left", padx=(0, 10))

        self._query_var = tk.StringVar()
        entry = tk.Entry(
            inner, textvariable=self._query_var,
            font=FONT["body"], bg=C["bg_input"], fg=C["fg_dark"],
            relief="flat", insertbackground=C["fg_dark"],
        )
        entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))
        entry.bind("<Return>", lambda _: self._render_text_solution())

        send_btn = _make_pill_button(inner, "Consultar",
                                     self._render_text_solution,
                                     bg=C["primary_dk"], padx=16, pady=5)
        send_btn.pack(side="left")

    # --- Status bar ---
    def _build_status_bar(self, parent):
        sb = tk.Frame(parent, bg=C["bg_app"], height=26)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)

        self._status_dot = tk.Label(sb, text="●", font=("Segoe UI", 9),
                                    bg=C["bg_app"], fg=C["success"])
        self._status_dot.pack(side="left", padx=(14, 4), pady=4)

        self._status_label = tk.Label(sb, text="", font=FONT["caption"],
                                      bg=C["bg_app"], fg=C["fg_muted"],
                                      anchor="w")
        self._status_label.pack(side="left", fill="x", expand=True)

        self._busy_lbl = tk.Label(sb, text="", font=FONT["caption"],
                                  bg=C["bg_app"], fg=C["accent"])
        self._busy_lbl.pack(side="right", padx=14)

    def _status(self, msg: str, level: str = "info"):
        colors = {
            "info":    C["info"],
            "success": C["success"],
            "warning": C["warning"],
            "error":   C["danger"],
        }
        self._status_dot.config(fg=colors.get(level, C["info"]))
        self._status_label.config(text=msg)

    # --- Seleccion de imagen ---
    def _select_image(self):
        path = filedialog.askopenfilename(
            title="Seleccionar imagen de planta",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                ("Todos", "*.*"),
            ],
        )
        if not path:
            return

        self._img_path = path
        self._update_image_preview(path)
        name = os.path.basename(path)
        size = os.path.getsize(path) // 1024
        self._img_meta.config(
            text=f"📄 {name}\n📐 {size} KB — listo para diagnosticar"
        )
        self._status(f"Imagen cargada: {name}", "success")
        self._clear_results(silent=True)

    def _update_image_preview(self, path: str):
        try:
            img = Image.open(path)
            img.thumbnail((260, 230), Image.LANCZOS)
            self._thumb_ref = ImageTk.PhotoImage(img)
            c = self._img_canvas
            c.delete("all")
            x = (260 - img.width)  // 2
            y = (230 - img.height) // 2
            c.create_image(x, y, anchor="nw", image=self._thumb_ref)
        except Exception:
            self._draw_placeholder()

    # --- Diagnostico ---
    def _on_diagnose(self):
        if self._busy:
            return
        if not self._img_path:
            messagebox.showinfo("Sin imagen",
                                "Selecciona una imagen antes de diagnosticar.")
            return
        if not _PIPELINE_OK or self._model is None:
            messagebox.showerror("Pipeline",
                                 "El pipeline no está disponible.")
            return

        self._busy = True
        self._busy_lbl.config(text="⏳ Analizando…")
        self._status("Procesando imagen…", "info")
        threading.Thread(target=self._analyze, daemon=True).start()

    def _top_probs(self, image_path, top=3):
        """Devuelve las top-N clases con su probabilidad (como pares)."""
        img = preprocess_single_image(image_path).reshape(1, -1)
        probs = self._model.predict_proba(img)[0]
        idx_to_class = {v: k for k, v in self._class_map.items()}
        names = [idx_to_class.get(int(c), str(c)) for c in self._model.classes_]
        return sorted(zip(names, probs), key=lambda p: p[1], reverse=True)[:top]

    def _analyze(self):
        try:
            class_name, confidence = predict_single(
                self._model, self._class_map, self._img_path)

            category = classify_class(class_name)

            plan, total, expanded, cat = diagnose_recovery(class_name)

            top3 = self._top_probs(self._img_path)

            vector = extraer_vector_hoja(self._img_path)
            distancia = distancia_hoja_sana(vector)

            acciones = [accion for _, accion, _, _ in (plan or [])]
            is_valid, _final, _pasos = validar_secuencia(cat, acciones)

            self.after(0, lambda: self._render_report(
                class_name, confidence, top3,
                category, cat, plan, total, expanded, is_valid,
                vector, distancia))

        except Exception as exc:
            self.after(0, lambda: self._show_error(str(exc)))
        finally:
            self.after(0, self._done_busy)

    def _done_busy(self):
        self._busy = False
        self._busy_lbl.config(text="")

    def _show_error(self, msg: str):
        self._status(f"Error: {msg}", "error")
        self._txt_write([
            ("danger", f"⚠ Error durante el análisis:\n\n"),
            ("mono",   msg + "\n"),
        ])

    # --- Render de reporte ---
    def _render_report(self, class_name, confidence, top3,
                       category, cat, plan, total, expanded, is_valid,
                       vector=None, distancia=None):
        """Genera el reporte estructurado en el panel de resultados."""

        if confidence >= 0.75:
            conf_tag = "healthy"
            conf_sym = "✔"
        elif confidence >= 0.50:
            conf_tag = "warning"
            conf_sym = "⚠"
        else:
            conf_tag = "danger"
            conf_sym = "✘"

        cat_map = {
            "Plantas sanas":            ("healthy", "✿"),
            "Enfermedades fungicas":    ("warning", "🍄"),
            "Enfermedades bacterianas": ("danger",  "🦠"),
            "Enfermedades virales":     ("danger",  "⚡"),
            "Plagas":                   ("warning", "🐛"),
        }
        cat_tag, cat_sym = cat_map.get(cat, ("info", "?"))

        lines = []

        # 1. Clasificacion
        lines += [
            ("h1",    "Resultado del Diagnóstico\n"),
            ("hr",    "─" * 55 + "\n"),

            ("h2",    "§ 1  Clasificación de Enfermedad\n"),
            ("label", "  Clase detectada:   "),
            ("value", f"{class_name}\n"),
            ("label", "  Confianza:         "),
            (conf_tag, f"{conf_sym}  {confidence:.1%}\n"),
        ]

        if top3:
            lines.append(("h3", "\n  Top-3 clases:\n"))
            for i, (cls, prob) in enumerate(top3, 1):
                lines.append(("mono",
                              f"  {i}. {cls:<45} {prob:.1%}\n"))

        # 2. Taxonomia
        lines += [
            ("hr",    "\n" + "─" * 55 + "\n"),
            ("h2",    "§ 2  Categoría Taxonómica\n"),
            ("label", "  Categoría:  "),
            (cat_tag, f"{cat_sym}  {cat}\n"),
        ]

        # 3. Representacion numerica (semana 07)
        lines += [
            ("hr",    "\n" + "─" * 55 + "\n"),
            ("h2",    "§ 3  Representación Numérica de la Hoja (semana 07)\n"),
            ("label", "  Vector (verdor, amarillez, manchas):  "),
            ("mono",  f"{vector}\n" if vector else "no disponible\n"),
            ("label", "  Hoja sana de referencia:              "),
            ("mono",  "[0.85, 0.10, 0.05]\n"),
            ("label", "  Distancia a hoja sana (euclidiana):   "),
        ]
        if distancia is None:
            lines.append(("value", "no disponible\n"))
        else:
            lines.append(("mono", f"{distancia:.3f}\n"))
        lines.append(("info",
                      "  0 = idéntica a la referencia; a mayor valor,\n"
                      "  más alejada de la hoja sana.\n"))

        # 4. Plan A*
        lines += [
            ("hr",    "\n" + "─" * 55 + "\n"),
            ("h2",    "§ 4  Plan de Recuperación (A*)\n"),
        ]
        if cat == "Plantas sanas":
            lines.append(("healthy",
                          "  ✿  Planta sana — no se requiere tratamiento.\n"))
        elif plan is None:
            lines.append(("danger",
                          "  ⚡  Meta inalcanzable (viral): solo contención y manejo.\n"))
        else:
            lines.append(("label",
                          f"  Costo óptimo: {total}    Nodos expandidos: {expanded}\n\n"))
            for idx, (origen, accion, step, nxt) in enumerate(plan, 1):
                lines.append(("mono",
                              f"  {idx:>2}. {accion:<28} (+{step}) → {nxt}\n"))

        # 5. Validacion (Automata)
        lines += [
            ("hr",    "\n" + "─" * 55 + "\n"),
            ("h2",    "§ 5  Validación de Secuencia (Autómata)\n"),
        ]
        if cat == "Plantas sanas":
            lines.append(("healthy",
                          "  ✔  Secuencia vacía válida — la meta ya está alcanzada.\n"))
        elif plan is None:
            lines.append(("danger",
                          "  ✘  Meta inalcanzable: ninguna secuencia llega a 'healthy'.\n"))
        elif is_valid:
            lines.append(("healthy",
                          "  ✔  Secuencia válida — el plan llega a 'healthy'.\n"))
        else:
            lines.append(("danger",
                          "  ✘  Secuencia inválida — el plan no termina en 'healthy'.\n"))

        # 6. Resumen
        lines += [
            ("hr",    "\n" + "─" * 55 + "\n"),
            ("h2",    "§ 6  Resumen Ejecutivo\n"),
            ("label", "  Planta:     "), ("value", f"{class_name}\n"),
            ("label", "  Categoría:  "), (cat_tag, f"{cat}\n"),
            ("label", "  Confianza:  "), (conf_tag, f"{confidence:.1%}\n"),
            ("label", "  Dist. sana: "),
            ("value" if distancia is None else "mono",
             ("n/d\n" if distancia is None else f"{distancia:.3f}\n")),
            ("label", "  DFA:        "),
        ]
        if cat == "Plantas sanas":
            lines.append(("healthy", "Planta sana\n"))
        elif plan is None:
            lines.append(("danger", "Meta inalcanzable\n"))
        elif is_valid:
            lines.append(("healthy", "Protocolo válido\n"))
        else:
            lines.append(("danger",  "Protocolo inválido\n"))

        self._txt_write(lines)
        self._status(
            f"Diagnóstico completo: {class_name} — {confidence:.1%}",
            "success" if confidence >= 0.6 else "warning",
        )

    # --- Consulta de texto ---
    def _render_text_solution(self):
        query = self._query_var.get().strip()
        if not query:
            return
        if not _PIPELINE_OK:
            messagebox.showerror("Pipeline", "Sistema híbrido no disponible.")
            return

        self._status("Consultando sistema híbrido…", "info")
        try:
            response = answer(query)
        except Exception as exc:
            response = {"solucion": f"Error: {exc}"}

        lines = [
            ("h2",    "💬  Consulta por Síntomas\n"),
            ("label", "  Pregunta:  "), ("value", f"{query}\n"),
            ("hr",    "─" * 55 + "\n"),
        ]

        if isinstance(response, dict):
            cat = response.get("categoria")
            ruta = response.get("ruta") if isinstance(response.get("ruta"), dict) else None
            plan = (ruta or {}).get("plan")

            lines += [
                ("label", "  Categoría:  "),
                ("value", f"{cat or 'sin clasificar'}\n"),
                ("label", "  Reglas:     "),
                ("value", ", ".join(response.get("reglas") or []) + "\n"),
                ("hr",    "─" * 55 + "\n"),
                ("value", response.get("solucion", "") + "\n"),
            ]

            if plan:
                lines += [("hr", "─" * 55 + "\n"),
                          ("h2", "  Plan A* sugerido\n")]
                for idx, (origen, accion, step, nxt) in enumerate(plan, 1):
                    lines.append(("mono",
                                  f"  {idx:>2}. {accion:<28} (+{step}) → {nxt}\n"))
                lines.append(("value", f"  Costo óptimo: {ruta.get('total')}\n"))

            if cat:
                acciones = [accion for _, accion, _, _ in (plan or [])]
                _ok, final, _pasos = validar_secuencia(cat, acciones)
                lines += [("hr", "─" * 55 + "\n"),
                          ("h2", "  Validación (Autómata)\n")]
                if cat == "Plantas sanas":
                    lines.append(("healthy",
                                  "  ✔  Planta sana — secuencia vacía válida.\n"))
                elif plan is None:
                    lines.append(("danger",
                                  "  ✘  Meta inalcanzable (viral): solo contención.\n"))
                elif _ok:
                    lines.append(("healthy",
                                  f"  ✔  Secuencia válida — termina en '{final}'.\n"))
                else:
                    lines.append(("danger",
                                  "  ✘  Secuencia inválida.\n"))
        else:
            lines.append(("value", f"{response}\n"))

        self._txt_write(lines)
        self._query_var.set("")
        self._status("Respuesta generada.", "success")

    # --- Helpers de texto ---
    def _txt_write(self, segments):
        """Reemplaza el contenido del widget de resultados."""
        t = self._result_text
        t.config(state="normal")
        t.delete("1.0", "end")
        for tag, text in segments:
            t.insert("end", text, tag)
        t.config(state="disabled")
        t.see("1.0")

    def _clear_results(self, silent: bool = False):
        self._txt_write([("value", "")])
        self._show_welcome()
        if not silent:
            self._status("Resultados limpiados.", "info")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()