"""Repositories — the only layer that talks to the database."""

from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.user_repository import UserRepository
from app.repositories.ward_repository import WardRepository

__all__ = [
	"ComplaintRepository",
	"UserRepository",
	"WardRepository",
]
