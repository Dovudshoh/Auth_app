from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.schemas.schemas import UserRegister, UserLogin, Token, UserOut, UserUpdate
from app.services import auth_service
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    return auth_service.register_user(data, db)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login and receive a JWT access token."""
    return auth_service.login_user(data, db)


@router.post("/logout")
def logout(current_user: models.User = Depends(get_current_user)):
    """
    Logout endpoint.
    JWT tokens are stateless — client must discard the token.
    On the server side we confirm the identity and return success.
    """
    return {"detail": f"User {current_user.email} logged out successfully"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    """Get current authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile information."""
    updates = data.model_dump(exclude_none=True)
    return auth_service.update_user(current_user, updates, db)


@router.delete("/me", status_code=204)
def delete_me(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Soft-delete current user's account.
    Sets is_active=False. User cannot login after this.
    """
    auth_service.soft_delete_user(current_user, db)
