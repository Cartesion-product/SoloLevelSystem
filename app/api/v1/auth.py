"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserSettingsUpdate,
)
from app.core.logger import get_logger
from app.dependencies import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.domain.interview.models import User
from app.infrastructure.database import get_db

logger = get_logger(__name__)
router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    logger.info(f"Register attempt: username={body.username}, email={body.email}")
    # Check uniqueness
    existing = await db.execute(
        select(User).where((User.email == body.email) | (User.username == body.username))
    )
    if existing.scalar_one_or_none():
        logger.warning(f"Register conflict: username={body.username}, email={body.email}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    logger.info(f"User registered: id={user.id}, username={user.username}")
    return UserResponse(id=str(user.id), username=user.username, email=user.email, settings=user.settings or {})


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    logger.info(f"Login attempt: email={body.email}")
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        logger.warning(f"Login failed: email={body.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(str(user.id))
    logger.info(f"Login success: user_id={user.id}")
    return TokenResponse(access_token=token)


@router.put("/users/settings", response_model=UserResponse)
async def update_settings(
    body: UserSettingsUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current = user.settings or {}
    updates = body.model_dump(exclude_none=True)
    current.update(updates)
    user.settings = current
    await db.flush()
    await db.refresh(user)
    return UserResponse(id=str(user.id), username=user.username, email=user.email, settings=user.settings or {})
