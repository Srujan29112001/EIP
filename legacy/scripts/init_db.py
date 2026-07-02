#!/usr/bin/env python3
"""
Database initialization script
Creates all necessary tables and initial data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.models.database import Base, engine
from backend.app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def init_db():
    """Initialize database with all tables"""
    try:
        logger.info("Creating database tables...")

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("Database tables created successfully!")

        # TODO: Add seed data if needed

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    init_db()
