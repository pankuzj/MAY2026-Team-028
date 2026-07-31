"""Aggregates all v1 resource routers into a single APIRouter."""

from fastapi import APIRouter

from app.api.v1.routes import auth, wards

router = APIRouter()
router.include_router(auth.router)
router.include_router(wards.router)

__all__ = ["router"]
