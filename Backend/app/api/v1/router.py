"""Aggregates all v1 resource routers into a single APIRouter."""

from fastapi import APIRouter

from app.api.v1.routes import auth

router = APIRouter()
router.include_router(auth.router)

__all__ = ["router"]
