import os.path

from PyQt6.QtGui import QPixmap

import app.config
from app.config import PLACEHOLDERS, BASE_DIR
from  app.repositories.books_repo import fetch_books
from app.repositories.books_repo import get_book_by_id

TAG_MAP = {
    "биография": "Biography",
    "бизнес": "Business",
    "финансы": "Finance",
    "общее": "Generic",
    "история": "History",
    "психология": "Psychology",
    "наука": "Science",
    "технологии": "Technology"
}

def _resolve_cover_path(path_db, tag):

    if path_db:
        full_path = os.path.join(BASE_DIR, path_db)
        if os.path.exists(full_path):
            return full_path

    if tag:
        key = tag.lower()
        mapped = TAG_MAP.get(key)
        if mapped:
            cand = os.path.join(PLACEHOLDERS, f"{mapped}_placeholder.svg")
            if os.path.exists(cand):
                return cand

    return os.path.join(PLACEHOLDERS, 'Generic_placeholder.svg')


def get_books(tag = None, q = None, limit = 50, offset = 0):
    rows = fetch_books(tag, q, limit, offset)
    print(f"rows = {rows}")
    books = []
    for r in rows:

        tags_list = [t.strip() for t in (r.get("tags") or "").split(",") if t.strip()]
        primary_tag = tags_list[0] if tags_list else None

        cover_path = _resolve_cover_path(r.get('cover'), primary_tag)
        px = QPixmap(cover_path)

        books.append({
            "id": r["id"],
            "title": r["title"],
            "author": r["author"],
            "description": r["description"],
            "tags": tags_list,
            "cover_pixmap": px
        })

    return books

def get_book_details(book_id):
    r = get_book_by_id(book_id)
    if not r:
        raise ValueError("Книга не найдена")

    tags_list = [t.strip() for t in (r.get("tags") or "").split(",") if t.strip()]
    primary_tag = tags_list[0] if tags_list else None

    cover_path = _resolve_cover_path(r.get("cover"), primary_tag)
    px = QPixmap(cover_path)

    return {
        "id": r["id"],
        "title": r["title"],
        "author": r["author"],
        "description": r["description"],
        "tags": tags_list,
        "cover_pixmap": px,
    }