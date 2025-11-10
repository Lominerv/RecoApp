

from app.db.connection import get_connection

def upsert_rating(user_id, book_id, rating):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO ratings(user_id, book_id, rating)
        VALUES (?, ?, ?)
        ON CONFLICT (user_id, book_id) DO UPDATE
        SET rating = excluded.rating,
            rated_at = CURRENT_TIMESTAMP
        """,
        (user_id, book_id, rating),
    )
    conn.commit()
    conn.close()

def get_user_book_rating(user_id, book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT rating FROM ratings WHERE user_id = ? AND book_id = ?",
        (user_id, book_id),
    )
    row = cur.fetchone()
    conn.close()
    return int(row[0]) if row is not None else None

def delete_rating(user_id, book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM ratings WHERE user_id = ? AND book_id = ?",
        (user_id, book_id),
    )
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted


def get_book_avg_rating(book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT AVG(rating) FROM ratings WHERE book_id = ?", (book_id, ))
    row = cur.fetchone()
    conn.close()
    return float(row[0]) if row and row[0] is not None else 0.0


def list_user_rated_book_ids(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT book_id FROM ratings WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [int(r[0]) for r in rows]
