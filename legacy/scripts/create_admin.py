#!/usr/bin/env python3
"""
Create admin user script
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.models.database import SessionLocal
from backend.app.models.user import User, UserTier
from backend.app.core.security import get_password_hash
from backend.app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def create_admin_user():
    """Create admin user"""
    db = SessionLocal()

    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@eip.com").first()

        if admin:
            logger.info("Admin user already exists")
            return

        # Create admin user
        admin = User(
            email="admin@eip.com",
            name="Admin User",
            hashed_password=get_password_hash("admin123"),
            tier=UserTier.TOP_LEVEL,
            is_active=True,
            is_verified=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        logger.info(f"Admin user created successfully!")
        logger.info(f"Email: admin@eip.com")
        logger.info(f"Password: admin123")
        logger.info("⚠️  Please change the password after first login!")

    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
