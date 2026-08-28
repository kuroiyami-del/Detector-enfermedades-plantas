# Semana 04 - Plan de recuperacion con A*

**Modulo:** `src/semana04_busqueda.py` | **Ejecucion:** `python -m src.semana04_busqueda`

## Que hace

Las semanas anteriores dicen **que tiene** la planta (imagen -> clase -> tipo).
Esta semana (con A*) calcula **como sanarla con el menor costo**:

```
enfermedad detectada --A*--> plan de tratamientos optimo -> planta sana
```

Un solo agente planifica (no hay adversario, por eso Minimax no aplica).

## Salida en consola

```
SEMANA 04 - BUSQUEDA EN ESPACIO DE ESTADOS: PLAN DE RECUPERACION

Diagnostico de ejemplo (salida del clasificador): Tomato___Late_blight
Categoria (semana 03): Enfermedades fungicas

--- Modelo: estados y tratamientos ---
  Estado actual        Tratamiento                    Estado siguiente   Costo
  enfermedad_avanzada  podar_rama_afectada            enfermedad_activa  3
  enfermedad_avanzada  aplicar_fungicida_fuerte       en_recuperacion    6
  enfermedad_activa    aplicar_fungicida              en_recuperacion    2
  en_recuperacion      aplicar_fungicida              healthy            3
  en_recuperacion      seguimiento_semanal            healthy            4

--- Recorrido encontrado por A* ---
  enfermedad_avanzada    g=0  h=6  f=6
  enfermedad_avanzada    --podar_rama_afectada (+3)--> enfermedad_activa  g=3  h=4  f=7
  enfermedad_activa      --aplicar_fungicida (+2)--> en_recuperacion    g=5  h=2  f=7
  en_recuperacion        --aplicar_fungicida (+3)--> healthy            g=8  h=0  f=8

--- Plan optimo de recuperacion ---
  1. podar_rama_afectada ............ +3
  2. aplicar_fungicida ............ +2
  3. aplicar_fungicida ............ +3
  Costo total: 8
  Nodos expandidos: 4
```

**Lectura:** el plan cuesta 8. La otra via (`fungicida_fuerte` 6 + `seguimiento_semanal` 4 = 9) es mas cara y A* la descarta.

## La idea del algoritmo

- **Estados:** `enfermedad_avanzada` -> `enfermedad_activa` -> `en_recuperacion` -> `healthy` (meta).
- **Acciones:** tratamientos; cada uno tiene un **costo** y lleva a otro estado.
- **g(n):** costo acumulado. **h(n):** estimacion optimista del costo restante (heuristica, nunca sobrestima).
- **f(n) = g(n) + h(n):** A* siempre expande el nodo de menor f, por eso encuentra el **camino mas barato**.
- **Casos:** si la clase es sana -> plan vacio. Si la enfermedad es viral -> "meta inalcanzable" (no hay cura).

## Que hace cada parte del codigo

| Parte | Que hace |
|---|---|
| `import heapq` + `classify_class` | Cola de prioridad para A*; funcion de la semana 03 que da el tipo de enfermedad |
| `META`, `ESTADO_INICIAL` | Meta = `healthy`; toda enfermedad inicia en `enfermedad_avanzada` |
| `H` | La heuristica h(n): tabla de "costo restante estimado" por estado |
| `TRATAMIENTOS` | El grafo: cada estado tiene una lista de `(tratamiento, estado_siguiente, costo)` |
| `astar(grafo, inicio)` | El algoritmo A*: expande el nodo de menor f, guarda el mejor g de cada estado y al final reconstruye el plan desde la meta |
| `show_tratamientos(grafo)` | Imprime la tabla de tratamientos (solo visual) |
| `run()` | Orquesta todo: obtiene el tipo, elige el grafo, ejecuta A* e imprime resultados + formulacion |
| `if __name__ == "__main__"` | Permite ejecutar el modulo solo (`python -m ...`) sin afectar `main.py` |

**Ojo:** los estados y costos son un **modelo didactico** de ejemplo, no datos biologicos reales. A* no reemplaza al clasificador (semana 02); solo planifica la accion de apoyo despues del diagnostico.