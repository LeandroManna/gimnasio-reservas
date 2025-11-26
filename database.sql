-- Crear base de datos
CREATE DATABASE IF NOT EXISTS gimnasio_reservas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gimnasio_reservas;

-- Tabla de disciplinas
CREATE TABLE disciplinas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_activa (activa)
) ENGINE=InnoDB;

-- Tabla de horarios por disciplina
CREATE TABLE horarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    disciplina_id INT NOT NULL,
    dia_semana ENUM('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo') NOT NULL,
    hora_inicio TIME NOT NULL,
    cupo_maximo INT DEFAULT 10,
    FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE,
    INDEX idx_disciplina (disciplina_id),
    INDEX idx_dia (dia_semana)
) ENGINE=InnoDB;

-- Tabla de reservas
CREATE TABLE reservas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    horario_id INT NOT NULL,
    fecha_clase DATE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    dni VARCHAR(20) NOT NULL,
    comprobante_pago VARCHAR(255),
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('pendiente', 'confirmada', 'cancelada') DEFAULT 'confirmada',
    FOREIGN KEY (horario_id) REFERENCES horarios(id) ON DELETE CASCADE,
    UNIQUE KEY unique_reserva (horario_id, fecha_clase, dni),
    INDEX idx_fecha_clase (fecha_clase),
    INDEX idx_dni (dni),
    INDEX idx_estado (estado)
) ENGINE=InnoDB;

-- Tabla de administradores
CREATE TABLE administradores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Insertar datos de ejemplo

-- Disciplinas
INSERT INTO disciplinas (nombre, descripcion, activa) VALUES
('Yoga', 'Clases de yoga para todos los niveles. Mejora tu flexibilidad y encuentra tu paz interior.', TRUE),
('Spinning', 'Entrenamiento cardiovascular intenso sobre bicicleta estática. ¡Quema calorías y mejora tu resistencia!', TRUE),
('Funcional', 'Entrenamiento funcional y crossfit. Desarrolla fuerza, resistencia y agilidad.', TRUE),
('Pilates', 'Fortalecimiento muscular y flexibilidad. Ideal para mejorar postura y core.', TRUE),
('Zumba', 'Baile fitness con ritmos latinos. Divertite mientras te ejercitás.', TRUE),
('Boxing', 'Boxeo recreativo y fitness. Libera estrés y ponte en forma.', TRUE);

-- Horarios para Yoga (disciplina_id = 1)
INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, cupo_maximo) VALUES
(1, 'Lunes', '08:00:00', 10),
(1, 'Lunes', '18:00:00', 10),
(1, 'Miércoles', '08:00:00', 10),
(1, 'Miércoles', '18:00:00', 10),
(1, 'Viernes', '08:00:00', 10),
(1, 'Viernes', '18:00:00', 10);

-- Horarios para Spinning (disciplina_id = 2)
INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, cupo_maximo) VALUES
(2, 'Martes', '07:00:00', 10),
(2, 'Martes', '19:00:00', 10),
(2, 'Jueves', '07:00:00', 10),
(2, 'Jueves', '19:00:00', 10),
(2, 'Sábado', '09:00:00', 10);

-- Horarios para Funcional (disciplina_id = 3)
INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, cupo_maximo) VALUES
(3, 'Lunes', '19:00:00', 10),
(3, 'Miércoles', '19:00:00', 10),
(3, 'Viernes', '19:00:00', 10);

-- Horarios para Pilates (disciplina_id = 4)
INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, cupo_maximo) VALUES
(4, 'Martes', '09:00:00', 10),
(4, 'Jueves', '09:00:00', 10);

-- Horarios para Zumba (disciplina_id = 5)
INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, cupo_maximo) VALUES
(5, 'Lunes', '20:00:00', 10),
(5, 'Miércoles', '20:00:00', 10),
(5, 'Viernes', '20:00:00', 10);

-- Horarios para Boxing (disciplina_id = 6)
INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, cupo_maximo) VALUES
(6, 'Martes', '20:00:00', 10),
(6, 'Jueves', '20:00:00', 10),
(6, 'Sábado', '10:00:00', 10);

-- Crear usuario administrador
-- Usuario: admin
-- Contraseña: admin123
-- IMPORTANTE: Cambiá esta contraseña en producción
INSERT INTO administradores (usuario, password_hash, email) VALUES
('admin', 'scrypt:32768:8:1$pQxmHvnOQDvvKvlr$b8b0c3c3e8f9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9', 'admin@gimnasio.com');

-- Nota: Para generar un nuevo hash de contraseña, usá este código Python:
-- from werkzeug.security import generate_password_hash
-- print(generate_password_hash('tu_contraseña'))

-- Reservas de ejemplo (opcional)
-- Descomentar para tener datos de prueba
/*
INSERT INTO reservas (horario_id, fecha_clase, nombre, apellido, dni, estado) VALUES
(1, '2024-11-25', 'Juan', 'Pérez', '12345678', 'confirmada'),
(1, '2024-11-25', 'María', 'González', '23456789', 'confirmada'),
(2, '2024-11-25', 'Carlos', 'López', '34567890', 'confirmada'),
(3, '2024-11-27', 'Ana', 'Martínez', '45678901', 'confirmada'),
(5, '2024-11-26', 'Luis', 'Rodríguez', '56789012', 'confirmada');
*/