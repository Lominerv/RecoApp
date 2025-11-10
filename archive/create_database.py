# create_database.py
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "reco_database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# включаем внешние ключи
cur.execute("PRAGMA foreign_keys = ON;")

cur.executescript("""
-- USERS
CREATE TABLE IF NOT EXISTS users(
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT NOT NULL UNIQUE,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    CHECK (email = lower(trim(email)))
);

-- BOOKS
CREATE TABLE IF NOT EXISTS books (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    author      TEXT,
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    cover       TEXT,
    created_at  TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    UNIQUE(title, author)
);

-- TAGS (нормализованные)
CREATE TABLE IF NOT EXISTS tags (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL UNIQUE COLLATE NOCASE,
    CHECK (name = lower(trim(name)))
);

-- BOOK_TAGS (многие↔многим книги↔теги)
CREATE TABLE IF NOT EXISTS book_tags (
    book_id INTEGER NOT NULL,
    tag_id  INTEGER NOT NULL,
    PRIMARY KEY (book_id, tag_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)  REFERENCES tags(id)  ON DELETE CASCADE
);

-- RATINGS
CREATE TABLE IF NOT EXISTS ratings (
    user_id  INTEGER NOT NULL,
    book_id  INTEGER NOT NULL,
    rating   INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    rated_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    PRIMARY KEY (user_id, book_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- FAVORITES
CREATE TABLE IF NOT EXISTS favorites (
    user_id  INTEGER NOT NULL,
    book_id  INTEGER NOT NULL,
    added_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    PRIMARY KEY (user_id, book_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);
""")


cur.executescript("""
INSERT OR IGNORE INTO tags (name) VALUES
 ('биография'),
 ('бизнес'),
 ('финансы'),
 ('история'),
 ('психология'),
 ('наука'),
 ('технологии'),
 ('общее');
 
 
 
INSERT OR IGNORE INTO books (title, author, description, cover) VALUES
 ('1984', 'Джордж Оруэлл', 'Антиутопия о тоталитарном обществе, где за каждым шагом следит Большой Брат.', 'assets/covers/placeholders/Generic_placeholders.svg'),
 ('Сапиенс. Краткая история человечества', 'Юваль Ной Харари', 'Переосмысление истории человека от каменного века до цифровой эпохи.', 'assets/covers/placeholders/History_placeholder.svg'),
 ('Атлант расправил плечи', 'Айн Рэнд', 'Философский роман о свободе, ответственности и силе человеческого разума.', 'assets/covers/placeholders/Business_placeholder.svg'),
 ('Богатый папа, бедный папа', 'Роберт Кийосаки', 'Легендарная книга о финансовой грамотности и мышлении инвестора.', 'assets/covers/placeholders/Finance_placeholders.svg'),
 ('Думай медленно… решай быстро', 'Даниэль Канеман', 'О работе человеческого мышления и ловушках восприятия, которые влияют на решения.', 'assets/covers/placeholders/Psychology_placeholders.svg'),
 ('Краткие ответы на большие вопросы', 'Стивен Хокинг', 'Простое объяснение сложнейших научных загадок вселенной от великого физика.', 'assets/covers/placeholders/Science_placeholders.svg'),
 ('Стив Джобс', 'Уолтер Айзексон', 'Официальная биография создателя Apple, полная открытых признаний и вдохновения.', 'assets/covers/placeholders/Biography_placeholder.svg'),
 ('История государства Российского', 'Николай Карамзин', 'Классический труд о становлении русской государственности и культуры.', 'assets/covers/placeholders/History_placeholder.svg'),
 ('Илон Маск. Tesla, SpaceX и дорога в будущее', 'Эшли Вэнс', 'Биография современного предпринимателя, изменившего представление о технологиях.', 'assets/covers/placeholders/Technology_placeholders.svg'),
 ('7 навыков высокоэффективных людей', 'Стивен Кови', 'Практическое руководство по саморазвитию, лидерству и личной эффективности.', 'assets/covers/placeholders/Business_placeholder.svg');


    -- Связи книг с тегами
INSERT OR IGNORE INTO book_tags (book_id, tag_id)
SELECT b.id, t.id FROM books b
JOIN tags t ON (
   (b.title = '1984' AND t.name = 'общее') OR
   (b.title = 'Сапиенс. Краткая история человечества' AND t.name = 'история') OR
   (b.title = 'Атлант расправил плечи' AND t.name = 'бизнес') OR
   (b.title = 'Богатый папа, бедный папа' AND t.name = 'финансы') OR
   (b.title = 'Думай медленно… решай быстро' AND t.name = 'психология') OR
   (b.title = 'Краткие ответы на большие вопросы' AND t.name = 'наука') OR
   (b.title = 'Стив Джобс' AND t.name = 'биография') OR
   (b.title = 'История государства Российского' AND t.name = 'история') OR
   (b.title = 'Илон Маск. Tesla, SpaceX и дорога в будущее' AND t.name = 'технологии') OR
   (b.title = '7 навыков высокоэффективных людей' AND t.name = 'бизнес')
);
""")




conn.commit()
conn.close()
print("База создана/обновлена.")


