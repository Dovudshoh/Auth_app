"""
Seed script — fills the DB with test data.
Run: python -m app.db.seed
"""
from app.db.database import SessionLocal, engine, Base
from app.db import models
from app.core.security import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if not db.query(models.Permission).first():
            perms = [
                models.Permission(name="read", description="Read access"),
                models.Permission(name="write", description="Write access"),
                models.Permission(name="delete", description="Delete access"),
            ]
            db.add_all(perms)
            db.flush()

        perm_read = db.query(models.Permission).filter_by(name="read").first()
        perm_write = db.query(models.Permission).filter_by(name="write").first()
        perm_delete = db.query(models.Permission).filter_by(name="delete").first()

        if not db.query(models.Resource).first():
            resources = [
                models.Resource(name="documents", description="Company documents"),
                models.Resource(name="reports", description="Analytics reports"),
                models.Resource(name="admin_panel", description="Administration panel"),
            ]
            db.add_all(resources)
            db.flush()

        res_docs = db.query(models.Resource).filter_by(name="documents").first()
        res_reports = db.query(models.Resource).filter_by(name="reports").first()
        res_admin = db.query(models.Resource).filter_by(name="admin_panel").first()

        if not db.query(models.Role).first():
            role_user = models.Role(name="user", description="Regular user")
            role_user.permissions = [perm_read]
            role_user.resources = [res_docs]

            role_moderator = models.Role(name="moderator", description="Content moderator")
            role_moderator.permissions = [perm_read, perm_write]
            role_moderator.resources = [res_docs, res_reports]

            role_admin = models.Role(name="admin", description="Full access administrator")
            role_admin.permissions = [perm_read, perm_write, perm_delete]
            role_admin.resources = [res_docs, res_reports, res_admin]

            db.add_all([role_user, role_moderator, role_admin])
            db.flush()

        role_user = db.query(models.Role).filter_by(name="user").first()
        role_moderator = db.query(models.Role).filter_by(name="moderator").first()
        role_admin = db.query(models.Role).filter_by(name="admin").first()

        if not db.query(models.User).first():
            admin = models.User(
                first_name="Иван",
                last_name="Администраторов",
                patronymic="Сергеевич",
                email="admin@example.com",
                hashed_password=hash_password("Admin1234!"),
            )
            admin.roles = [role_admin]

            moderator = models.User(
                first_name="Мария",
                last_name="Модераторова",
                patronymic="Ивановна",
                email="moderator@example.com",
                hashed_password=hash_password("Moder1234!"),
            )
            moderator.roles = [role_moderator]

            user1 = models.User(
                first_name="Алексей",
                last_name="Пользователев",
                patronymic="Петрович",
                email="user@example.com",
                hashed_password=hash_password("User1234!"),
            )
            user1.roles = [role_user]

            db.add_all([admin, moderator, user1])

        db.commit()
        print("✅ Seed completed successfully!")
        print("\nTest accounts:")
        print("  admin@example.com      / Admin1234!")
        print("  moderator@example.com  / Moder1234!")
        print("  user@example.com       / User1234!")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
