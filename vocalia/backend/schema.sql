-- Ejecutar solo si faltan tablas. Usa IF NOT EXISTS para no tocar lo que ya tienes.
CREATE TABLE IF NOT EXISTS usuarios (
  id_usuario SERIAL PRIMARY KEY, nombre TEXT, correo TEXT UNIQUE,
  contrasena TEXT, rol TEXT, colegio TEXT, grado TEXT);
CREATE TABLE IF NOT EXISTS evaluaciones (
  id_evaluacion SERIAL PRIMARY KEY, id_usuario INT REFERENCES usuarios, fecha TIMESTAMP, estado TEXT);
CREATE TABLE IF NOT EXISTS preguntas (
  id_pregunta SERIAL PRIMARY KEY, enunciado TEXT);
CREATE TABLE IF NOT EXISTS respuestas (
  id_respuesta SERIAL PRIMARY KEY, id_evaluacion INT REFERENCES evaluaciones,
  id_pregunta INT REFERENCES preguntas, valor TEXT);
CREATE TABLE IF NOT EXISTS instituciones_educativas (
  id_institucion SERIAL PRIMARY KEY, nombre TEXT);
CREATE TABLE IF NOT EXISTS carreras (
  id_carrera SERIAL PRIMARY KEY, nombre TEXT, area_conocimiento TEXT,
  id_institucion INT REFERENCES instituciones_educativas);
CREATE TABLE IF NOT EXISTS perfiles_vocacionales (
  id_perfil SERIAL PRIMARY KEY, id_usuario INT REFERENCES usuarios, resumen_personalidad TEXT);

-- Preguntas del test (escala 1 a 5)
INSERT INTO preguntas (id_pregunta, enunciado) VALUES
(1,'Me gusta resolver problemas de lógica, números o programación'),
(2,'Disfruto ayudar y escuchar a otras personas'),
(3,'Me atrae crear cosas: diseño, arte, música o escritura'),
(4,'Me interesa saber cómo funcionan las máquinas y la tecnología'),
(5,'Me gusta liderar equipos y organizar proyectos'),
(6,'Me interesan la biología, la salud y el cuidado de la vida'),
(7,'Me gusta investigar y experimentar hasta entender algo'),
(8,'Me veo creando mi propio negocio')
ON CONFLICT (id_pregunta) DO NOTHING;

-- Datos de ejemplo (reemplaza por la oferta real de Chiclayo)
INSERT INTO instituciones_educativas (id_institucion, nombre) VALUES
(1,'Universidad Señor de Sipán'),(2,'Universidad Nacional Pedro Ruiz Gallo'),(3,'Universidad Católica Santo Toribio de Mogrovejo')
ON CONFLICT (id_institucion) DO NOTHING;
INSERT INTO carreras (nombre, area_conocimiento, id_institucion) VALUES
('Ingeniería de Sistemas','Tecnología',1),('Psicología','Ciencias de la Salud',1),
('Medicina Humana','Ciencias de la Salud',2),('Administración de Empresas','Negocios',3),
('Arquitectura','Diseño y Construcción',3),('Ingeniería Civil','Ingeniería',2);
