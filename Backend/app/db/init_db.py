"""Database initialization and seeding of demo users."""

import logging
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

DEMO_USERS_SEED = [
    {
        "username": "citizen",
        "email": "citizen@smartsweep.gov",
        "password": "citizen123",
        "full_name": "Sagnik Halder",
        "role": UserRole.CITIZEN.value,
    },
    {
        "username": "anita",
        "email": "anita@smartsweep.gov",
        "password": "anita123",
        "full_name": "Anita Rao",
        "role": UserRole.CITIZEN.value,
    },
    {
        "username": "mohammed",
        "email": "mohammed@smartsweep.gov",
        "password": "mohammed123",
        "full_name": "Mohammed Iqbal",
        "role": UserRole.CITIZEN.value,
    },
    {
        "username": "crew",
        "email": "crew@smartsweep.gov",
        "password": "crew123",
        "full_name": "Suresh Patil",
        "role": UserRole.CREW.value,
    },
    {
        "username": "admin",
        "email": "admin@smartsweep.gov",
        "password": "admin123",
        "full_name": "Ward Supervisor / Admin",
        "role": UserRole.ADMIN.value,
    },
]


def init_db(db: Session) -> None:
    """Ensure database tables exist and seed initial demo users."""
    Base.metadata.create_all(bind=engine)

    for user_data in DEMO_USERS_SEED:
        existing = UserRepository.get_by_email(db, user_data["email"])
        if not existing:
            user = User(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
            )
            UserRepository.create(db, user)
            logger.info("Seeded demo user: %s (%s)", user_data["full_name"], user_data["email"])
