"""Resource route modules (one per aggregate)."""

from app.api.v1.routes import auth, wards

__all__ = ["auth", "wards"]
