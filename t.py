# app/services/catalog_service.py
import os
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from app.repositories.books_repo import fetch_books

# Базовая папка проекта (подстрой под свой конфиг, если есть assets_path и т.п.)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS = os.path.join(BASE_DIR, "assets")
PLACEHOLDERS = os.path.join(ASSETS, "covers", "placeholders")

def _ensure_pixmap(path: str, w: int, h: int):
    """Возвращает QPixmap нужного размера. SVG и PNG/JPG — единый путь через QIcon."""
    icon = QIcon(path)
    # важно: задаём размер, QIcon сам отрисует в QPixmap
    return icon.pixmap(QSize(w, h))

def _resolve_cover_path(cover_path_from_db: str | None, tag: str | None) -> str:
    """
    Пробуем путь из БД; если файла нет — подбираем плейсхолдер по тегу,
    иначе дефолтный плейсхолдер.
    """
    # Нормализуем относительные пути из БД
    def as_abs(p: str) -> str:
        return p if os.path.isabs(p) else os.path.join(BASE_DIR, p)

    # 1) путь из БД
    if cover_path_from_db:
        abs_path = as_abs(cover_path_from_db)
        if os.path.exists(abs_path):
            return abs_path

    # 2) плейсхолдер по тегу, если он есть
    if tag:
        name = f"{tag.capitalize()}_placeholder.svg"
        cand = os.path.join(PLACEHOLDERS, name)
        if os.path.exists(cand):
            return cand

    # 3) дефолтный плейсхолдер
    return os.path.join(PLACEHOLDERS, "default_placeholder.svg")

def get_books(tag: str | None = None, limit: int = 50, offset: int = 0):
    rows = fetch_books(tag, limit, offset)
    books = []
    for r in rows:
        cover_path = _resolve_cover_path(r["cover"], tag)
        px = _ensure_pixmap(cover_path, w=224, h=180)  # CARD_WIDTH-16 и COVER_HEIGHT из твоей карточки
        books.append({
            "id": r["id"],
            "title": r["title"],
            "author": r["author"],
            "description": r["description"],
            "tags": tag or "все категории",
            "cover_pixmap": px,
        })
    return books
