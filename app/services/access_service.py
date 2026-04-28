from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db import models


def get_user_permissions(user: models.User) -> set[str]:
    permissions = set()
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.name)
    return permissions


def get_user_resources(user: models.User) -> set[str]:
    resources = set()
    for role in user.roles:
        for resource in role.resources:
            resources.add(resource.name)
    return resources


def check_resource_access(user: models.User, resource_name: str, db: Session):
    accessible = get_user_resources(user)
    if resource_name not in accessible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access to resource '{resource_name}' is forbidden",
        )


def require_permission(user: models.User, permission: str):
    permissions = get_user_permissions(user)
    if permission not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission}' required",
        )
