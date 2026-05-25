from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


def _key_ip_user(request: Request) -> str:
    """Combina IP + user_id quando autenticado. Anti-bypass em sessao compartilhada."""
    ip = get_remote_address(request)
    user_id = getattr(request.state, "user_id", None)
    return f"{ip}:{user_id}" if user_id else ip


limiter = Limiter(key_func=_key_ip_user)
