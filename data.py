import sqlite3

# Подключаемся к базе (файл создастся автоматически)
conn = sqlite3.connect("education.db")
cursor = conn.cursor()

# ======================
# Весь SQL как многострочная строка
# ======================
sql = """
-- Таблица учебных заведений
CREATE TABLE IF NOT EXISTS institutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    duration TEXT,
    price TEXT,
    site TEXT
);

-- Таблица программ/направлений
CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institution_id INTEGER NOT NULL,
    program_name TEXT NOT NULL,
    FOREIGN KEY (institution_id) REFERENCES institutions(id)
);

-- Университеты
INSERT INTO institutions (name, type, duration, price, site) VALUES
('АУЦА', 'university', '4 года (бакалавриат)', '~$5,500 за год (финансовая помощь до 40%)', 'https://auca.kg'),
('КГНУ', 'university', '4 года (бакалавриат)', 'Стоимость зависит от факультета, уточняется на сайте', 'https://ksu.kg/'),
('КТУ "Манас"', 'university', '4 года + 1 год подготовительный', 'Бюджетные и контрактные места', 'https://manas.edu.kg'),
('КГТУ', 'college', '4 года (бакалавриат)', 'Контракт: 34 320–42 900 сом/год', 'https://kstu.kg/');

-- Колледжи
INSERT INTO institutions (name, type, duration, price, site) VALUES
('Инновационный колледж АУЦА', 'college', '~3 года', '$6,000 за год (~523,825 сом)', 'https://tsiauca.kg'),
('Compass College', 'college', '2-3 года (зависит от базы)', '$5,500 за год + задаток 50,000 сом', 'https://compasscollege.org'),
('КГТУ / КГУСТА', 'college', '1 год 10 мес. (после 11 класса), 2 года 10 мес. (после 9 класса)', '25,500-27,000 сом/год', 'https://kstu.kg, https://kgusta.kg');

-- Курсы
INSERT INTO institutions (name, type, duration, price, site) VALUES
('СММ-Менеджер, Видео блогер (IT Club)', 'course', '1 месяц', '20,000 сом', 'https://it-club.kg/course/video-montazh/'),
('2D анимация (LineArt)', 'course', '3-4 месяца', '5,000 сом/мес', 'https://www.instagram.com/lineart_class/'),
('Графический дизайнер (IT Club)', 'course', '1 месяц', '11,000 сом (оплата частями: 6,000 сом каждые 2 недели)', 'https://it-club.kg/course/graficheskij-dizajner/');

-- Программы / направления
-- АУЦА
INSERT INTO programs (institution_id, program_name) VALUES
(1, 'Медиа'), (1, 'Дизайн (графический)'), (1, 'IT');

-- КГНУ
INSERT INTO programs (institution_id, program_name) VALUES
(2, 'Дизайн'), (2, 'Актёрство'), (2, 'Музыка');

-- КТУ "Манас"
INSERT INTO programs (institution_id, program_name) VALUES
(3, 'Живопись'), (3, 'Дизайн (графический)'), (3, 'Музыка'), (3, 'Театр');

-- КГТУ
INSERT INTO programs (institution_id, program_name) VALUES
(4, 'Дизайн'), (4, 'Актёрство'), (4, 'Музыка');

-- Колледжи
-- Инновационный колледж АУЦА
INSERT INTO programs (institution_id, program_name) VALUES
(5, 'Архитектура'), (5, 'Дизайн'), (5, 'IT');

-- Compass College
INSERT INTO programs (institution_id, program_name) VALUES
(6, 'Дизайн (графический)'), (6, 'Дизайн (интерьера)'), (6, 'Дизайн (одежды)'), (6, 'Креативный бизнес'), (6, 'Анимация'), (6, 'IT');

-- КГТУ / КГУСТА
INSERT INTO programs (institution_id, program_name) VALUES
(7, 'Архитектура'), (7, 'Дизайн'), (7, 'IT');

-- Курсы
-- СММ-Менеджер, Видео блогер
INSERT INTO programs (institution_id, program_name) VALUES
(8, 'СММ-Менеджер'), (8, 'Видео блогер');

-- 2D анимация (LineArt)
INSERT INTO programs (institution_id, program_name) VALUES
(9, '2D анимация');

-- Графический дизайнер (IT Club)
INSERT INTO programs (institution_id, program_name) VALUES
(10, 'Дизайн (графический)');
"""

# ======================
# Выполняем SQL
# ======================
cursor.executescript(sql)
conn.commit()
conn.close()
print("База данных успешно создана!")
