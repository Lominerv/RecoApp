from app.db.connection import get_connection

def insert_user(email, username, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, username, password_hash) VALUES (?, ? ,?)",
        (email, username, password_hash)
    )
    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return user_id

def find_by_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, email, username, password_hash, is_admin FROM users WHERE email = ?",
        (email,)
    )
    row = cur.fetchone()
    conn.close()
    return row

def find_by_username(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, email, username, password_hash, is_admin FROM users WHERE username = ?",
        (username,)
    )

    row = cur.fetchone()
    conn.close()
    return row


def count_users() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    n = cur.fetchone()[0] or 0
    conn.close()
    return int(n)