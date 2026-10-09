"""
PlantAI - Backend web ligero.

Reemplaza la interfaz tkinter (gui.py) por una API HTTP que sirve index.html
y expone el mismo diagnostico de la interfaz anterior, llamando a las funciones
ya existentes de los modulos src/semanaXX.py SIN modificarlos.

Caso A (imagen):  semana02 + semana03 + semana04 + semana07 + semana08 + semana09
Caso B (texto):   semana05 (sistema hibrido) via answer()

Ejecutar:  python server.py
Abrir:     http://127.0.0.1:5000
"""

import base64
import io
import os
import sys

# Permitir importar src/ y los modulos del proyecto desde cualquier cwd.
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from flask import Flask, jsonify, request, send_from_directory

try:
    import numpy as np
except Exception:  # pragma: no cover - numpy es dependencia base
    np = None

app = Flask(__name__, static_folder=None)

# ---------------------------------------------------------------------------
# Carga perezosa de modulos de logica. Nunca se modifica su contenido: solo se
# importan y se invocan sus funciones tal cual estan definidas.
# ---------------------------------------------------------------------------

_PIPELINE = None
_PIPELINE_ERROR = None

_MODEL = None
_MODEL_ERROR = None

_RED = None
_RED_ERROR = None
_RED_TRIED = False


def pipeline():
    """Importa los modulos de clasificacion/planificacion una sola vez."""
    global _PIPELINE, _PIPELINE_ERROR
    if _PIPELINE is None and _PIPELINE_ERROR is None:
        try:
            from src.semana02_entrenamiento import (
                load_model, predict_single, preprocess_single_image,
            )
            from src.semana03_taxonomia import classify_class
            from src.semana04_busqueda import diagnose_recovery
            from src.semana05_sistema_hibrido import answer
            from src.semana07_representaciones import (
                validar_secuencia, extraer_vector_hoja, distancia_hoja_sana,
                representacion_simbolica,
            )
            import src.semana09_vision as semana09_vision
            import src.semana10_texturas as semana10_texturas

            _PIPELINE = {
                "load_model": load_model,
                "predict_single": predict_single,
                "preprocess_single_image": preprocess_single_image,
                "classify_class": classify_class,
                "diagnose_recovery": diagnose_recovery,
                "answer": answer,
                "validar_secuencia": validar_secuencia,
                "extraer_vector_hoja": extraer_vector_hoja,
                "distancia_hoja_sana": distancia_hoja_sana,
                "representacion_simbolica": representacion_simbolica,
                "semana09_vision": semana09_vision,
                "semana10_texturas": semana10_texturas,
            }
        except Exception as exc:  # pragma: no cover
            _PIPELINE_ERROR = str(exc)
    return _PIPELINE


def modelo():
    """Carga el modelo de la semana 02 (regresion logistica) y su class_map."""
    global _MODEL, _MODEL_ERROR
    if _MODEL is None and _MODEL_ERROR is None:
        p = pipeline()
        if p is None:
            _MODEL_ERROR = _PIPELINE_ERROR or "pipeline no disponible"
        else:
            try:
                _MODEL = p["load_model"]()
            except Exception as exc:
                _MODEL_ERROR = str(exc)
    return _MODEL


def modelo_red():
    """Carga, si existe, la red MLP guardada de la semana 08.

    Devuelve (modelo, error). No reentrena ni recorre el dataset: reutiliza el
    artefacto artifacts/red_hojas.pkl generado por semana08_red_ontologia.py.
    """
    global _RED, _RED_ERROR, _RED_TRIED
    if not _RED_TRIED:
        _RED_TRIED = True
        try:
            from src.config import ARTIFACTS_DIR
            import joblib

            ruta = ARTIFACTS_DIR / "red_hojas.pkl"
            if ruta.exists():
                _RED = joblib.load(ruta)
            else:
                _RED_ERROR = f"no existe {ruta.name}"
        except Exception as exc:
            _RED_ERROR = str(exc)
    return _RED, _RED_ERROR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _b64_png(matriz_rgb=None, matriz_gris=None):
    """Convierte una matriz (RGB o escala de grises) en PNG base64."""
    if np is None or matriz_rgb is None and matriz_gris is None:
        return None
    from PIL import Image

    if matriz_rgb is not None:
        arr = np.asarray(matriz_rgb)
        if arr.dtype != np.uint8:
            if arr.max() <= 1.0:
                arr = (arr * 255.0)
            arr = arr.astype("uint8")
        imagen = Image.fromarray(arr)
    else:
        arr = np.asarray(matriz_gris)
        if arr.dtype != np.uint8:
            arr = (arr.astype("uint8") * 255)
        imagen = Image.fromarray(arr, "L")

    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _top_probs(model, class_map, image_path, top=3):
    """Top-N clases con su probabilidad, igual que hacia la GUI."""
    p = pipeline()
    img = p["preprocess_single_image"](image_path).reshape(1, -1)
    probs = model.predict_proba(img)[0]
    idx_to_class = {v: k for k, v in class_map.items()}
    names = [idx_to_class.get(int(c), str(c)) for c in model.classes_]
    pares = sorted(zip(names, [float(x) for x in probs]),
                   key=lambda par: par[1], reverse=True)[:top]
    return [{"clase": n, "probabilidad": pr} for n, pr in pares]


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(_PROJECT_ROOT, "index.html")


@app.route("/api/health")
def health():
    ok = pipeline() is not None
    red, red_err = modelo_red()
    return jsonify({
        "pipeline": ok,
        "pipeline_error": _PIPELINE_ERROR,
        "modelo_semana02": modelo() is not None,
        "modelo_semana02_error": _MODEL_ERROR,
        "modelo_semana08": red is not None,
        "modelo_semana08_error": red_err,
        "vision": "semana09_vision" in (pipeline() or {}),
        "texturas": _semana10_disponible(),
    })


def _semana10_disponible():
    """Indica si los artefactos de la semana 10 ya se generaron."""
    try:
        from src.config import ARTIFACTS_DIR

        return ((ARTIFACTS_DIR / "semana10_features.npy").exists()
                and (ARTIFACTS_DIR / "semana10_histograma.png").exists())
    except Exception:
        return False


def _resumen_semana10_imagen(resultado):
    """Resume una imagen ya procesada por semana10.analizar_imagen().

    Se usa tanto para la comparacion en vivo (diagnostico) como para los
    artefactos guardados, para no repetir el calculo del resumen del vector.
    """
    vector = np.asarray(resultado["vector"], dtype=float)
    hist_int = np.asarray(resultado["histograma_intensidad"], dtype=float)
    hist_lbp = np.asarray(resultado["histograma_lbp"], dtype=float)
    regiones = resultado["regiones"]
    return {
        "nombre": resultado["nombre"],
        "ruta": resultado.get("ruta", ""),
        "umbral_otsu": float(resultado["umbral_otsu"]),
        "total_regiones": int(resultado["total_regiones"]),
        "cantidad_regiones": int(regiones["cantidad"]),
        "area_media": float(regiones["area_media"]),
        "area_desviacion": float(regiones["area_desviacion"]),
        "dimension": int(vector.size),
        "resumen_vector": {
            "min": float(vector.min()),
            "max": float(vector.max()),
            "media": float(vector.mean()),
            "desviacion": float(vector.std()),
            "primeros": [float(x) for x in vector[:3]],
        },
        "histograma_intensidad_pico": {
            "bin": int(np.argmax(hist_int)),
            "valor": float(hist_int.max()),
        },
        "lbp_no_uniforme": float(hist_lbp[-1]),
    }


def _semana10_comparacion(ruta):
    """Compara la imagen subida con una referencia del proyecto (semana 10).

    Ejecuta el pipeline de la semana 10 sobre la imagen del usuario y sobre la
    hoja sana de referencia, genera la figura comparativa en artifacts/ y
    devuelve el mismo resumen que /api/semana10. Devuelve (payload, error).
    """
    p = pipeline()
    if p is None or "semana10_texturas" not in (p or {}):
        return None, "modulo de semana 10 no disponible"
    if np is None:
        return None, "numpy no disponible"

    from src.config import ARTIFACTS_DIR, ROOT

    s10 = p["semana10_texturas"]
    referencia = getattr(s10, "IMAGEN_REFERENCIA",
                        ROOT / "data" / "imagen_proyecto_2.png")
    if not referencia.exists():
        return None, "falta data/imagen_proyecto_2.png (referencia)"

    try:
        resultados = [
            s10.analizar_imagen(ruta, "Tu imagen"),
            s10.analizar_imagen(referencia, "Referencia · hoja sana"),
        ]
        salida = ARTIFACTS_DIR / "web_semana10_comparacion.png"
        s10.generar_figura(resultados, salida)
        with open(salida, "rb") as fh:
            histograma_b64 = base64.b64encode(fh.read()).decode("ascii")
    except Exception as exc:  # pragma: no cover
        return None, str(exc)

    return {
        "disponible": True,
        "es_diagnostico": True,
        "dimension": int(resultados[0]["dimension"]),
        "area_minima": int(getattr(s10, "AREA_MINIMA", 0)),
        "lbp": {"radius": getattr(s10, "LBP_RADIUS", 0),
                "points": getattr(s10, "LBP_POINTS", 0),
                "method": getattr(s10, "LBP_METHOD", "")},
        "imagenes": [_resumen_semana10_imagen(r) for r in resultados],
        "histograma": histograma_b64,
        "referencia": "data/imagen_proyecto_2.png",
        "figura": "artifacts/web_semana10_comparacion.png",
    }, None


@app.route("/api/semana10")
def semana10():
    """Devuelve los artefactos de la semana 10.

    Reune el codigo fuente del modulo, la figura comparativa, el resumen del
    vector guardado en artifacts/semana10_features.npy y el contenido del
    reporte reports/semana10.md, sin recalcular nada.
    """
    from src.config import ARTIFACTS_DIR, ROOT

    ruta_features = ARTIFACTS_DIR / "semana10_features.npy"
    ruta_hist = ARTIFACTS_DIR / "semana10_histograma.png"
    ruta_codigo = ROOT / "src" / "semana10_texturas.py"
    ruta_reporte = ROOT / "reports" / "semana10.md"

    if np is None:
        return jsonify({"disponible": False, "detalle": "numpy no disponible"})
    if not ruta_features.exists() or not ruta_hist.exists():
        return jsonify({
            "disponible": False,
            "detalle": ("Faltan artifacts/semana10_features.npy o "
                        "artifacts/semana10_histograma.png. Ejecuta: "
                        "python -m src.semana10_texturas"),
        })

    datos = np.load(ruta_features, allow_pickle=True).item()

    imagenes = [
        _resumen_semana10_imagen({
            "nombre": im["nombre"],
            "ruta": im.get("ruta", ""),
            "umbral_otsu": im["umbral_otsu"],
            "total_regiones": im["total_regiones"],
            "regiones": {
                "cantidad": im["cantidad_regiones"],
                "area_media": im["area_media"],
                "area_desviacion": im["area_desviacion"],
            },
            "vector": im["vector"],
            "histograma_intensidad": im["histograma_intensidad"],
            "histograma_lbp": im["histograma_lbp"],
        })
        for im in datos.get("imagenes", [])
    ]

    with open(ruta_hist, "rb") as fh:
        histograma_b64 = base64.b64encode(fh.read()).decode("ascii")

    codigo = ruta_codigo.read_text(encoding="utf-8") if ruta_codigo.exists() else ""
    reporte = ruta_reporte.read_text(encoding="utf-8") if ruta_reporte.exists() else ""

    return jsonify({
        "disponible": True,
        "dimension": int(datos.get("dimension", 0)),
        "area_minima": int(datos.get("area_minima", 0)),
        "lbp": datos.get("lbp", {}),
        "imagenes": imagenes,
        "histograma": histograma_b64,
        "codigo": codigo,
        "reporte": reporte,
        "archivos": {
            "features": "artifacts/semana10_features.npy",
            "histograma": "artifacts/semana10_histograma.png",
            "codigo": "src/semana10_texturas.py",
            "reporte": "reports/semana10.md",
        },
    })


@app.route("/api/diagnostico", methods=["POST"])
def diagnostico():
    """Caso A: diagnostico por imagen.

    Recibe multipart/form-data con 'imagen'. Devuelve un JSON con el resultado
    desglosado por semana, replicando el informe de la GUI anterior.
    """
    p = pipeline()
    if p is None:
        return jsonify({"error": "Pipeline no disponible",
                        "detalle": _PIPELINE_ERROR}), 500

    archivo = request.files.get("imagen")
    if archivo is None or archivo.filename == "":
        return jsonify({"error": "No se recibio ninguna imagen."}), 400

    # Guardado temporal de la subida (la logica trabaja con rutas de archivo).
    import tempfile

    sufijo = os.path.splitext(archivo.filename)[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=sufijo) as tmp:
        archivo.save(tmp.name)
        ruta = tmp.name

    resultado = {"semanas": {}, "archivo": archivo.filename}

    try:
        par = modelo()
        if par is None:
            return jsonify({"error": "Modelo de la semana 02 no disponible",
                            "detalle": _MODEL_ERROR}), 500
        model, class_map = par

        # --- Semana 02: clasificacion de la enfermedad ---------------------
        class_name, confidence = p["predict_single"](model, class_map, ruta)
        top3 = _top_probs(model, class_map, ruta)
        resultado["clase"] = class_name
        resultado["confianza"] = float(confidence)
        resultado["semanas"]["2"] = {
            "titulo": "Semana 02 - Entrenamiento (clasificacion)",
            "clase": class_name,
            "confianza": float(confidence),
            "top3": top3,
            "modelo": "StandardScaler + LogisticRegression",
            "clases_dataset": len(class_map),
        }

        # --- Semana 03: taxonomia ------------------------------------------
        category = p["classify_class"](class_name)
        resultado["categoria"] = category
        resultado["semanas"]["3"] = {
            "titulo": "Semana 03 - Taxonomia",
            "categoria": category,
        }

        # --- Semana 04: plan de recuperacion (A*) --------------------------
        plan, total, expanded, cat = p["diagnose_recovery"](class_name)
        resultado["semanas"]["4"] = {
            "titulo": "Semana 04 - Busqueda A* (plan de recuperacion)",
            "categoria": cat,
            "plan": [
                {"origen": origen, "accion": accion, "costo": step,
                 "siguiente": nxt}
                for (origen, accion, step, nxt) in (plan or [])
            ],
            "costo_total": total,
            "nodos_expandidos": expanded,
            "meta_inalcanzable": plan is None and cat != "Plantas sanas",
            "planta_sana": cat == "Plantas sanas",
        }

        # --- Semana 07: representaciones (numerica + simbolica + automata) -
        vector = p["extraer_vector_hoja"](ruta)
        distancia = p["distancia_hoja_sana"](vector)
        simbolico = p["representacion_simbolica"](cat)
        acciones = [accion for _, accion, _, _ in (plan or [])]
        is_valid, final, pasos = p["validar_secuencia"](cat, acciones)
        resultado["semanas"]["7"] = {
            "titulo": "Semana 07 - Representaciones",
            "vector": list(vector),
            "hoja_sana": [0.85, 0.10, 0.05],
            "distancia": float(distancia),
            "simbolico": {
                "hechos": simbolico["hechos"],
                "reglas": [
                    {"condiciones": sorted(cond), "resultado": res,
                     "aplica": bool(aplica)}
                    for (cond, res, aplica) in simbolico["reglas"]
                ],
                "conclusion": simbolico["conclusion"],
                "significado": simbolico["significado"],
            },
            "automata": {
                "secuencia_valida": bool(is_valid),
                "estado_final": final,
                "pasos": pasos,
            },
        }

        # --- Semana 08: red neuronal MLP + evidencia + ontologia -----------
        red, red_err = modelo_red()
        if red is not None:
            from PIL import Image

            dimensiones = getattr(red, "n_features_in_", 2304)
            lado = int(round(dimensiones ** 0.5))
            with Image.open(ruta) as im:
                pixeles = (np.asarray(im.convert("L").resize((lado, lado)),
                                      dtype=np.float32).ravel() / 255.0)
            pred = int(red.predict(pixeles.reshape(1, -1))[0])
            probs = red.predict_proba(pixeles.reshape(1, -1))[0]
            conf_red = float(probs[pred])

            # Nombres de clase: orden de carpetas de RAW_DIR, igual que la S8.
            # Si el dataset no esta presente, se reconstruye el orden desde el
            # class_map de la semana 02 (ambos se generan ordenando carpetas).
            clases = _nombres_clases()
            clase_red = (clases[pred] if 0 <= pred < len(clases)
                         else str(pred))

            top_red = []
            if clases and len(clases) == len(probs):
                orden = sorted(range(len(probs)), key=lambda i: probs[i],
                               reverse=True)[:3]
                top_red = [{"clase": clases[i], "probabilidad": float(probs[i])}
                           for i in orden]

            resultado["semanas"]["8"] = {
                "titulo": "Semana 08 - Red neuronal MLP + evidencia + ontologia",
                "prediccion": clase_red,
                "confianza": conf_red,
                "top3": top_red,
                "arquitectura": "MLP (48x48 gris -> 2304 entradas)",
                "evidencia": _evidencia_sqlite(clase_red),
                "ontologia": _resumen_ontologia(),
            }
        else:
            resultado["semanas"]["8"] = {
                "titulo": "Semana 08 - Red neuronal MLP + evidencia + ontologia",
                "no_disponible": True,
                "detalle": red_err or "modelo de la semana 08 no disponible",
            }

        # --- Semana 09: vision por computador ------------------------------
        vision, bordes, panel_b64 = _vision_semana09(ruta)
        resultado["semanas"]["9"] = {
            "titulo": "Semana 09 - Vision por computador",
            "no_disponible": vision is None,
            "umbral": None if vision is None else float(vision["umbral"]),
            "canales": None if vision is None else vision["canales"],
            "canny": None if vision is None else vision["canny"],
            "total_regiones": None if vision is None else vision["total_regiones"],
            "region_principal": None if vision is None else vision["principal"],
            "cobertura": None if vision is None else float(vision["cobertura"]),
            "imagenes": None if vision is None else vision.get("imagenes"),
            "panel": panel_b64,
        }

        # --- Semana 10: reconocimiento de imagenes (texturas) --------------
        # Compara la imagen subida por el usuario con la hoja sana de
        # referencia del proyecto, reutilizando el mismo pipeline.
        comparacion, error10 = _semana10_comparacion(ruta)
        if comparacion is not None:
            resultado["semanas"]["10"] = {
                "titulo": "Semana 10 - Reconocimiento de imagenes (texturas)",
                **comparacion,
            }
        else:
            resultado["semanas"]["10"] = {
                "titulo": "Semana 10 - Reconocimiento de imagenes (texturas)",
                "no_disponible": True,
                "detalle": error10,
            }

        return jsonify(resultado)

    except Exception as exc:  # pragma: no cover
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500
    finally:
        try:
            os.remove(ruta)
        except OSError:
            pass


def _nombres_clases():
    """Nombres de clase en el orden que usa la semana 08.

    La semana 08 construye CLASES ordenando las carpetas de RAW_DIR. Si el
    dataset no esta presente (esta en .gitignore), se reconstruye el mismo
    orden a partir del class_map de la semana 02, que se genero con el mismo
    criterio de ordenacion.
    """
    try:
        from src.config import RAW_DIR
        if RAW_DIR.exists():
            return sorted(carpeta.name for carpeta in RAW_DIR.iterdir()
                          if carpeta.is_dir())
    except Exception:
        pass
    try:
        import json
        from src.config import MODELS_DIR
        ruta = MODELS_DIR / "class_map.json"
        if ruta.exists():
            with open(ruta, "r", encoding="utf-8") as fh:
                cm = json.load(fh)
            return [nombre for nombre, _ in sorted(cm.items(),
                                                   key=lambda kv: kv[1])]
    except Exception:
        pass
    return []


def _evidencia_sqlite(clase_red):
    """Lee la evidencia guardada por la semana 08 (SQLite), si existe."""
    try:
        from src.config import ARTIFACTS_DIR
        import sqlite3

        ruta = ARTIFACTS_DIR / "evidencia_hojas.db"
        if not ruta.exists():
            return None
        with sqlite3.connect(ruta) as con:
            total = con.execute("SELECT COUNT(*) FROM predicciones").fetchone()[0]
            correctas = con.execute(
                "SELECT COALESCE(SUM(correcta),0) FROM predicciones").fetchone()[0]
            filas = con.execute(
                "SELECT id, imagen, categoria_real, prediccion, correcta, fecha "
                "FROM predicciones ORDER BY id LIMIT 5").fetchall()
        return {
            "registros": int(total),
            "correctas": int(correctas),
            "muestras": [
                {"id": f[0], "imagen": f[1], "real": f[2],
                 "prediccion": f[3], "correcta": bool(f[4]), "fecha": f[5]}
                for f in filas
            ],
        }
    except Exception:
        return None


def _resumen_ontologia():
    """Resume la ontologia (GraphML) generada por la semana 08."""
    try:
        from src.config import ARTIFACTS_DIR
        import networkx as nx

        ruta = ARTIFACTS_DIR / "ontologia.graphml"
        if not ruta.exists():
            return None
        G = nx.read_graphml(ruta)
        relaciones = [
            {"origen": o, "relacion": datos.get("rel", ""), "destino": d}
            for o, d, datos in G.edges(data=True)
        ]
        return {
            "nodos": G.number_of_nodes(),
            "relaciones": G.number_of_edges(),
            "detalle": relaciones[:12],
        }
    except Exception:
        return None


def _vision_semana09(ruta):
    """Ejecuta la vision (Canny/Otsu) y genera el panel de evidencia."""
    p = pipeline()
    if p is None:
        return None, None, None
    try:
        vision = p["semana09_vision"].analizar_imagen(ruta)
        bordes, conteo = p["semana09_vision"].barrido_sigma(vision["gris"])
        vision["canny"] = conteo

        canny_b64 = _b64_png(matriz_gris=bordes[1.0])
        otsu_b64 = _b64_png(matriz_gris=vision["mascara"])

        panel_b64 = None
        try:
            from src.config import ARTIFACTS_DIR
            salida = ARTIFACTS_DIR / "web_semana09_panel.png"
            p["semana09_vision"].generar_panel(ruta, salida, limpiar=True)
            with open(salida, "rb") as fh:
                panel_b64 = base64.b64encode(fh.read()).decode("ascii")
        except Exception:
            panel_b64 = None

        vision["imagenes"] = {"canny": canny_b64, "otsu": otsu_b64}
        return vision, bordes, panel_b64
    except Exception:
        return None, None, None


@app.route("/api/consulta", methods=["POST"])
def consulta():
    """Caso B: consulta por sintomas (semana 05, sistema hibrido)."""
    p = pipeline()
    if p is None:
        return jsonify({"error": "Sistema hibrido no disponible",
                        "detalle": _PIPELINE_ERROR}), 500

    datos = request.get_json(silent=True) or {}
    texto = (datos.get("texto") or "").strip()
    if not texto:
        return jsonify({"error": "No se recibio texto de sintomas."}), 400

    try:
        respuesta = p["answer"](texto)
    except Exception as exc:
        respuesta = {"solucion": f"Error: {exc}"}

    ruta = respuesta.get("ruta") if isinstance(respuesta, dict) else None
    plan = (ruta or {}).get("plan") if isinstance(ruta, dict) else None
    categoria = respuesta.get("categoria") if isinstance(respuesta, dict) else None

    validacion = None
    if categoria:
        acciones = [accion for _, accion, _, _ in (plan or [])]
        ok, final, _pasos = p["validar_secuencia"](categoria, acciones)
        validacion = {"valida": bool(ok), "estado_final": final}

    return jsonify({
        "consulta": texto,
        "categoria": categoria,
        "reglas": respuesta.get("reglas") or [],
        "palabras_clave": respuesta.get("palabras_clave") or [],
        "casos": respuesta.get("casos") or [],
        "razones": respuesta.get("razones") or [],
        "explicacion": respuesta.get("explicacion") or "",
        "aplica_astar": bool(respuesta.get("aplica_astar")),
        "intencion_ruta": bool(respuesta.get("intencion_ruta")),
        "solucion": respuesta.get("solucion") or "",
        "plan": [
            {"origen": origen, "accion": accion, "costo": step,
             "siguiente": nxt}
            for (origen, accion, step, nxt) in (plan or [])
        ],
        "costo_total": (ruta or {}).get("total") if isinstance(ruta, dict) else None,
        "validacion": validacion,
    })


if __name__ == "__main__":
    print("PlantAI web en http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
