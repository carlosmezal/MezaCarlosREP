───────────────────────
CREATE TABLE estudiantes (
    id         SERIAL PRIMARY KEY,
    nombre     VARCHAR(50)  NOT NULL,
    apellido   VARCHAR(50)  NOT NULL,
    carrera    VARCHAR(60)  NOT NULL,
    semestre   INTEGER      CHECK (semestre BETWEEN 1 AND 12),
    promedio   NUMERIC(4,2) CHECK (promedio BETWEEN 0 AND 10),
    correo     VARCHAR(100) UNIQUE,
    ciudad     VARCHAR(60),
    edad       INTEGER      CHECK (edad BETWEEN 15 AND 60),
    beca       BOOLEAN      DEFAULT FALSE,
    created_at TIMESTAMP    DEFAULT NOW()
);

INSERT INTO estudiantes (nombre, apellido, carrera, semestre, promedio, correo, ciudad, edad, beca) VALUES
('Ana',       'García',    'Ingeniería en Sistemas', 5, 9.2,  'ana.garcia@escom.ipn.mx',    'CDMX',              21, TRUE),
('Carlos',    'Martínez',  'Ciencia de Datos',       3, 8.7,  'carlos.mtz@escom.ipn.mx',    'Ecatepec',          20, FALSE),
('Lucía',     'Hernández', 'Ingeniería en Sistemas', 7, 9.8,  'lucia.hdz@escom.ipn.mx',     'CDMX',              23, TRUE),
('Miguel',    'López',     'Ciberseguridad',         1, 7.5,  'miguel.lop@escom.ipn.mx',    'Naucalpan',         19, FALSE),
('Sofía',     'Ramírez',   'Ciencia de Datos',       5, 9.1,  'sofia.ram@escom.ipn.mx',     'Tlalnepantla',      22, TRUE),
('Diego',     'Torres',    'Ingeniería en Sistemas', 3, 8.3,  'diego.tor@escom.ipn.mx',     'CDMX',              20, FALSE),
('Valentina', 'Flores',    'Ciberseguridad',         7, 9.5,  'vale.flo@escom.ipn.mx',      'Iztapalapa',        23, TRUE),
('Andrés',    'Ruiz',      'Ciencia de Datos',       1, 7.9,  'andres.rui@escom.ipn.mx',    'CDMX',              19, FALSE),
('Camila',    'Morales',   'Ingeniería en Sistemas', 5, 8.6,  'camila.mor@escom.ipn.mx',    'Gustavo A. Madero', 21, FALSE),
('Luis',      'Jiménez',   'Ciberseguridad',         3, 9.0,  'luis.jim@escom.ipn.mx',      'Azcapotzalco',      20, TRUE),
('Mariana',   'Díaz',      'Ciencia de Datos',       7, 9.4,  'mariana.diaz@escom.ipn.mx',  'CDMX',              23, TRUE),
('Roberto',   'Pérez',     'Ingeniería en Sistemas', 1, 6.8,  'roberto.per@escom.ipn.mx',   'Nezahualcóyotl',    19, FALSE),
('Isabella',  'Sánchez',   'Ciberseguridad',         5, 8.9,  'isa.san@escom.ipn.mx',       'CDMX',              22, FALSE),
('Fernando',  'Castro',    'Ciencia de Datos',       3, 7.2,  'fer.cas@escom.ipn.mx',       'Tlalpan',           20, FALSE),
('Daniela',   'Reyes',     'Ingeniería en Sistemas', 7, 9.7,  'dani.rey@escom.ipn.mx',      'Coyoacán',          24, TRUE);

-- ──────────────────────────────────────────────────────────────
--  TABLA: profesores
-- ──────────────────────────────────────────────────────────────
CREATE TABLE profesores (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(50)  NOT NULL,
    apellido        VARCHAR(50)  NOT NULL,
    departamento    VARCHAR(60),
    grado           VARCHAR(20)  CHECK (grado IN ('Licenciatura','Maestría','Doctorado')),
    anos_servicio   INTEGER      DEFAULT 0,
    salario_mensual NUMERIC(10,2),
    correo          VARCHAR(100) UNIQUE,
    activo          BOOLEAN      DEFAULT TRUE
);

INSERT INTO profesores (nombre, apellido, departamento, grado, anos_servicio, salario_mensual, correo, activo) VALUES
('Jorge',    'Mendoza',    'Sistemas',       'Doctorado',   15, 28500.00, 'j.mendoza@ipn.mx',    TRUE),
('Patricia', 'Villanueva', 'Matemáticas',    'Maestría',     8, 22000.00, 'p.villanueva@ipn.mx', TRUE),
('Ricardo',  'Fuentes',    'Ciberseguridad', 'Doctorado',   20, 32000.00, 'r.fuentes@ipn.mx',    TRUE),
('Elena',    'Castillo',   'Ciencia de Datos','Maestría',    5, 21000.00, 'e.castillo@ipn.mx',   TRUE),
('Manuel',   'Vargas',     'Sistemas',       'Licenciatura', 3, 18000.00, 'm.vargas@ipn.mx',     FALSE),
('Adriana',  'Rojas',      'Matemáticas',    'Doctorado',   12, 29000.00, 'a.rojas@ipn.mx',      TRUE),
('Héctor',   'Guerrero',   'Ciberseguridad', 'Maestría',     7, 23500.00, 'h.guerrero@ipn.mx',   TRUE),
('Laura',    'Salinas',    'Ciencia de Datos','Doctorado',  18, 31000.00, 'l.salinas@ipn.mx',    TRUE);

-- ──────────────────────────────────────────────────────────────
--  CONSULTAS DE PRUEBA (cópialas en la app)
-- ──────────────────────────────────────────────────────────────
-- Todos los estudiantes:
--   SELECT * FROM estudiantes;

-- Estudiantes con beca ordenados por promedio:
--   SELECT nombre, apellido, carrera, promedio FROM estudiantes WHERE beca = TRUE ORDER BY promedio DESC;

-- Promedio por carrera:
--   SELECT carrera, COUNT(*) AS total, ROUND(AVG(promedio),2) AS promedio_carrera FROM estudiantes GROUP BY carrera ORDER BY promedio_carrera DESC;

-- Join estudiantes con info útil:
--   SELECT nombre, apellido, carrera, semestre, promedio, ciudad FROM estudiantes ORDER BY semestre, promedio DESC;

-- Todos los profesores activos:
--   SELECT * FROM profesores WHERE activo = TRUE;
