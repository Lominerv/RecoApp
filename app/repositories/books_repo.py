from app.db.connection import get_connection


def fetch_books(tag: str | None = None, title_like = None, limit: int = 50, offset: int = 0):
    conn = get_connection()
    cur = conn.cursor()


    base_sql = """
        SELECT
            b.id, b.title, b.author, b.description, b.cover,
            COALESCE(GROUP_CONCAT(t.name, ', '), '') AS tags
        FROM books b
        LEFT JOIN book_tags bt ON b.id = bt.book_id
        LEFT JOIN tags t ON bt.tag_id = t.id 
    """

    sql_where_list = []
    params = []
    where_sql = ""
    if tag:
        sql_where_list.append("""
            EXISTS (
                SELECT 1
                FROM book_tags bt2
                JOIN tags t2 ON t2.id = bt2.tag_id
                WHERE bt2.book_id = b.id AND t2.name = ?
        )
        """)
        params.append(tag)


    if title_like:
        sql_where_list.append("LOWER(b.title) LIKE LOWER(?)")
        params.append(f"%{title_like.strip()}%")

    where_sql = ""
    if sql_where_list:
        where_sql = " WHERE " + " AND ".join(sql_where_list)

    tail_sql ="""
        GROUP BY b.id
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    cur.execute(base_sql + where_sql + tail_sql, tuple(params))
    rows = cur.fetchall()
    conn.close()

    return [{"id": r[0], "title": r[1], "author": r[2], "description": r[3], "cover": r[4], "tags": r[5], }
            for r in rows]

def count_books():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM books")
    n = cur.fetchone()[0] or 0
    conn.close()
    return int(n)

def delete_book_by_title(title):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE title = ?", (title.strip(), ))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted

def insert_book(title, author, description, cover_relpath):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO books (title, author, description, cover)
        VALUES (?, ?, ?, ?)
    """, (title, author, description, cover_relpath))
    book_id = cur.lastrowid
    conn.commit()
    conn.close()
    return book_id

def get_book_by_id(book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            b.id, b.title, b.author, b.description, b.cover,
            COALESCE(GROUP_CONCAT(t.name, ', '), '') AS tags
        FROM books b
        LEFT JOIN book_tags bt ON b.id = bt.book_id
        LEFT JOIN tags t ON bt.tag_id = t.id
        WHERE b.id = ?
        GROUP BY b.id
        LIMIT 1
    """, (book_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "title": row[1], "author": row[2], "description": row[3], "cover": row[4], "tags": row[5],}