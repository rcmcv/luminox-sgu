from fastapi import APIRouter, Depends, HTTPException, status, Query, Security, Header, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.api import ok
from app.deps.pagination import get_pagination

from typing import List
from app.schemas.user import UserOut
from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.schemas.user import (
    LoginInput, TokenPair, UserCreate, UserOut, UserUpdateSelf,
    UserUpdateAdmin, PasswordChangeSelf, PasswordSetAdmin,)

from app.deps.auth import bearer_scheme, get_current_user
from app.repositories import user as repo
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token

router = APIRouter()

@router.post("/auth/login", response_model=TokenPair)
async def login(payload: LoginInput, db: AsyncSession = Depends(get_db)):
    user = await repo.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenPair(
        access_token=create_access_token(user.email, extra={"role": user.role}),
        refresh_token=create_refresh_token(user.email),
    )

@router.post("/auth/refresh", response_model=TokenPair)
async def refresh(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing refresh token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    # Gera novos tokens
    return TokenPair(
        access_token=create_access_token(email),
        refresh_token=create_refresh_token(email),
    )

@router.patch("/users/me", response_model=UserOut, dependencies=[])
async def update_me(
    payload: UserUpdateSelf,
    db: AsyncSession = Depends(get_db),
    current = Depends(get_current_user),
):
    try:
        updated = await repo.update_self(db, current, payload)
        return updated
    except ValueError as e:
        if str(e) == "email_taken":
            raise HTTPException(status_code=400, detail="E-mail já está em uso")
        raise

@router.patch("/users/me/password")
async def change_my_password(
    payload: PasswordChangeSelf,
    db: AsyncSession = Depends(get_db),
    current = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    await repo.set_password(db, current, payload.new_password)
    return {
        "detail": f"Senha alterada com sucesso, {current.full_name}.",
        "user": {"id": current.id, "full_name": current.full_name, "email": current.email},
    }

@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
):
    """
    Bootstrapping:
    - Se a tabela estiver VAZIA, permite criar usuário sem autenticação (primeiro admin).
    - Se já existir usuário, EXIGE ACCESS TOKEN com role=ADMIN.
    """
    total = await repo.count_all(db)
    if total > 0:
        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        token = credentials.credentials
        try:
            payload_token = decode_token(token)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        if payload_token.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        email = payload_token.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        current_user = await repo.get_by_email(db, email)
        if not current_user or not current_user.is_active:
            raise HTTPException(status_code=401, detail="Inactive or not found")
        if current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Not enough permissions")

    exists = await repo.get_by_email(db, payload.email)
    if exists:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    return await repo.create(db, payload)

@router.get("/users", response_model=None, dependencies=[Depends(require_roles("ADMIN"))])
async def list_users(
    request: Request,
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
):
    items = await repo.list_(db, skip=pagination.skip, limit=pagination.limit)
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    return ok(data=[
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None,
        } for u in items
    ], meta=meta, request=request)

@router.patch("/users/{user_id}", response_model=UserOut, dependencies=[Depends(require_roles("ADMIN"))])
async def admin_update_user(
    user_id: int,
    payload: UserUpdateAdmin,
    db: AsyncSession = Depends(get_db),
):
    user = await repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    try:
        updated = await repo.update_admin(db, user, payload)
        return updated
    except ValueError as e:
        if str(e) == "email_taken":
            raise HTTPException(status_code=400, detail="E-mail já está em uso")
        if str(e) == "would_remove_last_admin":
            raise HTTPException(status_code=400, detail="Não é permitido remover/rebaixar o último ADMIN ativo")
        raise

@router.patch("/users/{user_id}/password", dependencies=[Depends(require_roles("ADMIN"))])
async def admin_set_password(
    user_id: int,
    payload: PasswordSetAdmin,
    db: AsyncSession = Depends(get_db),
):
    user = await repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    await repo.set_password(db, user, payload.new_password)
    return {
        "detail": f"Senha do usuário '{user.full_name}' atualizada com sucesso.",
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email},
    }

@router.get("/users/{user_id}", response_model=UserOut, dependencies=[Depends(require_roles("ADMIN"))])
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user
