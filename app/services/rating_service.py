from app.services.auth_service import get_current_user
from app.repositories.ratings_repo import (
    upsert_rating as repo_upsert_rating,
    get_user_book_rating as repo_get_user_book_rating,
    delete_rating as repo_delete_rating,
    get_book_avg_rating as repo_get_book_avg_rating,
    list_user_rated_book_ids as _repo_list_rated_ids
)

class NotAuthenticatedError(Exception):
    pass

def _require_user_id():
    user = get_current_user()
    if not user:
        raise NotAuthenticatedError("Требуется вход в систему")
    return int(user["id"])

def set_rating(book_id, rating):
    try:
        iv = int(rating)
    except (TypeError, ValueError):
        raise ValueError("Оценка должна быть целым числом от 1 до 5")

    if iv < 1 or iv > 5:
        raise ValueError("Оценка должна быть от 1 до 5")

    uid = _require_user_id()
    repo_upsert_rating(uid, book_id, iv)
    return rating

def get_my_rating(book_id):
    uid = _require_user_id()
    return repo_get_user_book_rating(uid, book_id)

def remove_my_rating(book_id):
    uid = _require_user_id()
    repo_delete_rating(uid, book_id)

def get_book_avg(book_id):
    return repo_get_book_avg_rating(book_id)

def list_my_rated_ids():
    uid = _require_user_id()
    return _repo_list_rated_ids(uid)

def get_my_rated_count():
    return len(list_my_rated_ids())