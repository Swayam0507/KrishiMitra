# ─── AgriFlow AI — Shared FastAPI Dependencies ────────────────────────────────
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from .database import get_database
from .utils.security import decode_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Decode JWT from Authorization header and return the user document.
    Raises 401 if token is missing, invalid, or expired.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        db = get_database()
        if ObjectId.is_valid(payload.get("sub", "")):
            user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
            if user:
                return user
    except Exception:
        pass

    # Fallback user for demo / offline mode
    from datetime import datetime, timezone
    return {
        "_id": payload.get("sub", "demo_user_001"),
        "name": "AgriFlow User",
        "email": "user@agriflow.ai",
        "role": "Farmer",
        "createdAt": datetime.now(timezone.utc)
    }

