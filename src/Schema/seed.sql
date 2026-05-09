SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

USE asistencia_automation;

INSERT INTO salones (nombre, ubicacion) VALUES
  ('Salón A-101', 'Edificio Principal');

INSERT INTO usuarios (nombre, apellido_paterno, apellido_materno, matricula) VALUES
  ('Néstor Isaac', 'Bello', 'Benítez', 'A2024002'),
  ('Cecilia Yaramith', 'Ibarra', 'Ambrosio', 'A2024003'),
  ('Abraham', 'Bello', 'Benítez', 'A2024004'),
  ('Leslie', 'Mendoza', 'Guadalupe', 'A2024005'),
  ('Gustavo', 'Mendoza', 'Barrón', 'A2024006');

INSERT INTO tarjetas_nfc (uid, id_usuario) VALUES
  ('39105303', 1),
  ('9C675403', 2),
  ('E6EF0F03', 3),
  ('4EF51003', 4),
  ('B9175303', 5);