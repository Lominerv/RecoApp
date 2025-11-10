from app.services.auth_service import get_current_user
from app.repositories.books_repo import fetch_books
from app.repositories.favorites_repo import list_favorite_book_ids
from app.repositories.ratings_repo import list_user_rated_book_ids
from app.repositories.books_repo import get_book_by_id

from collections import Counter
import traceback
from app.services.auth_service import get_current_user
from app.services import rating_service
from app.repositories.favorites_repo import list_favorite_book_ids
from app.repositories.books_repo import get_book_by_id
from app.services.catalog_service import get_books  # даст книги сразу с cover_pixmap и tags-списком

class NotEnoughData(Exception):
    pass

def _collect_base_book_ids(user_id):
    rated = set(rating_service.list_my_rated_ids())
    favs = set(list_favorite_book_ids(user_id))
    return rated | favs

def _collect_tag_freq(book_ids):
    tags = []
    for bid in book_ids:
        row = get_book_by_id(bid)
        if not row:
            continue
        tags += [t.strip() for t in (row.get("tags") or "").split(",") if t.strip()]
    return Counter(tags) #подсчёт повторяющихся тегов

def get_recommendations(limit: int = 15) -> list[dict]:
    user = get_current_user()
    if not user:
        return []
    base_ids = _collect_base_book_ids(user["id"])
    if len(base_ids) < 3:
        raise NotEnoughData("Нужно минимум 3 оценённые/избранные книги")
    tag_counter = _collect_tag_freq(base_ids)
    if not tag_counter:
        return []
    top_tags = [t for t, _ in tag_counter.most_common(3)] #3 самых популярных тега
    rec_by_id = {}
    for tag in top_tags:
        for book in get_books(tag=tag, limit=limit):
            bid = int(book["id"])
            if bid in base_ids:
                continue
            if bid not in rec_by_id:
                rec_by_id[bid] = book
            if len(rec_by_id) >= limit:
                break
        if len(rec_by_id) >= limit:
            break
    return list(rec_by_id.values())


# def get_recommendations(limit: int = 15) -> list[dict]:
#     print("[RECSVC] enter, limit=", limit)
#     user = get_current_user()
#     print("[RECSVC] user:", user)
#
#     if not user:
#         print("[RECSVC] no user -> []")
#         return []
#
#     try:
#         base_ids = _collect_base_book_ids(user["id"])
#         print("[RECSVC] base_ids:", sorted(list(base_ids)))
#     except Exception as e:
#         print("[RECSVC] error in _collect_base_book_ids:", e)
#         print(traceback.format_exc())
#         raise
#
#     if len(base_ids) < 3:
#         print("[RECSVC] NotEnoughData (<3)")
#         raise NotEnoughData("Нужно минимум 3 оценённые/избранные книги")
#
#     try:
#         cnt = _collect_tag_freq(base_ids)
#         print("[RECSVC] tag_counter:", dict(cnt))
#     except Exception as e:
#         print("[RECSVC] error in _collect_tag_freq:", e)
#         print(traceback.format_exc())
#         raise
#
#     if not cnt:
#         print("[RECSVC] no tags -> []")
#         return []
#
#     top_tags = [t for t, _ in cnt.most_common(3)]
#     print("[RECSVC] top_tags:", top_tags)
#
#     rec: dict[int, dict] = {}
#     for tag in top_tags:
#         print(f"[RECSVC] fetching by tag='{tag}'")
#         try:
#             books = get_books(tag=tag, limit=limit)
#             print(f"[RECSVC] fetched {len(books)} books for tag '{tag}'")
#         except Exception as e:
#             print("[RECSVC] get_books error:", e)
#             print(traceback.format_exc())
#             continue
#
#         for b in books:
#             try:
#                 bid = int(b["id"])
#             except Exception as e:
#                 print("[RECSVC] bad book row (no id/int):", b, e)
#                 continue
#
#             if bid in base_ids or bid in rec:
#                 continue
#             rec[bid] = b
#             if len(rec) >= limit:
#                 break
#         if len(rec) >= limit:
#             break
#
#     out = list(rec.values())
#     print("[RECSVC] result size:", len(out))
#     return out
