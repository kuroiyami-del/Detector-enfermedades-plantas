# Semana 07 - Representaciones del conocimiento

- **Asignatura:** Inteligencia Artificial
- **Proyecto:** PlantAI - Deteccion de Enfermedades en Plantas
- **Modulo:** `src/semana07_representaciones.py`
- **Interfaz:** `gui.py` (secciones `§ 3 Representacion Numerica de la Hoja` y `§ 4 Representacion Simbolica de la Salud de la Planta`)
- **Ejecucion:** `python gui.py` (diagnostico por imagen) o `python -m src.semana07_representaciones`

Este reporte compara las dos formas de representar la salud de una hoja que se
implementaron en la Semana 07. No es una comparacion generica: ambas
representaciones estan **implementadas y en ejecucion en el codigo real**, y se
muestran en paralelo en el panel de resultados de `gui.py`. La misma imagen de
una planta genera, al mismo tiempo, un **vector de numeros** (seccion 3) y un
**conjunto de etiquetas + reglas simbolicas** (seccion 4); este documento
analiza que aporta cada una y que deja de capturar.

---

## Comparativa

| Aspecto | Representacion Numerica | Representacion Simbolica |
|---|---|---|
| **Que informacion utiliza** | Los pixeles de la imagen RGB de la hoja (reducida a 64x64). Con ellos calcula un vector de 3 componentes: `verdor` (razon media del canal verde), `amarillez` (diferencia rojo-verde normalizada) y `manchas` (desviacion estandar de la escala de grises). Compara ese vector contra una referencia fija de hoja sana `[0.85, 0.10, 0.05]` mediante distancia euclidiana. | La **categoria taxonomica** que ya decidieron las semanas anteriores (`classify_class`), traducida a un conjunto de hechos como etiquetas de sintomas: por ejemplo `manchas_concetricas`, `esporas_en_borde`, `halo_amarillento`, `exudado_acuoso`, `patron_mosaico`, `telarana_fina`, `follaje_uniforme`. Esos hechos se evaluan contra 5 reglas del tipo `SI condiciones ENTONCES conclusion`. |
| **Que puede reconocer** | Un **grado numerico de alejamiento** respecto a la hoja sana: la distancia euclidiana (0 = identica a la referencia; a mayor valor, mas sospechosa). Es un indice continuo de "que tan enferma se ve la hoja", calculado directamente desde los pixeles. | Una **conclusion simbolica legible**: el tipo de sospecha (fungica, bacteriana, viral, acaros) o `planta_sana` / `sin_concluir`, junto con la regla que la disparo. Reconoce **que tipo de enfermedad** es, no solo cuanto se desvia la hoja. |
| **Ventajas** | Es objetiva y continua: cuantifica el nivel de dano con un numero comparable entre imagenes; se calcula automaticamente desde los datos reales de la foto (solo numpy/PIL); admite ser ordenada, umbralizada o analizada estadisticamente; no depende de reglas escritas a mano. | Es **interpretable y explicable**: muestra "SI se observan X e Y ENTONCES Z", muy cerca de como piensa un agronomo; distingue entre los 5 tipos del dominio (fungicas, bacterianas, virales, plagas y sanas) que la parte numerica no separa; usa conocimiento declarativo facil de ampliar agregando mas hechos o reglas. |
| **Limitaciones** | Solo resume la hoja en 3 agregados globales: omite la forma, tamano y distribucion de las lesiones; la referencia `[0.85, 0.10, 0.05]` es una constante elegida a mano, no medida del dataset; la distancia sola no distingue *que* enfermedad es (dos patogenos distintos pueden dar vectores similares). | Los hechos **no se extraen de la imagen**: se asignan a partir de la categoria ya clasificada, de modo que no aporta precision de medida; las conclusiones son discretas (sospecha de X, sin nivel de severidad); la primera regla que matchea fija la conclusion y oculta las demas; si la categoria no esta en el mapa, concluye `sin_concluir`. |
| **Informacion que puede perderse** | Pierde el **significado** del sintoma: un vector dice "amarillez 0.55" pero no que eso corresponde a mosaico, halo bacteriano o carencia; pierde la identidad de la enfermedad, la relacion entre sintomas y el conocimiento experto sobre causas y tratamientos. | Pierde la **magnitud**: no dice si la enfermedad es incipiente o avanzada, ni la proporcion de la hoja afectada, ni la distancia a lo sano; pierde la evidencia pixel-a-pixel y las variaciones continuas (una hoja ligeramente amarillenta es "con sospecha" sin matiz de intensidad). |

---

## Conclusion

Las dos representaciones son **complementarias**, no rivales. La numerica aporta
la **evidencia medida** (un indice continuo de dano calculado sobre los pixeles
reales de la hoja), pero no interpreta *que* esta pasando; la simbolica aporta el
**significado** (una sospecha etiquetada de tipo de enfermedad construida con
hechos y reglas IF-THEN), pero renuncia a la precision numerica. Por eso el
diagnostico de `gui.py` las muestra juntas: el vector y la distancia de la
seccion 3 dan el "cuanto", y los hechos, las reglas y la conclusion de la
seccion 4 dan el "que". Esta dupla ilustra el concepto central de la semana: un
mismo problema (la salud de una planta) se puede representar numericamente o de
forma simbolica, y cada representacion ilumina aspectos que la otra no puede
capturar por si sola.