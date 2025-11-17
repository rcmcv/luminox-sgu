# app/core/error_handlers.py

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy.exc import IntegrityError  # <-- NOVO
from app.core.api import fail


def _msg_unique(e_msg: str) -> str:
    txt = (e_msg or "").lower()
    if "contrato_hh_precos" in txt:
        return "Já existe um preço de HH para esta combinação (Contrato, Máquina, Tipo de Hora)."
    if "contrato_material_precos" in txt:
        return "Já existe um preço de material para esta combinação (Contrato, Material)."
    if "unique" in txt or "duplicate key" in txt:
        return "Registro duplicado: violação de unicidade."
    return "Violação de unicidade."

def _msg_fk(e_msg: str) -> str:
    return "Violação de integridade referencial: verifique se os IDs relacionados existem."

def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exc_handler(request: Request, exc: StarletteHTTPException):
        payload = fail(
            message=exc.detail if isinstance(exc.detail, str) else "Erro HTTP",
            errors=None if isinstance(exc.detail, str) else exc.detail,
            status_code=exc.status_code,
            request=request,
        )
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exc_handler(request: Request, exc: RequestValidationError):
        raw_errors = exc.errors()

        friendly_errors = []
        for err in raw_errors:
            loc = err.get("loc", [])
            field = loc[-1] if loc else None
            typ = err.get("type", "")
            ctx = err.get("ctx", {}) or {}

            # Mensagens personalizadas por campo/regra
            if field == "cliente_id":
                # vazio/0 → swagger costuma mandar 0; também pode ser tipo errado
                if typ in ("greater_than_equal", "int_type", "int_parsing"):
                    friendly_errors.append({
                        "field": "cliente_id",
                        "message": "cliente_id é obrigatório e deve ser um inteiro ≥ 1."
                    })
                    continue

            # fallback genérico (mantém algo útil, mas mais curto)
            friendly_errors.append({
                "field": str(field) if field else "body",
                "message": err.get("msg", "Campo inválido.")
            })

        payload = fail(
            message="Dados inválidos. Corrija os campos destacados.",
            errors=friendly_errors,
            status_code=422,
            request=request,
        )
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(IntegrityError)
    async def integrity_exc_handler(request: Request, exc: IntegrityError):
        raw = ""
        if getattr(exc, "orig", None) and getattr(exc.orig, "args", None):
            raw = str(exc.orig.args[0])
        else:
            raw = str(exc)

        msg_lower = raw.lower()
        if "unique" in msg_lower or "duplicate key" in msg_lower:
            friendly = "Registro duplicado: violação de unicidade."
            if "contrato_hh_precos" in msg_lower:
                friendly = "Já existe um preço de HH para esta combinação (Contrato, Máquina, Tipo de Hora)."
            if "contrato_material_precos" in msg_lower:
                friendly = "Já existe um preço de material para esta combinação (Contrato, Material)."
            status_code = 409
        elif "foreign key" in msg_lower or ("constraint failed" in msg_lower and "references" in msg_lower):
            friendly = "Violação de integridade referencial: verifique se os IDs relacionados existem."
            status_code = 400
        else:
            friendly = "Erro de integridade do banco de dados."
            status_code = 400

        payload = fail(
            message=friendly,
            errors=None,
            status_code=status_code,
            request=request,
        )
        return JSONResponse(status_code=status_code, content=payload)

    @app.middleware("http")
    async def catch_all_exceptions(request: Request, call_next):
        try:
            return await call_next(request)
        except (IntegrityError, RequestValidationError, StarletteHTTPException):
            raise
        except Exception as e:
            payload = fail(
                message="Erro interno no servidor",
                errors=str(e),
                status_code=500,
                request=request,
            )
            return JSONResponse(status_code=500, content=payload)
