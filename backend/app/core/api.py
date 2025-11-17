from typing import Any, Optional, Dict
from fastapi import Request

def _rid(request: Optional[Request]) -> Optional[str]:
    try:
        return request.state.request_id  # setado pelo middleware
    except Exception:
        return None

def ok(
    data: Any = None,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
):
    return {
        "success": True,
        "message": message,
        "data": data,
        "meta": meta or {},
        "request_id": _rid(request),
    }

def created(
    data: Any = None,
    message: Optional[str] = "Criado com sucesso.",
    meta: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
):
    return {
        "success": True,
        "message": message,
        "data": data,
        "meta": meta or {},
        "request_id": _rid(request),
    }

def fail(
    message: str,
    errors: Optional[Any] = None,
    status_code: int = 400,
    request: Optional[Request] = None,
):
    # apenas estrutura; o status code é aplicado pelos handlers
    return {
        "success": False,
        "message": message,
        "errors": errors,
        "request_id": _rid(request),
    }
