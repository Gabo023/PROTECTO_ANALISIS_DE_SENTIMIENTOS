-- Creación de la tabla de Productos
CREATE TABLE IF NOT EXISTS productos (
    id_producto SERIAL PRIMARY KEY,
    nombre_modelo VARCHAR(100) NOT NULL UNIQUE, -- Ej: 'Xiaomi Redmi Note 13', 'Samsung Galaxy A55'
    marca VARCHAR(50) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creación de la tabla de Reseñas
CREATE TABLE IF NOT EXISTS resenas (
    id_opinion SERIAL PRIMARY KEY, -- Control interno incremental
    id_producto INT NOT NULL,
    fecha_publicacion DATE, -- Análisis de tendencias temporales
    calificacion_numerica INT NOT NULL, -- Puntuación original de estrellas (1-5)
    texto_resena TEXT NOT NULL, -- Opinión cruda del usuario
    texto_limpio TEXT, -- Texto normalizado post-preprocesamiento
    polaridad_score NUMERIC(4,3), -- Rango -1.0 a +1.0
    etiqueta_sentimiento VARCHAR(20), -- Positivo, Neutro, Negativo
    fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Restricciones de integridad y validación
    CONSTRAINT fk_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    CONSTRAINT check_estrellas CHECK (calificacion_numerica BETWEEN 1 AND 5),
    CONSTRAINT check_polaridad CHECK (polaridad_score BETWEEN -1.0 AND 1.0)
);