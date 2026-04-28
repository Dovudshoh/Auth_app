from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db import models
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.schemas import UserRegister, UserLogin, Token


def register_user(data: UserRegister, db: Session) -> models.User:
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Assign default "user" role
    default_role = db.query(models.Role).filter(models.Role.name == "user").first()

    user = models.User(
        first_name=data.first_name,
        last_name=data.last_name,
        patronymic=data.patronymic,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    if default_role:
        user.roles = [default_role]

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(data: UserLogin, db: Session) -> Token:
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
        )

    token = create_access_token(data={"sub": user.id})
    return Token(access_token=token)


def update_user(user: models.User, updates: dict, db: Session) -> models.User:
    for field, value in updates.items():
        if value is not None:
            # Check email uniqueness if email is being changed
            if field == "email" and value != user.email:
                existing = db.query(models.User).filter(models.User.email == value).first()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use",
                    )
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def soft_delete_user(user: models.User, db: Session) -> None:
    """Soft delete: mark as inactive, keep record in DB."""
    user.is_active = False
    db.commit()
