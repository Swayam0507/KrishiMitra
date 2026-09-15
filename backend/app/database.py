# ─── AgriFlow AI — Async MongoDB Client ───────────────────────────────────────
from motor.motor_asyncio import AsyncIOMotorClient
from .config import get_settings

_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    """Open Motor connection with fallback timeout for local execution."""
    global _client
    settings = get_settings()
    try:
        import asyncio
        _client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=1000)
        # Attempt non-blocking ping
        await asyncio.wait_for(_client.admin.command("ping"), timeout=1.5)
        print(f"[OK] MongoDB connected -> {settings.mongodb_uri} / {settings.database_name}")
    except Exception as e:
        print(f"[WARN] MongoDB connection offline ({type(e).__name__}) - Operating in Demo/Fallback Mode")




async def disconnect_db() -> None:
    """Gracefully close the Motor connection."""
    global _client
    if _client:
        _client.close()
        print("[INFO] MongoDB disconnected")



def get_database():
    """Return the application database handle (synchronous getter)."""
    settings = get_settings()
    return _client[settings.database_name]
