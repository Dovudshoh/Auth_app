from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.schemas.schemas import ResourceOut, UserOut
from app.core.security import get_current_user
from app.services.access_service import (
    check_resource_access,
    require_permission,
    get_user_permissions,
    get_user_resources,
)

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/", response_model=list[ResourceOut])
def list_my_resources(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all resources the current user has access to."""
    accessible_names = get_user_resources(current_user)
    resources = db.query(models.Resource).filter(
        models.Resource.name.in_(accessible_names)
    ).all()
    return resources


@router.get("/documents")
def get_documents(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Access documents resource.
    Available to: user, moderator, admin
    """
    check_resource_access(current_user, "documents", db)
    return {
        "resource": "documents",
        "data": [
            {"id": 1, "title": "Company Policy v2.0"},
            {"id": 2, "title": "Onboarding Guide"},
        ],
    }


@router.post("/documents")
def create_document(current_user: models.User = Depends(get_current_user)):
    """
    Create a document (requires 'write' permission).
    Available to: moderator, admin
    """
    check_resource_access(current_user, "documents")
    require_permission(current_user, "write")
    return {"detail": "Document created successfully"}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, current_user: models.User = Depends(get_current_user)):
    """
    Delete a document (requires 'delete' permission).
    Available to: admin only
    """
    check_resource_access(current_user, "documents")
    require_permission(current_user, "delete")
    return {"detail": f"Document {doc_id} deleted"}


@router.get("/reports")
def get_reports(current_user: models.User = Depends(get_current_user)):
    """
    Access reports resource.
    Available to: moderator, admin
    """
    check_resource_access(current_user, "reports")
    return {
        "resource": "reports",
        "data": [
            {"id": 1, "title": "Q1 2024 Analytics"},
            {"id": 2, "title": "User Growth Report"},
        ],
    }


@router.get("/admin_panel")
def get_admin_panel(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Access admin panel.
    Available to: admin only
    """
    check_resource_access(current_user, "admin_panel", db)
    users = db.query(models.User).all()
    return {
        "resource": "admin_panel",
        "total_users": len(users),
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "is_active": u.is_active,
                "roles": [r.name for r in u.roles],
            }
            for u in users
        ],
    }


@router.get("/my-permissions")
def my_permissions(current_user: models.User = Depends(get_current_user)):
    """Returns current user's roles and permissions."""
    return {
        "roles": [r.name for r in current_user.roles],
        "permissions": list(get_user_permissions(current_user)),
        "resources": list(get_user_resources(current_user)),
    }
