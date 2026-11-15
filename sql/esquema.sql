-- Semana 15 - Ingenieria del conocimiento: base de conocimiento de PlantAI.
-- Define las cinco tablas del repositorio de conocimiento y sus relaciones.
-- Este archivo SOLO define la estructura; los datos de ejemplo van en datos.sql.

PRAGMA foreign_keys = ON;

-- Dominio: area tematica que agrupa el conocimiento (la columna vertebral).
CREATE TABLE IF NOT EXISTS dominio (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

-- Aplicacion: sistema o proceso donde se usa el conocimiento del dominio.
CREATE TABLE IF NOT EXISTS aplicacion (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    dominio_id INTEGER NOT NULL REFERENCES dominio(id)
);

-- Experto: persona (recurso humano) responsable de revisar y mantener el
-- contenido. El proyecto no implementa autenticacion: modela el rol.
CREATE TABLE IF NOT EXISTS experto (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    cargo TEXT NOT NULL
);

-- Herramienta: medio de captura, almacenamiento o consulta del conocimiento.
-- La herramienta no es el conocimiento: es el soporte para gestionarlo.
CREATE TABLE IF NOT EXISTS herramienta (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    finalidad TEXT NOT NULL
);

-- Articulo: el contenido util. Une contexto (dominio, aplicacion),
-- responsable (experto), soporte (herramienta), procedencia (fuente) y
-- estado editorial. Siempre nace como BORRADOR.
CREATE TABLE IF NOT EXISTS articulo (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    contenido TEXT NOT NULL,
    dominio_id INTEGER NOT NULL REFERENCES dominio(id),
    aplicacion_id INTEGER REFERENCES aplicacion(id),
    experto_id INTEGER NOT NULL REFERENCES experto(id),
    herramienta_id INTEGER REFERENCES herramienta(id),
    fuente TEXT NOT NULL,
    fecha_revision TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'BORRADOR'
        CHECK (estado IN ('BORRADOR', 'VALIDADO')),
    UNIQUE (titulo, dominio_id)
);

-- Indice del patron de consulta mas frecuente: articulos de un dominio.
CREATE INDEX IF NOT EXISTS idx_articulo_dominio_estado
    ON articulo(dominio_id, estado);
