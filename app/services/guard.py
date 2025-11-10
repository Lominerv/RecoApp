from app.services import auth_service

class PermissionDenied(Exception):
    pass

def require_admin():
    user = auth_service.get_current_user()
    if not user or int(user.get("is_admin", 0)) != 1:
        raise PermissionDenied("Требуются права администратора")