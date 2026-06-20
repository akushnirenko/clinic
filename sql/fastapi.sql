-- ============================================================================
-- СКРИПТ ИНИЦИАЛИЗАЦИИ БАЗЫ ДАННЫХ КЛИНИКИ (8 ТАБЛИЦ)
-- СУБД: PostgreSQL
-- ============================================================================

-- Удаление старых объектов для возможности перезапуска скрипта
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS referrals CASCADE;
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS doctor_schedules CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS doctors CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS specialties CASCADE;

DROP TYPE IF EXISTS appointment_status CASCADE;

-- ============================================================================
-- 1. СОЗДАНИЕ ТАБЛИЦ СПРАВОЧНИКОВ И ПОЛЬЗОВАТЕЛЕЙ
-- ============================================================================

-- 1. Специализации врачей
CREATE TABLE specialties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Учетные записи (Родители)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

-- 3. Врачи
CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    specialty_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    phone VARCHAR(20),
    FOREIGN KEY (specialty_id) REFERENCES specialties(id) ON DELETE RESTRICT
);

-- 4. Пациенты (Дети)
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    snils VARCHAR(20) UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================================
-- 2. СОЗДАНИЕ ТАБЛИЦ РАСПИСАНИЯ И ЗАПИСЕЙ
-- ============================================================================

-- 5. График работы врачей (шаблон недели)
CREATE TABLE doctor_schedules (
    id SERIAL PRIMARY KEY,
    doctor_id INT NOT NULL,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 1 AND 7), -- 1 - Пн, 7 - Вс
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_duration INT NOT NULL DEFAULT 20, -- Длительность слота в минутах
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    CHECK (start_time < end_time)
);

-- Кастомный тип статуса для записей
CREATE TYPE appointment_status AS ENUM ('scheduled', 'completed', 'canceled');

-- 6. Записи на прием
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status appointment_status NOT NULL DEFAULT 'scheduled',
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    
    -- ЗАЩИТА ОТ ДВОЙНОЙ ЗАПИСИ НА ОДИН СЛОТ К ОДНОМУ ВРАЧУ
    CONSTRAINT unique_doctor_time_slot UNIQUE (doctor_id, appointment_date, appointment_time)
);

-- ============================================================================
-- 3. СОЗДАНИЕ МЕДИЦИНСКИХ ТАБЛИЦ
-- ============================================================================

-- 7. Направления к узким специалистам
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    from_doctor_id INT NOT NULL,
    target_specialty_id INT NOT NULL,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (from_doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT,
    FOREIGN KEY (target_specialty_id) REFERENCES specialties(id) ON DELETE RESTRICT
);

-- 8. Медицинская карта (История приемов)
CREATE TABLE medical_records (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_id INT NULL, -- NULL разрешен, если пациент пришел без записи
    visit_date DATE NOT NULL DEFAULT CURRENT_DATE,
    complaints TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    treatment_plan TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
);

-- Создание индексов для ускорения выборок
CREATE INDEX idx_appointments_date ON appointments(doctor_id, appointment_date);
CREATE INDEX idx_medical_records_patient ON medical_records(patient_id);


-- ============================================================================
-- 4. НАПОЛНЕНИЕ ТЕСТОВЫМИ ДАННЫМИ (DML)
-- ============================================================================

-- 4 базовые специальности
INSERT INTO specialties (name) VALUES 
('Педиатр'), ('Отоларинголог (ЛОР)'), ('Детский хирург'), ('Офтальмолог');

-- 10 Врачей
INSERT INTO doctors (specialty_id, first_name, last_name, room_number, phone) VALUES
(1, 'Иван', 'Иванов', '101', '+79991112233'),
(1, 'Анна', 'Петрова', '102', '+79991112234'),
(1, 'Мария', 'Сидорова', '103', '+79991112235'),
(1, 'Елена', 'Кузнецова', '104', '+79991112236'),
(2, 'Сергей', 'Попов', '201', '+79992223344'),
(2, 'Ольга', 'Смирнова', '202', '+79992223345'),
(3, 'Дмитрий', 'Васильев', '301', '+79993334455'),
(3, 'Алексей', 'Федоров', '302', '+79993334456'),
(4, 'Наталья', 'Соколова', '401', '+79994445566'),
(4, 'Татьяна', 'Морозова', '402', '+79994445567');

-- 5 Пользователей (Родителей)
INSERT INTO users (email, password_hash, phone) VALUES
('parent1@example.com', 'hash_pass_1', '+79001234561'),
('parent2@example.com', 'hash_pass_2', '+79001234562'),
('parent3@example.com', 'hash_pass_3', '+79001234563'),
('parent4@example.com', 'hash_pass_4', '+79001234564'),
('parent5@example.com', 'hash_pass_5', '+79001234565');

-- 20 Пациентов (Детей), распределенных по родителям
INSERT INTO patients (user_id, first_name, last_name, birth_date, snils) VALUES
(1, 'Александр', 'Иванов', '2018-05-12', '111-222-333 41'),
(1, 'Мария', 'Иванова', '2020-09-22', '111-222-333 42'),
(1, 'Дмитрий', 'Иванов', '2022-01-15', '111-222-333 43'),
(1, 'Елена', 'Иванова', '2015-11-30', '111-222-333 44'),
(2, 'Максим', 'Петров', '2017-03-05', '222-333-444 51'),
(2, 'Ольга', 'Петрова', '2019-07-19', '222-333-444 52'),
(2, 'Артем', 'Петров', '2021-12-01', '222-333-444 53'),
(2, 'Анна', 'Петрова', '2016-04-25', '222-333-444 54'),
(3, 'Кирилл', 'Сидоров', '2018-08-14', '333-444-555 61'),
(3, 'София', 'Сидорова', '2020-10-05', '333-444-555 62'),
(3, 'Илья', 'Сидоров', '2023-02-20', '333-444-555 63'),
(3, 'Дарья', 'Сидорова', '2014-06-11', '333-444-555 64'),
(4, 'Никита', 'Кузнецов', '2017-01-28', '444-555-666 71'),
(4, 'Полина', 'Кузнецова', '2019-05-17', '444-555-666 72'),
(4, 'Егор', 'Кузнецов', '2021-09-09', '444-555-666 73'),
(4, 'Алиса', 'Кузнецова', '2015-02-14', '444-555-666 74'),
(5, 'Даниил', 'Попов', '2018-12-25', '555-666-777 81'),
(5, 'Вероника', 'Попова', '2020-04-03', '555-666-777 82'),
(5, 'Матвей', 'Попов', '2022-07-29', '555-666-777 83'),
(5, 'Ксения', 'Попова', '2016-08-18', '555-666-777 84');

-- Расписание врачей (Пн-Пт смены по 6 часов)
INSERT INTO doctor_schedules (doctor_id, day_of_week, start_time, end_time, slot_duration) VALUES
(1, 1, '08:00:00', '14:00:00', 20), (1, 2, '14:00:00', '20:00:00', 20),
(2, 1, '14:00:00', '20:00:00', 20), (2, 2, '08:00:00', '14:00:00', 20),
(3, 3, '08:00:00', '14:00:00', 20), (3, 4, '14:00:00', '20:00:00', 20),
(4, 3, '14:00:00', '20:00:00', 20), (4, 4, '08:00:00', '14:00:00', 20),
(5, 1, '09:00:00', '15:00:00', 20), (5, 3, '09:00:00', '15:00:00', 20),
(6, 2, '09:00:00', '15:00:00', 20), (6, 4, '09:00:00', '15:00:00', 20),
(7, 1, '10:00:00', '16:00:00', 20), (7, 5, '10:00:00', '16:00:00', 20),
(8, 2, '10:00:00', '16:00:00', 20), (8, 5, '10:00:00', '16:00:00', 20),
(9, 3, '08:30:00', '14:30:00', 20), (9, 5, '08:30:00', '14:30:00', 20),
(10, 4, '11:00:00', '17:00:00', 20), (10, 5, '11:00:00', '17:00:00', 20);

-- Записи на прием (Прошедшие и предстоящие)
INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, appointment_time, status) VALUES
(1, 1, 1, '2026-06-15', '08:00:00', 'completed'),
(2, 5, 1, '2026-06-15', '08:20:00', 'completed'),
(3, 9, 5, '2026-06-15', '09:00:00', 'completed'), -- Пример "живой очереди" (запись создана при приёме)
(4, 13, 7, '2026-06-15', '10:00:00', 'completed'),
(5, 2, 1, '2026-06-22', '08:00:00', 'scheduled'),
(6, 6, 1, '2026-06-22', '08:20:00', 'scheduled'),
(7, 10, 2, '2026-06-23', '08:00:00', 'scheduled'),
(8, 14, 6, '2026-06-23', '09:20:00', 'scheduled'),
(9, 18, 9, '2026-06-24', '08:30:00', 'scheduled'),
(10, 4, 10, '2026-06-25', '11:00:00', 'scheduled');

-- Синхронизация генератора id для будущих инсертов через приложение
SELECT setval(pg_get_serial_sequence('appointments', 'id'), COALESCE(MAX(id), 1)) FROM appointments;

-- Записи в электронную медицинскую карту
INSERT INTO medical_records (patient_id, doctor_id, appointment_id, visit_date, complaints, diagnosis, treatment_plan) VALUES
(1, 1, 1, '2026-06-15', 'Повышенная температура, насморк.', 'ОРИЗ', 'Обильное питье, домашний режим.'),
(5, 1, 2, '2026-06-15', 'Плановый осмотр перед садом.', 'Здоров', 'Разрешено посещение детского сада.'),
(9, 5, 3, '2026-06-15', 'Острая боль в левом ухе.', 'Острый средний отит', 'Капли Отипакс, повторный осмотр через 3 дня.'),
(13, 7, 4, '2026-06-15', 'Боль в правом колене после падения.', 'Ушиб мягких тканей', 'Холод локально, ограничение физических нагрузок.');

