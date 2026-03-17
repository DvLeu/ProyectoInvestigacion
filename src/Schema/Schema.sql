-- Base de datos para control de asistencia escolar
CREATE DATABASE IF NOT EXISTS asistencia_automation
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE asistencia_automation;

-- Tabla usuarios
CREATE TABLE usuarios (
    id_usuario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100) NULL,
    matricula VARCHAR(30) NOT NULL UNIQUE,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tabla tarjetas_nfc
CREATE TABLE tarjetas_nfc (
    id_tarjeta INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(50) NOT NULL UNIQUE,
    id_usuario INT UNSIGNED NOT NULL,
    activa TINYINT(1) NOT NULL DEFAULT 1,
    fecha_alta DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tarjetas_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Tabla salones
CREATE TABLE salones (
    id_salon INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(150) NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tabla registros_acceso
CREATE TABLE registros_acceso (
    id_registro BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNSIGNED NOT NULL,
    id_tarjeta INT UNSIGNED NOT NULL,
    id_salon INT UNSIGNED NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_evento ENUM('ENTRADA', 'SALIDA') NOT NULL,
    origen VARCHAR(50) NULL,
    observacion VARCHAR(255) NULL,
    CONSTRAINT fk_registros_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_registros_tarjeta
        FOREIGN KEY (id_tarjeta)
        REFERENCES tarjetas_nfc(id_tarjeta)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_registros_salon
        FOREIGN KEY (id_salon)
        REFERENCES salones(id_salon)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Índices
CREATE INDEX idx_tarjetas_uid ON tarjetas_nfc(uid);
CREATE INDEX idx_registros_fecha_hora ON registros_acceso(fecha_hora);
CREATE INDEX idx_registros_usuario_fecha ON registros_acceso(id_usuario, fecha_hora);
CREATE INDEX idx_registros_tarjetas_fecha ON registros_acceso(id_tarjeta, fecha_hora);
CREATE INDEX idx_registros_salon_fecha ON registros_acceso(id_salon, fecha_hora);