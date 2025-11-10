import sqlite3
import re
import bcrypt
from app.db.connection import get_connection
from app.repositories.users_repo import insert_user, find_by_email, find_by_username


_current_user = None

_ZW_CHARS_RE = re.compile(r"[\u200B\u200C\u200D\uFEFF]")
_CTRL_CHARS_RE = re.compile(r"[\u0000-\u001F\u007F]")

def _hash_password(password):
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")

def get_current_user():
    return _current_user

def logout():
    global _current_user
    _current_user = None

def _check_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

# def login(email, password):
#     global _current_user
#     user = find_by_email(email.lower())
#     if not user:
#         raise ValueError("Нет пользователя с такой почтой")
#     user_id, email, username, password_hash = user
#     if _check_password(password, password_hash):
#         _current_user = {"id": user_id, "email": email, "username": username}
#         return _current_user
#     else:
#         raise ValueError("Неверный пароль")




def _strip_invisible(s):
    if s is None:
        return ""
    s = _ZW_CHARS_RE.sub("", s)
    s = _CTRL_CHARS_RE.sub("", s)
    return s

def _normalize_email(email):
    s =_strip_invisible(email).strip().lower()
    if " " in s:
        raise ValueError("E-mail не должен содержать пробелы")
    return s

def _normalize_username(username):
    s = _strip_invisible(username or "").strip()
    if not s:
        raise ValueError("Имя пользователя не может быть пустым")
    return s

def validate_email_basic(email):
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ValueError("Введите корректный e-mail")

def validate_password(password, min_len = 6):
    if password is None:
        raise ValueError("Введите пароль")
    p = password.strip()
    if len(p) < min_len:
        raise ValueError(f"Пароль не меньше {min_len} символов")
    if not p or p.isspace():
        raise ValueError("Пароль не может состоять только из пробелов")

def login(email_or_username: str, password: str):
    identifier = (email_or_username or "").strip()
    user_row = None

    # сначала пробуем по email
    if "@" in identifier:
        user_row = find_by_email(_normalize_email(identifier))
    # иначе по username
    if user_row is None:
        user_row = find_by_username(_normalize_username(identifier))

    if not user_row:
        raise ValueError("Неверный логин или пароль")

    # Извлекаем поля
    try:
        user_id = user_row["id"]
        email = user_row["email"]
        username = user_row["username"]
        pwd_hash = user_row["password_hash"]
        is_admin = int(user_row["is_admin"] or 0)
    except (TypeError, KeyError):
        user_id, email, username, pwd_hash, is_admin = user_row

    if not bcrypt.checkpw(password.encode("utf-8"), pwd_hash.encode("utf-8")):
        raise ValueError("Неверный логин или пароль")

    global _current_user
    _current_user = {
        "id": user_id,
        "email": email,
        "username": username,
        "is_admin": is_admin,
    }

def create_user(email, username, password, password_confirm, *, auto_login: bool = True):
    email_n = _normalize_email(email)
    username_n = _normalize_username(username)
    password = (password or "").strip()
    password_confirm = (password_confirm or "").strip()

    if not all([email_n, username_n, password, password_confirm]):
        raise ValueError("Заполните все поля")
    if password != password_confirm:
        raise ValueError("Пароли не совпадают")
    validate_email_basic(email_n)
    validate_password(password, min_len=6)

    if find_by_email(email_n) is not None:
        raise ValueError("Учётная запись уже существует")
    if find_by_username(username_n) is not None:
        raise ValueError("Учётная запись уже существует")

    password_hash = _hash_password(password)
    try:
        user_id = insert_user(email_n, username_n, password_hash)
    except sqlite3.IntegrityError as e:
        msg = str(e).lower()
        if "email" in msg or "username" in msg or "unique" in msg:
            raise ValueError("Учётная запись уже существует")
        raise ValueError("Ошибка базы данных при создании пользователя")

    global _current_user
    if auto_login:
        _current_user = {"id": user_id, "email": email_n, "username": username_n,  "is_admin": 0}
        return _current_user
    else:
        _current_user = None
        return True
