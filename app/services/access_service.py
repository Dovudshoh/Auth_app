from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db import models


def get_user_permissions(user: models.User) -> set[str]:
    """Return set of permission names the user has via their roles."""
    permissions = set()
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.name)
    return permissions


def get_user_resources(user: models.User) -> set[str]:
    """Return set of resource names accessible to the user via their roles."""
    resources = set()
    for role in user.roles:
        for resource in role.resources:
            resources.add(resource.name)
    return resources


def check_resource_access(user: models.User, resource_name: str, db: Session):
    """
    Verify the user has access to the given resource.
    Raises 403 if access is denied.
    """
    accessible = get_user_resources(user)
    if resource_name not in accessible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access to resource '{resource_name}' is forbidden",
        )


def require_permission(user: models.User, permission: str):
    """
    Verify the user has a specific permission.
    Raises 403 if not.
    """
    permissions = get_user_permissions(user)
    if permission not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission}' required",
        )
