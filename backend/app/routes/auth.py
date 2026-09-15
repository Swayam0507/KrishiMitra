# ─── AgriFlow AI — Auth Routes ────────────────────────────────────────────────
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timezone
from bson import ObjectId

from ..database import get_database
from ..utils.security import hash_password, verify_password, create_access_token
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse, VALID_ROLES
from ..dependencies import get_current_user

router = APIRouter()


def _serialize_user(user: dict) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user["role"],
        createdAt=user["createdAt"],
    )


# In-memory demo user store for offline/demo fallback
_IN_MEMORY_USERS = {}

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest):
    """Register a new user. Returns JWT on success."""
    role = data.role if data.role in VALID_ROLES else "Farmer"

    try:
        db = get_database()
        if await db.users.find_one({"email": data.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        doc = {
            "name": data.name,
            "email": data.email,
            "passwordHash": hash_password(data.password),
            "role": role,
            "createdAt": datetime.now(timezone.utc),
        }
        result = await db.users.insert_one(doc)
        doc["_id"] = result.inserted_id
        token = create_access_token({"sub": str(result.inserted_id)})
        return TokenResponse(access_token=token, user=_serialize_user(doc))
    except HTTPException:
        raise
    except Exception as e:
        # Fallback to in-memory store if MongoDB is offline/unreachable
        if data.email in _IN_MEMORY_USERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        user_id = f"demo_user_{len(_IN_MEMORY_USERS) + 1}"
        user_doc = {
            "_id": user_id,
            "name": data.name,
            "email": data.email,
            "passwordHash": hash_password(data.password),
            "role": role,
            "createdAt": datetime.now(timezone.utc),
        }
        _IN_MEMORY_USERS[data.email] = user_doc
        token = create_access_token({"sub": user_id})
        return TokenResponse(access_token=token, user=_serialize_user(user_doc))


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """Authenticate and return JWT."""
    try:
        db = get_database()
        user = await db.users.find_one({"email": data.email})
        if user and verify_password(data.password, user["passwordHash"]):
            token = create_access_token({"sub": str(user["_id"])})
            return TokenResponse(access_token=token, user=_serialize_user(user))
    except Exception:
        pass

    # Check in-memory store or fallback demo login
    user = _IN_MEMORY_USERS.get(data.email)
    if user and verify_password(data.password, user["passwordHash"]):
        token = create_access_token({"sub": str(user["_id"])})
        return TokenResponse(access_token=token, user=_serialize_user(user))

    # Allow instant demo login for testing
    if data.email == "demo@agriflow.ai" and data.password == "demo1234":
        demo_doc = {
            "_id": "demo_user_001",
            "name": "AgriFlow Demo Farmer",
            "email": "demo@agriflow.ai",
            "passwordHash": hash_password("demo1234"),
            "role": "Farmer",
            "createdAt": datetime.now(timezone.utc),
        }
        token = create_access_token({"sub": "demo_user_001"})
        return TokenResponse(access_token=token, user=_serialize_user(demo_doc))

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )



@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return _serialize_user(current_user)
