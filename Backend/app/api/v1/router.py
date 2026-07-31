"""Aggregates all v1 resource routers into a single APIRouter."""

from fastapi import APIRouter

from app.api.v1.routes import auth, complaints, resources, wards

router = APIRouter()
router.include_router(auth.router)
router.include_router(wards.router)
router.include_router(complaints.router)
router.include_router(resources.router)

__all__ = ["router"]
