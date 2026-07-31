"""Repositories — the only layer that talks to the database."""

from app.repositories.user_repository import UserRepository

__all__ = ["UserRepository"]
