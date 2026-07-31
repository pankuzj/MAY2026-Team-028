"""Resource route modules (one per aggregate)."""

from app.api.v1.routes import auth, complaints, wards

__all__ = ["auth", "complaints", "wards"]
