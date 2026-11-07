<!-- Slide number: 1 -->

Inteligencia Artificial  |  Semana 14

Material docente editable · Redes semánticas · 1

**01**

**Semana 14**

**Ingeniería del**

**conocimiento**

**Representaciones del conocimiento y**

**lingüística con redes semánticas**

**Conceptos**

**Relaciones**

**Inferencia**

**Lingüística**

**Meta: construir una red semántica desde oraciones y demostrar una inferencia.**

![/mnt/data/sem14_ia_work/foto_plantilla.png]()

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
El sílabo establece esta semana como Ingeniería del conocimiento: representaciones del conocimiento y lingüística con redes semánticas. Enfatice que el lenguaje elegido para practicar no forma parte del sílabo.
[Demostración o ejemplo]
Muestre la frase «Un perro es un mamífero» y conviértala en tres piezas.
[Pregunta al grupo]
¿Qué información necesita un programa para responder «¿perro es animal?»?
[Respuesta esperada]
Nodos, relaciones explícitas y una regla de inferencia por jerarquía.

1

<!-- Slide number: 2 -->

Inteligencia Artificial  |  Semana 14

**Ruta de la clase**

Qué se comprende, qué se implementa y qué se entrega

Material docente editable · Redes semánticas · 2

**02**

**1**

Diferenciar datos, conceptos y conocimiento

**2**

Interpretar redes con nodos y aristas

**3**

Convertir oraciones en triples semánticos

**4**

Implementar el modelo con Python (propuesta)

**5**

Consultar jerarquía y propiedades heredadas

**6**

Ejecutar pruebas y justificar resultados

**es_un**

**es_un**

**es_un**

**necesita**

**perro**

**mamífero**

**animal**

**gato**

**agua**

**Resultado: una red con hechos explícitos, consultas e inferencias justificadas.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
La ruta sigue una progresión desde representar información hasta justificar una conclusión calculada.
[Demostración o ejemplo]
Trace un recorrido de seis pasos en el tablero y pregunte dónde aparece realmente la inferencia.
[Pregunta al grupo]
¿La inferencia ocurre al leer la oración o al recorrer el grafo?
[Respuesta esperada]
Al recorrer hechos y aplicar una regla de inferencia declarada.

2

<!-- Slide number: 3 -->

Inteligencia Artificial  |  Semana 14

**Modelo mental de una red semántica**

Una oración se vuelve una estructura que puede consultarse

Material docente editable · Redes semánticas · 3

**03**

**1. Lenguaje
**Una persona formula una oración comprensible en español.

**2. Representación
**El sistema identifica sujeto, relación y objeto.

**3. Grafo
**Los conceptos se vuelven nodos y las relaciones, aristas.

**4. Consulta / inferencia
**Una regla recorre las aristas para responder.

**es_un**

**es_un**

**es_un**

**necesita**

**perro**

**mamífero**

**animal**

**gato**

**agua**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
En la red semántica un nodo no es la palabra escrita en sí, sino un concepto modelado dentro de un dominio. Las flechas tienen nombres y direcciones.
[Demostración o ejemplo]
Dibuje perro → mamífero → animal y pregunte si el sistema necesita una flecha directa perro → animal.
[Pregunta al grupo]
¿Qué representan nodos y aristas?
[Respuesta esperada]
Nodos: conceptos o entidades; aristas etiquetadas: relaciones de significado entre ellos.

3

<!-- Slide number: 4 -->

Inteligencia Artificial  |  Semana 14

**Fundamentos de ingeniería del conocimiento**

Representar no es solo guardar palabras: exige definir significado y reglas

Material docente editable · Redes semánticas · 4

**04**

**Concepto
**Entidad o categoría del dominio: perro, mamífero, animal.

**Relación
**Predicado dirigido: es_un o necesita.

**Regla
**Criterio explícito para obtener conocimiento nuevo.

HECHO 1  (perro, es_un, mamifero)

HECHO 2  (mamifero, es_un, animal)

REGLA   es_un + es_un  =>  es_un

CONCLU. (perro, es_un, animal)

**La conclusión no se almacenó: se infiere a partir de los hechos y la regla.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Exponga la diferencia entre almacenar hechos y aplicar reglas. No todas las relaciones admiten transitividad ni herencia.
[Demostración o ejemplo]
Construya tres tarjetas; indique cuáles son hechos y cuál es la regla.
[Pregunta al grupo]
¿Puede deducirse “necesita” transitivamente de la misma forma que “es_un”?
[Respuesta esperada]
No automáticamente: cada predicado exige una semántica y reglas propias.

4

<!-- Slide number: 5 -->

Inteligencia Artificial  |  Semana 14

**Lingüística y representación semántica**

De una oración simple a un triple sujeto–relación–objeto

Material docente editable · Redes semánticas · 5

**05**

**«Un perro es un mamífero»**

**sujeto**

**relación**

**objeto**

**PERRO
**Concepto origen de la afirmación.

**ES_UN
**Arista etiquetada.

**MAMÍFERO
**Concepto destino.

**Límite del ejemplo
**El analizador reconoce frases con dos patrones fijos. No interpreta lenguaje natural general, ambigüedad ni negaciones.

("perro", "es_un", "mamifero")

**Normalizar palabras facilita comparaciones, pero puede perder matices del lenguaje.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Relacione la lingüística con la identificación de términos y predicados. Un triple es una representación simplificada, no una gramática completa.
[Demostración o ejemplo]
Escriba la oración, marque las tres partes y cambie “es un” por “necesita” para discutir nuevas relaciones.
[Pregunta al grupo]
¿Por qué “Los perros corren muy rápido” no funciona en este ejercicio?
[Respuesta esperada]
Porque no coincide con los dos patrones gramaticales programados.

5

<!-- Slide number: 6 -->

Inteligencia Artificial  |  Semana 14

**Red semántica: nodos y enlaces**

Las aristas dirigidas permiten expresar tipos distintos de conocimiento

Material docente editable · Redes semánticas · 6

**06**

**es_un**

**es_un**

**es_un**

**necesita**

**perro**

**mamífero**

**animal**

**gato**

**agua**

**es_un
**Relaciona un concepto con una clase o categoría. La práctica habilita transitividad en esta relación.

**necesita
**Expresa una propiedad del nodo. La práctica la hereda por categorías superiores como supuesto didáctico.

**Nunca mezcles dos predicados distintos solo porque ambos están dibujados como flechas.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Distinga relaciones taxonómicas de atributos. Las etiquetas son relevantes: dos aristas visualmente similares pueden tener reglas muy diferentes.
[Demostración o ejemplo]
En el grafo dibuje una flecha morada para “necesita” y verdes para “es_un”.
[Pregunta al grupo]
¿Por qué es importante guardar la etiqueta de la relación?
[Respuesta esperada]
Porque determina el significado del enlace y qué inferencias pueden aplicarse.

6

<!-- Slide number: 7 -->

Inteligencia Artificial  |  Semana 14

**Representación formal: triples**

La unidad mínima del grafo es (sujeto, relación, objeto)

Material docente editable · Redes semánticas · 7

**07**

("perro", "es_un", "mamifero")

("mamifero", "es_un", "animal")

("animal", "necesita", "agua")

**Hecho explícito
**Es una relación añadida directamente a la estructura de datos.

**Dato inferido
**Se obtiene al recorrer enlaces y aplicar una regla del dominio.

**Ejemplo de inferencia: «perro es_un animal» sin crear una arista directa.**

red.agregar("perro", "es_un", "mamifero")

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Un triple es una estructura simple de conocimiento: dos conceptos conectados por un predicado. En el código se almacena como una entrada en un diccionario de listas.
[Demostración o ejemplo]
Muestre cómo una lista de tuplas se transforma en aristas; identifique qué se almacena explícitamente.
[Pregunta al grupo]
¿Por qué no incluir siempre todos los hechos inferidos en la base?
[Respuesta esperada]
Porque pueden derivarse bajo demanda; guardar todo agrega mantenimiento y posible inconsistencia.

7

<!-- Slide number: 8 -->

Inteligencia Artificial  |  Semana 14

**Inferencia por jerarquía y herencia**

Recorrer el grafo permite concluir hechos que no aparecen como aristas directas

Material docente editable · Redes semánticas · 8

**08**

**perro**

**mamífero**

**animal**

**agua**

**es_un**

**es_un**

**necesita**

**Regla 1: si A es_un B y B es_un C, entonces A es_un C.**

**Regla 2 (didáctica): A hereda «necesita» de sus categorías superiores.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Presente dos reglas diferentes, transitividad de `es_un` y herencia declarada de la propiedad `necesita`. Aclare que la herencia no siempre es válida fuera de este modelo.
[Demostración o ejemplo]
Recorra físicamente las flechas perro→mamífero→animal→agua y explique dónde cambia de predicado.
[Pregunta al grupo]
¿La conclusión «perro necesita agua» está escrita directamente en los hechos?
[Respuesta esperada]
No; es una propiedad heredada bajo una regla explícita del programa.

8

<!-- Slide number: 9 -->

Inteligencia Artificial  |  Semana 14

**Práctica guiada en clase**

De oraciones en español a consultas y pruebas automatizadas

Material docente editable · Redes semánticas · 9

**09**

**1**

**Crear carpeta
**Iniciar el ejercicio del proyecto.

**2**

**Crear módulo
**red_semantica.py

**3**

**Normalizar
**Eliminar tildes y mayúsculas.

**4**

**Interpretar
**Reconocer dos tipos de oraciones.

**5**

**Registrar
**Almacenar triples en el grafo.

**6**

**Consultar
**Jerarquía es_un.

**7**

**Heredar
**Recorrer la relación necesita.

**8**

**Ejecutar
**python main.py

**9**

**Probar
**python -m unittest -v

**No es tecnología exigida en el sílabo: Python y unittest son una propuesta de laboratorio.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Recuerde que las herramientas y versiones son una decisión pedagógica, no una prescripción del sílabo. Mantenga todos los archivos en la misma carpeta.
[Demostración o ejemplo]
Construya la primera oración junto al grupo y guarde el triple en un diccionario.
[Pregunta al grupo]
¿En qué archivo está la lógica y en cuál el guion de prueba manual?
[Respuesta esperada]
En `red_semantica.py` está la lógica; `main.py` ejecuta la demostración.

9

<!-- Slide number: 10 -->

Inteligencia Artificial  |  Semana 14

**Código comentado — Bloque 1**

Archivo red_semantica.py · normalización y análisis de oraciones

Material docente editable · Redes semánticas · 10

**10**

import re

import unicodedata

def normalizar(texto):

    base = unicodedata.normalize(

        "NFD", texto.casefold().strip())

    return "".join(

        c for c in base

        if unicodedata.category(c) != "Mn")

**Importaciones
**`re` reconoce patrones; `unicodedata` permite normalizar cadenas con tildes.

**casefold + NFD
**Unifica las variaciones de escritura y separa marcas de acento.

**return
**Produce una cadena canónica como mamifero, utilizada en los triples.

**Código completo y explicación línea por línea: archivo Markdown complementario.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
La normalización lingüística sirve para comparaciones, pero no resuelve el significado ni todas las variaciones gramaticales. Separa caracteres Unicode antes de filtrar marcas combinantes.
[Demostración o ejemplo]
Compare “MAMÍFERO” y “mamifero” antes y después de normalizar.
[Pregunta al grupo]
¿Qué aporta casefold() y qué hace NFD?
[Respuesta esperada]
casefold simplifica comparación de mayúsculas; NFD separa letras y marcas acentuadas.

10

<!-- Slide number: 11 -->

Inteligencia Artificial  |  Semana 14

**Código comentado — Bloque 2**

Consulta de jerarquía en RedSemantica.es_un

Material docente editable · Redes semánticas · 11

**11**

def es_un(self, origen, categoria):

    pendientes = [origen]

    visitados = set()

    while pendientes:

        actual = pendientes.pop()

        if actual == categoria:

            return True

        if actual in visitados:

            continue

        visitados.add(actual)

        for relacion, destino in self.aristas.get(actual, []):

            if relacion == "es_un":

                pendientes.append(destino)

    return False

**pendientes
**Pila de conceptos por recorrer desde el origen hasta la categoría buscada.

**visitados
**Evita ciclos infinitos en la jerarquía y repeticiones de trabajo.

**Filtro de relación
**Solo las aristas `es_un` participan en esta consulta de jerarquía.

**Resultado: True si hay camino; False si no hay evidencia en el grafo.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Explique el algoritmo de recorrido y el uso de `visitados`. Este método calcula transitividad de es_un, no de cualquier relación arbitraria.
[Demostración o ejemplo]
Simule pendientes=[perro] y siga las iteraciones hasta encontrar animal.
[Pregunta al grupo]
¿Qué evita que un ciclo animal→perro cause un bucle infinito?
[Respuesta esperada]
El conjunto visitados evita procesar repetidamente los mismos nodos.

11

<!-- Slide number: 12 -->

Inteligencia Artificial  |  Semana 14

**Pruebas y resultado esperado**

Diferenciar hechos cargados, inferencias correctas y entradas rechazadas

Material docente editable · Redes semánticas · 12

**12**

$ python main.py

Hecho: (perro, es_un, mamifero)

Hecho: (mamifero, es_un, animal)

Hecho: (animal, necesita, agua)

Hecho: (gato, es_un, mamifero)

¿Perro es un animal?: True

Necesidades de perro: ['agua']

¿Perro es un ave?: False

**Caso esperado
**True: perro alcanza animal mediante dos enlaces es_un.

**Herencia
**[agua]: se obtiene de una propiedad asociada a animal.

**Caso negativo
**False: no se encuentra ruta a ave en los hechos registrados.

**Prueba adicional: una oración no admitida debe generar ValueError.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Las líneas de Hecho son datos explícitos; las respuestas de consulta derivan de recorrer la red. False significa falta de evidencia, no negación universal.
[Demostración o ejemplo]
Ejecute `python main.py` y compare con la guía; ejecute luego `python -m unittest -v`.
[Pregunta al grupo]
¿Qué líneas del resultado son hechos y cuáles conclusiones inferidas?
[Respuesta esperada]
Los cuatro triples son hechos, y las tres consultas devuelven resultados calculados.

12

<!-- Slide number: 13 -->

Inteligencia Artificial  |  Semana 14

**Errores frecuentes y correcciones**

Guía rápida para depurar la práctica de redes semánticas

Material docente editable · Redes semánticas · 13

**13**

**No importa el módulo
**Revisar que main.py y red_semantica.py estén juntos.

**Oración rechazada
**Verificar estructura; el parser solo admite dos patrones.

**Jerarquía inesperada
**Inspeccionar triples y normalización de conceptos.

**Herencia incorrecta
**Comprobar si la relación permite propagación.

**Python incompatible
**Usar 3.10+ o adaptar anotaciones de tipos.

**Ciclo de categorías
**Usar visitados e inspeccionar la calidad del modelo.

**Depurar = revisar entrada, triple generado, aristas almacenadas y regla aplicada.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Enseñe a localizar errores por etapas: parser, almacenamiento, consulta e inferencia. Los mensajes de error son evidencia útil.
[Demostración o ejemplo]
Introduzca una frase de gramática libre y muestre el ValueError; explique por qué es más seguro que inventar un triple.
[Pregunta al grupo]
¿Es correcto ampliar el parser sin agregar pruebas?
[Respuesta esperada]
No. Cada nueva regla exige ejemplos válidos, inválidos y casos límite.

13

<!-- Slide number: 14 -->

Inteligencia Artificial  |  Semana 14

**Entregable y adaptación al proyecto**

La evidencia debe demostrar que el estudiante entiende su modelo

Material docente editable · Redes semánticas · 14

**14**

**Código de la práctica
**red_semantica.py, main.py y test_red_semantica.py.

**Prueba observada
**Captura o salida de consola y reporte de casos exitosos.

**Adaptación del dominio
**Reemplazar animales por 4–8 conceptos del proyecto y justificar las relaciones.

**Cómo revisar
**Realizado · Funciona · Coincide · Sustenta.

**Pregunta de sustentación
**¿Qué inferencia obtuvo, por qué es válida y qué límite tiene?

**Nota académica
**El sílabo no fija fecha, formato de commit ni puntaje para este ejemplo; son orientaciones de aula.

**Propuesta de commit: semana14-redes-semanticas (opcional).**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14 (tema oficial).
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Esta práctica sirve como guía de clase; no se inventan fechas ni una ponderación distinta a la institucional. Los proyectos propios necesitan semántica de relaciones validada.
[Demostración o ejemplo]
Pida un ejemplo distinto al de animales; valore la explicación de por qué una propiedad puede heredarse o no.
[Pregunta al grupo]
¿Por qué no basta copiar los nodos del ejemplo?
[Respuesta esperada]
Porque el objetivo es modelar un dominio propio y justificar sus relaciones e inferencias.

14

<!-- Slide number: 15 -->

Inteligencia Artificial  |  Semana 14

**Cierre de clase**

Lo que el estudiante debe poder explicar con sus propias palabras

Material docente editable · Redes semánticas · 15

**15**

**Red semántica
**Conceptos conectados mediante relaciones dirigidas y etiquetadas.

**Lingüística
**De una oración simple a un triple estructurado con alcance limitado.

**Inferencia
**Reglas explícitas permiten alcanzar conocimiento no escrito directamente.

**es_un**

**es_un**

**es_un**

**necesita**

**perro**

**mamífero**

**animal**

**gato**

**agua**

**Frase: representar organiza hechos; interpretar extrae relaciones; inferir aplica reglas.**

### Notes:
[Sources]
Sílabo de Inteligencia Artificial, p. 3, Semana 14; resultados RAC1/RAC2 p. 2.
PPTX de referencia (JSP): únicamente estructura y tratamiento visual.
[Explicación para decir en clase]
Finalice reiterando los tres componentes: representación, interpretación lingüística simplificada e inferencia declarada. Las redes semánticas requieren claridad de dominio.
[Demostración o ejemplo]
Reproduzca un recorrido completo: oración → triple → nodo/arista → inferencia.
[Pregunta al grupo]
¿Qué diferencia hay entre un hecho almacenado y una inferencia, y qué limitación tiene el analizador?
[Respuesta esperada]
Hecho: triple guardado; inferencia: derivación por reglas; analizador: reconoce solo dos patrones lingüísticos.

15