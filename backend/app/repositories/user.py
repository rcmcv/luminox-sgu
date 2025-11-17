from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdateSelf, UserUpdateAdmin
from app.core.security import hash_password, verify_password

async def count_all(db: AsyncSession) -> int:
    res = await db.execute(select(func.count()).select_from(User))
    return res.scalar_one()

async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()

async def create(db: AsyncSession, data: UserCreate) -> User:
    obj = User(
        email=data.email,
        full_name=data.full_name,
        role=data.role,
        hashed_password=hash_password(data.password),
        is_active=True,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user

async def list_(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[User]:
    res = await db.execute(
        select(User).order_by(User.id).offset(skip).limit(limit)
    )
    return list(res.scalars())

async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    return await db.get(User, user_id)

async def count_admins_active(db: AsyncSession) -> int:
    res = await db.execute(
        select(func.count()).select_from(User).where(User.role == "ADMIN", User.is_active == True)  # noqa: E712
    )
    return res.scalar_one()

async def email_in_use(db: AsyncSession, email: str, exclude_user_id: Optional[int] = None) -> bool:
    q = select(User).where(User.email == email)
    res = await db.execute(q)
    user = res.scalar_one_or_none()
    if not user:
        return False
    if exclude_user_id and user.id == exclude_user_id:
        return False
    return True

async def update_self(db: AsyncSession, user: User, data: UserUpdateSelf) -> User:
    changes = data.model_dump(exclude_unset=True)
    if "email" in changes:
        if await email_in_use(db, changes["email"], exclude_user_id=user.id):
            raise ValueError("email_taken")
    for k, v in changes.items():
        setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return user

async def update_admin(db: AsyncSession, user: User, data: UserUpdateAdmin) -> User:
    changes = data.model_dump(exclude_unset=True)
    # Unique email
    if "email" in changes:
        if await email_in_use(db, changes["email"], exclude_user_id=user.id):
            raise ValueError("email_taken")

    # Proteções de último ADMIN ativo
    if user.role == "ADMIN":
        admins = await count_admins_active(db)
        # Se só existe 1 admin ativo e vamos desativar ou rebaixar -> bloquear
        if admins == 1:
            if ("is_active" in changes and changes["is_active"] is False) or ("role" in changes and changes["role"] != "ADMIN"):
                raise ValueError("would_remove_last_admin")

    for k, v in changes.items():
        setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return user

async def set_password(db: AsyncSession, user: User, new_password: str) -> User:
    user.hashed_password = hash_password(new_password)
    await db.commit()
    await db.refresh(user)
    return user
