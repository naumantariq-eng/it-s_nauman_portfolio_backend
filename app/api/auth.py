from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from app.core.security import verify_admin_credentials, create_access_token
from app.dependencies.auth import get_current_admin
from app.schemas.auth import LoginRequest, TokenResponse, AdminProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate administrator credentials configured via environment variables.
    Returns a signed JWT bearer token.
    """
    is_valid = verify_admin_credentials(credentials.email, credentials.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token payload
    token_data = {"sub": settings.ADMIN_EMAIL, "role": "admin"}
    access_token = create_access_token(data=token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=AdminProfile)
async def get_admin_profile(current_admin: AdminProfile = Depends(get_current_admin)):
    """Return currently authenticated administrator profile."""
    return current_admin
