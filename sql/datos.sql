-- Semana 15 - Datos ficticios del repositorio de conocimiento de PlantAI.
-- Los nombres de personas y herramientas son de ejemplo: no representan a
-- personas reales. INSERT OR IGNORE permite ejecutar el archivo dos veces.

INSERT OR IGNORE INTO dominio (id, nombre) VALUES
    (1, 'Diagnostico foliar'),
    (2, 'Manejo fitosanitario'),
    (3, 'Calidad de datos');

INSERT OR IGNORE INTO aplicacion (id, nombre, dominio_id) VALUES
    (1, 'Pipeline PlantAI', 1),
    (2, 'Planificador A*', 2),
    (3, 'Dataset PlantVillage', 3);

INSERT OR IGNORE INTO experto (id, nombre, cargo) VALUES
    (1, 'Ana Rivera', 'Ingeniera agronoma fitosanitaria'),
    (2, 'Luis Torres', 'Analista de datos de imagenes'),
    (3, 'Marta Salas', 'Tecnica de calidad de datos');

INSERT OR IGNORE INTO herramienta (id, nombre, finalidad) VALUES
    (1, 'Wiki del proyecto', 'Documentar procedimientos y decisiones'),
    (2, 'Repositorio Git', 'Controlar versiones y fuentes del codigo'),
    (3, 'Gestor de tickets', 'Registrar incidencias y consultas de soporte');

-- Articulo 1: VALIDADO (visible en las consultas normales).
-- Articulo 2: VALIDADO (visible).
-- Articulo 3: VALIDADO (visible).
-- Articulo 4: VALIDADO (visible).
-- Articulo 5: BORRADOR (existe, pero NO aparece en la busqueda habitual).
INSERT OR IGNORE INTO articulo
    (id, titulo, contenido, dominio_id, aplicacion_id, experto_id,
     herramienta_id, fuente, fecha_revision, estado)
VALUES
    (1, 'Registro de evidencia visual del diagnostico',
     'Guardar el panel de la semana 09 y el vector de textura de la semana 10 como evidencia visible del diagnostico realizado.',
     1, 1, 2, 2, 'Reporte semanal del proyecto', '2026-11-02', 'VALIDADO'),
    (2, 'Protocolo de manejo de septoria en tomate',
     'Aplicar el plan A* de tres acciones: retirar las hojas afectadas, tratar con fungicida y repetir el control a los 7 dias.',
     2, 2, 1, 3, 'Manual interno de manejo fitosanitario', '2026-11-05', 'VALIDADO'),
    (3, 'Criterio de clasificacion taxonomica',
     'Asociar cada clase del dataset con su categoria (fungica, bacteriana, viral, plaga o sana) mediante las palabras clave de la semana 03.',
     1, 1, 2, 1, 'Taxonomia de la semana 03', '2026-11-03', 'VALIDADO'),
    (4, 'Protocolo de contencion de problemas virales',
     'No hay cura quimica para los virus: retirar la planta infectada, controlar los vectores (pulgones y mosca blanca) y vigilar el cultivo durante 15 dias.',
     2, 2, 1, 3, 'Manual interno de manejo fitosanitario', '2026-11-07', 'VALIDADO'),
    (5, 'Revision de la calidad del dataset PlantVillage',
     'Pendiente de revisar la distribucion de clases por conjunto y la presencia de imagenes con dano menor al umbral de deteccion.',
     3, 3, 3, 1, 'Metadatos del dataset', '2026-11-06', 'BORRADOR');
