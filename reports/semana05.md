# Semana 05 - Sistema hibrido

- **Asignatura:** Inteligencia Artificial
- **Proyecto:** PlantAI - Deteccion de Enfermedades en Plantas
- **Modulo:** `src/semana05_sistema_hibrido.py`
- **Ejecucion:** `python -m src.semana05_sistema_hibrido`

Este reporte explica el modulo de la Semana 05: un **sistema hibrido** que
combina tres tecnicas de IA para responder consultas de texto sobre problemas
de plantas. Incluye la **base de conocimiento** utilizada (contenido completo)
y la **salida real** que produce en consola.

---

## 1. Que hace el modulo

Dado un problema de una planta descrito en lenguaje natural, el sistema genera
una respuesta combinando tres tecnicas de IA:

1. **Reglas de conocimiento (sistemas expertos):** palabras clave definidas a
   mano activan una categoria. Ejemplo: si la consulta menciona *"mosaico"* o
   *"amarillamiento"*, se activa la regla *Enfermedades virales*.
2. **Similitud de coseno (TF-IDF + cosine):** texto plano y estadistico. Cada
   consulta se vectoriza con TF-IDF y se compara contra los documentos de la
   base de conocimiento; el documento mas parecido se usa como **evidencia**.
3. **Clasificacion supervisada (LogisticRegression):** un clasificador
   entrenado con descripciones etiquetadas asigna la consulta a una categoria
   (fungica, viral, plaga o sana).

El sistema responde con los cuatro datos por consulta: **reglas activadas**,
**evidencia**, **similitud** y **clasificacion**. Asi puede verse como una
misma tecnica puede complementarse: si las reglas discrepan con el clasificador,
la prioridad la tienen las reglas (conocimiento experto) para elegir la
evidencia.

**Conexion con el proyecto:** las semanas 02-04 diagnostican a partir de
**imagenes**; esta semana agrega una via **de texto** para el mismo dominio de
enfermedades de plantas, usando las categorias que ya se definieron en la
semana 03.

---

## 2. Base de conocimiento

Archivo `data/base_conocimiento.txt`. Nota: la carpeta `data/` esta excluida de
git, por eso el contenido completo se documenta aqui. El modulo lee este archivo
si existe; si no, se auto-genera con una version minima de 5 documentos.

Contenido completo (10 documentos):

```
1. Enfermedades fungicas: manchas en las hojas, podredumbre, oxido, mildiu, moho. Causadas por hongos que prosperan en ambientes humedos. Tratamiento: fungicidas, poda de ramas afectadas, mejorar ventilacion y drenaje.

2. Enfermedades bacterianas: manchas acuosas, pudricion blanda, halo amarillo alrededor de las lesiones, exudados bacterianos. Causadas por bacterias. Tratamiento: bactericidas, erradicacion parcial de tejido afectado, control estricto del riego.

3. Enfermedades virales: mosaico en las hojas, amarillamiento generalizado, enrollamiento de hojas, enanismo. Sin cura quimica conocida. Tratamiento: erradicacion de plantas infectadas, control de vectores como pulgones y mosca blanca, manejo integrado.

4. Plagas: presencia de insectos como acaros, pulgones, orugas, mosca blanca o minadores en el enves de las hojas. Danos por picaduras y alimentacion. Tratamiento: acaricidas o insecticidas segun la plaga, trampas pegajosas, control biologico con depredadores naturales.

5. Plantas sanas: sin sintomas visibles de enfermedad o plaga. Hojas verdes, crecimiento normal, sin manchas ni deformaciones. Prevencion: riego adecuado, nutricion balanceada, monitoreo regular y buenas practicas agricolas.

6. Diagnostico y monitoreo: inspeccion visual periodica de cultivos para detectar sintomas tempranos. Uso de trampas y sensores. Identificacion temprana permite tratamiento oportuno y reduce perdidas.

7. Nutricion vegetal: deficiencias de nitrogeno, fosforo o potasio provocan amarillamiento, bordes quemados o crecimiento debil. Solucion: analisis de suelo, fertilizacion balanceada y enmiendas organicas.

8. Manejo integrado de plagas: estrategia que combina control biologico, cultural, quimico y fisico. Objetivo: reducir el uso de quimicos y mantener el equilibrio del ecosistema del cultivo.

9. Resistencia a enfermedades: variedades de plantas criadas para ser resistentes a patogenos especificos. Es la estrategia mas efectiva y sustentable a largo plazo.

10. Calidad de semilla: semilla sana y certificada reduce la probabilidad de enfermedades transmitidas por la semilla. Incluye tratamientos con fungicidas o bactericidas presembrilla.
```

Los documentos 1-5 son los que las reglas prioritarias pueden disparar
(las respuestas de evidencia de la demo). Los documentos 6-10 amplian la base
para las consultas que llegan por similitud de coseno.

---

## 3. Reglas de conocimiento

Las reglas se evaluan en orden de prioridad (mas especificas primero); la
primera que matchea define la evidencia:

| Regla | Palabras clave |
|---|---|
| Enfermedades virales | mosaico, amarillamiento, enrollamiento, enanismo |
| Plantas sanas | sanas, sin manchas, sin sintomas |
| Enfermedades fungicas | mancha, moho, oxido, mildiu, podredumbre, pudricion |
| Plagas | insecto, acaro, pulgon, oruga, mosca blanca, minador |

Si ninguna regla activa, la evidencia se elige por **similitud de coseno**
contra toda la base de conocimiento.

---

## 4. Salida real en consola

Ejecutando `python -m src.semana05_sistema_hibrido`:

```
============================================================
SEMANA 05 - SISTEMA HIBRIDO
============================================================

Consulta 1: Las hojas de mi tomate tienen manchas marrones y algo de moho.
  Reglas activadas : Enfermedades fungicas
  Evidencia        : Enfermedades fungicas: manchas en las hojas, podredumbre, oxido, mildiu, moho. Causadas por hongos que prosperan en ambientes humedos. Tratamiento: fungicidas, poda de ramas afectadas, mejorar ventilacion y drenaje.
  Similitud        : 0.333
  Clasificacion    : fungica

Consulta 2: Veo insectos verdes pequenos en el enves de las hojas.
  Reglas activadas : Plagas
  Evidencia        : Plagas: presencia de insectos como acaros, pulgones, orugas, mosca blanca o minadores en el enves de las hojas. Danos por picaduras y alimentacion. Tratamiento: acaricidas o insecticidas segun la plaga, trampas pegajosas, control biologico con depredadores naturales.
  Similitud        : 0.377
  Clasificacion    : plaga

Consulta 3: Las hojas se estan poniendo amarillas y con patron de mosaico.
  Reglas activadas : Enfermedades virales
  Evidencia        : Enfermedades virales: mosaico en las hojas, amarillamiento generalizado, enrollamiento de hojas, enanismo. Sin cura quimica conocida. Tratamiento: erradicacion de plantas infectadas, control de vectores como pulgones y mosca blanca, manejo integrado.
  Similitud        : 0.350
  Clasificacion    : viral

Consulta 4: Mis plantas tienen las hojas verdes y se ven sanas sin manchas.
  Reglas activadas : Plantas sanas, Enfermedades fungicas
  Evidencia        : Plantas sanas: sin sintomas visibles de enfermedad o plaga. Hojas verdes, crecimiento normal, sin manchas ni deformaciones. Prevencion: riego adecuado, nutricion balanceada, monitoreo regular y buenas practicas agricolas.
  Similitud        : 0.484
  Clasificacion    : sana

Consulta 5: Hay oxido y podredumbre en las hojas y los frutos del cultivo.
  Reglas activadas : Enfermedades fungicas
  Evidencia        : Enfermedades fungicas: manchas en las hojas, podredumbre, oxido, mildiu, moho. Causadas por hongos que prosperan en ambientes humedos. Tratamiento: fungicidas, poda de ramas afectadas, mejorar ventilacion y drenaje.
  Similitud        : 0.373
  Clasificacion    : fungica

============================================================
Consultas procesadas: 5
============================================================
```

**Lectura del output:** en 4 de 5 consultas las tres tecnicas coinciden
(fungica, plaga, viral, fungica). En la consulta 4 se activan dos reglas
(*Plantas sanas* y *Enfermedades fungicas*) porque la frase "sin manchas"
menciona la palabra *manchas*; gana la regla con mayor prioridad
(*Plantas sanas*) y el clasificador tambien responde *sana*. Es un ejemplo
practico de **resolucion de conflictos** entre tecnicas, propio de un sistema
hibrido.

---

## 5. Como ejecutar

```
.\.venv\Scripts\activate
python -m src.semana05_sistema_hibrido
```

Solo usa `scikit-learn` (ya instalado). No agrega dependencias ni carga
imagenes del dataset; trabaja con texto.