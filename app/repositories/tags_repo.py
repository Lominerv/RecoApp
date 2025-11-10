from app.db.connection import get_connection

def get_or_create_tag_id(name):
    n = (name or "").strip().lower()
    if not n:
        raise ValueError("Пустой тег")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM tags WHERE name = ?", (n, ))
    row = cur.fetchone()
    if row:
        tid = row[0]
    else:
        cur.execute("INSERT INTO tags(name) VALUES (?)", (n, ))
        tid = cur.lastrowid
        conn.commit()
    conn.close()
    return tid


def link_book_tags(book_id, tag_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO book_tags (book_id, tag_id) VALUES (?, ?)", (book_id, tag_id))
    conn.commit()
    conn.close()
