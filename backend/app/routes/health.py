# ─── AgriFlow AI — Health Route ───────────────────────────────────────────────
from fastapi import APIRouter
from ..database import get_database

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check.
    Returns database connection status alongside app info.
    """
    try:
        db = get_database()
        await db.command("ping")
        db_status = "connected"
    except Exception as exc:
        db_status = f"error: {exc}"

    return {
        "status": "ok",
        "database": db_status,
        "app": "AgriFlow AI",
        "version": "1.0.0",
    }
