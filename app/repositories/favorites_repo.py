from app.db.connection import get_connection

def is_favorite(user_id, book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM favorites WHERE user_id = ? AND book_id = ?",
        (user_id, book_id),
    )
    row = cur.fetchone()
    conn.close()
    return row

def add_favorite(user_id, book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO favorites (user_id, book_id) VALUES (?, ?)",
        (user_id, book_id),
    )
    conn.commit()
    conn.close()

def remove_favorite(user_id, book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM favorites WHERE user_id = ? AND book_id = ?",
        (user_id, book_id),
    )
    conn.commit()
    conn.close()

def list_favorite_book_ids(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT book_id FROM favorites WHERE user_id = ? ORDER BY added_at DESC",
        (user_id, ),
    )
    books = [r[0] for r in cur.fetchall()]
    conn.close()
    return books
