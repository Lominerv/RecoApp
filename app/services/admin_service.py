from app.repositories.tags_repo import link_book_tags, get_or_create_tag_id
from app.services.guard import require_admin
from app.services import auth_service
from app.repositories.books_repo import count_books, insert_book, delete_book_by_title
from app.repositories.users_repo import count_users

def get_dashboard_stats():
    require_admin()
    total_books = count_books()
    total_users = count_users()
    active_users = 1 if auth_service.get_current_user() else 0
    return {
        "books": total_books,
        "users": total_users,
        "active": active_users,
    }

def add_book(*, title, author, description, tags, cover):
    require_admin()

    title = (title or "").strip()
    author = (author or "").strip()
    description = (description or "").strip()
    if not title or not author or not description:
        raise ValueError("Название, автор и описание обязательны")

    book_id = insert_book(title, author, description, cover or None)

    for tag in tags:
        nm = (tag or "").strip().lower()
        if not nm:
            continue
        tid = get_or_create_tag_id(nm)
        link_book_tags(book_id,tid)

    return book_id

def delete_book(title):
    require_admin()
    if not title.strip():
        raise ValueError("Введите название книги.")
    n = delete_book_by_title(title)
    if n == 0:
        raise ValueError(f"Книга {title.strip()}, не найдена!")
    return n
