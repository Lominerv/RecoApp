# app/services/favorites_service.py
from typing import List

from app.services.auth_service import get_current_user
from app.repositories.favorites_repo import (
    is_favorite as repo_is_favorite,
    add_favorite as repo_add_favorite,
    remove_favorite as repo_remove_favorite,
    list_favorite_book_ids as repo_list_ids,
)

class NotAuthenticatedError(Exception):
    pass

def _require_user_id():
    user = get_current_user()
    if not user:
        raise NotAuthenticatedError("Требуется вход в систему")
    return int(user["id"])

def is_favorite(book_id: int) -> bool:
    uid = _require_user_id()
    return repo_is_favorite(uid, book_id)

def set_favorite(book_id, state):
    uid = _require_user_id()
    now_state = repo_is_favorite(uid, book_id)
    if state and not now_state:
        repo_add_favorite(uid, book_id)
        return True
    if not state and now_state:
        repo_remove_favorite(uid, book_id)
        return False
    return now_state

def toggle_favorite(book_id: int) -> bool:
    uid = _require_user_id()
    state = repo_is_favorite(uid, book_id)
    if state:
        repo_remove_favorite(uid, book_id)
        return False
    else:
        repo_add_favorite(uid, book_id)
        return True

def get_favorite_book_ids():
    uid = _require_user_id()
    return repo_list_ids(uid)
