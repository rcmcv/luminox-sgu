from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.deps.db import get_db

router = APIRouter()

@router.get("/health")
async def healthcheck(db: AsyncSession = Depends(get_db)):
    try:
        await db.scalar(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok",
        "service": "usinagem-backend",
        "db_ok": db_ok,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
