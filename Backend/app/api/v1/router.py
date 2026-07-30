"""Aggregates all v1 resource routers into a single APIRouter.

Task S1-A09. ``main.py`` includes exactly one router — this one — so adding an
endpoint group never means editing the app factory. Each owner adds a single
``include_router`` line here when their route module lands.

**Merge-conflict note:** five people will edit this file during Sprint 1. Add your
line in the alphabetical slot marked below and do not reorder the others; that
keeps conflicts to one line instead of the whole block.
"""

from fastapi import APIRouter

__all__ = ["api_router"]

api_router = APIRouter()

# --- Sprint 1 routers (plan section 9e) -----------------------------------
# Add one line each, keeping alphabetical order. Owners:
#   S1-A01 auth       — Sagnik
#   S1-A02 wards      — Sagnik
#   S1-A03/04/05 complaints — Vishal (6, 8, 9, 10, 11 + photo) / Jatin (12, 13, 14)
#   S1-A06 tasks      — Nitin
#   S1-A07 resources  — Pankaj (workers, equipment, vehicles)
#
# from app.api.v1.routes import auth, complaints, resources, tasks, wards
#
# api_router.include_router(auth.router)
# api_router.include_router(complaints.router)
# api_router.include_router(resources.router)
# api_router.include_router(tasks.router)
# api_router.include_router(wards.router)

# Each route module owns its own prefix and tags, e.g.
#     router = APIRouter(prefix="/complaints", tags=["complaints"])
# so the final path is settings.api_v1_prefix + "/complaints". Declaring the
# prefix in the module rather than here keeps a route's full URL visible in the
# file you are reading.
