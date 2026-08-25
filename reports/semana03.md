# Semana 03 - Taxonomia de Inteligencia Artificial

## Titulo del avance

Clasificacion taxonomica del proyecto de deteccion de enfermedades en plantas dentro del area de Inteligencia Artificial.

## Descripcion del proyecto

El proyecto consiste en desarrollar una solucion de Inteligencia Artificial para la **deteccion o clasificacion de enfermedades en plantas** a partir de imagenes. Utiliza el dataset PlantVillage, que contiene 54,304 imagenes clasificadas en 38 categorias correspondientes a diferentes cultivos, enfermedades y plantas sanas.

## Problema que busca resolver

La identificacion temprana de enfermedades en cultivos es un problema agricola importante. Los agricultores necesitan diagnosticar rapidamente si una planta esta sana o presenta alguna enfermedad, lo cual tradicionalmente requiere conocimiento especializado. Este proyecto busca automatizar ese proceso de diagnostico utilizando tecnicas de Inteligencia Artificial.

## Area principal de Inteligencia Artificial

### Vision por computador

El proyecto pertenece principalmente al area de **Vision por computador**. Esto se justifica porque:

- El dato de entrada son **imagenes** (fotografias de hojas de plantas).
- El problema requiere **analizar contenido visual** para extraer caracteristicas relevantes (patrones de color, textura, formas de manchas, etc.).
- El objetivo es que la maquina "vea" y comprenda lo que hay en una imagen para tomar una decision (sana o enferma).

La vision por computador es el area de la IA que estudia como hacer que las computadoras obtengan informacion de alto nivel a partir de imagenes o videos digitales.

## Areas secundarias relacionadas

### Aprendizaje automatico (Machine Learning)

El proyecto tambien se relaciona con el area de **Aprendizaje automatico** porque:

- Se utiliza un modelo que **aprende a partir de ejemplos** (las imagenes etiquetadas del dataset).
- El modelo se **entrena** con datos y luego se evalua con datos que no ha visto anteriormente.
- Se aplican conceptos como conjunto de entrenamiento, conjunto de prueba, accuracy y matriz de confusion.

El aprendizaje automatico es el subcampo de la IA que se enfoca en construir sistemas que aprenden automaticamente a partir de los datos.

### Relacion entre ambas areas

El proyecto se encuentra en la **interseccion** de ambas areas:

| Area | Rol en el proyecto |
|------|-------------------|
| Vision por computador | Procesamiento y analisis de imagenes de plantas |
| Aprendizaje automatico | Entrenamiento de un modelo para clasificar las imagenes |

**Vision por computador** es el area principal porque el nucleo del problema es interpretar imagenes. **Aprendizaje automatico** es el area complementaria porque proporciona los metodos para que el modelo aprenda a clasificar.

## Justificacion de la clasificacion

### Por que Vision por computador?

El dataset esta compuesto enteramente por imagenes. Cada muestra es una fotografia de una hoja de planta que puede estar sana o presentar signos de una enfermedad (manchas, decoloracion, marchitez, etc.). El desafio tecnico principal es extraer informacion util de pixels, lo cual es el objetivo central de la vision por computador.

### Por que Aprendizaje automatico?

El proyecto no utiliza reglas escritas manualmente para diagnosticar enfermedades. En su lugar, entrena un modelo con ejemplos etiquetados para que aprenda los patrones que distinguen una planta sana de una enferma. Este enfoque basado en datos es la esencia del aprendizaje automatico.

### Otras areas de la taxonomia descartadas

| Area | Por que NO aplica |
|------|------------------|
| Procesamiento de lenguaje natural | No se procesa texto ni lenguaje natural |
| Sistemas de recomendacion | No se recomiendan productos ni contenido |
| Busqueda y optimizacion | No se buscan rutas ni soluciones optimas |
| Sistemas expertos | No se basan en reglas escritas por expertos |
| Robotica y sistemas autonomos | No hay robots ni navegacion autonoma |

## Conclusion

El proyecto de deteccion de enfermedades en plantas pertenece principalmente a la **Vision por computador**, ya que su nucleo tecnico es el analisis de imagenes. Complementariamente, se apoya en el **Aprendizaje automatico** para entrenar un modelo clasificador. Esta clasificacion es coherente con las caracteristicas reales del proyecto: un dataset de imagenes etiquetadas que se utiliza para entrenar un modelo de clasificacion.
