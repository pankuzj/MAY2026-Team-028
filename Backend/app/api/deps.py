"""Shared FastAPI route dependencies.

Task S1-A08 (owner: Sagnik). **This file is published signature-first on purpose.**

The plan flags this as the sprint's highest-risk handoff: every one of the twenty
protected endpoints imports from here, so four other developers are blocked until
these names exist. They exist now. ``get_db`` is fully wired; the two auth
dependencies raise ``NotImplementedError`` until ``core/security.py`` lands.

That means route authors can write final code today::

    @router.get("/complaints")
    def list_complaints(
        db: Session = Depends(get_db),
        user: "User" = Depends(get_current_user),
    ) -> Page[ComplaintRead]: ...

and their imports, type hints, and OpenAPI security scheme are already correct.
When Sagnik fills the bodies, no caller changes.
"""

from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.db.session import get_db

__all__ = ["bearer_scheme", "get_current_user", "get_db", "require_role"]

# auto_error=False so a missing header reaches our own handler and produces the
# shared error envelope. With the default (True), HTTPBearer raises its own
# HTTPException and the client would get a differently-shaped 403.
bearer_scheme = HTTPBearer(auto_error=False, description="JWT access token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """Resolve the ``User`` owning the bearer token, or raise 401.

    Raises:
        AuthenticationError: header missing/malformed, signature invalid, token
            expired, token is a *refresh* token used on an access-token route, or
            the referenced user no longer exists.

    TODO(S1-A08, Sagnik): implement once ``core/security.py`` (S1-F04) provides
    ``decode_access_token``. Steps: reject when ``credentials`` is None; decode;
    read ``sub`` as the user id; load via ``UserRepository``; raise if absent or
    inactive; return the model.
    """
    if credentials is None:
        raise AuthenticationError("Missing bearer token.")
    raise NotImplementedError("S1-A08: awaiting core/security.py (S1-F04).")


def require_role(*roles: str) -> Callable:
    """Build a dependency permitting only the given roles.

    The server-side twin of the frontend's ``ProtectedRoute``. Usage::

        @router.post("/tasks", dependencies=[Depends(require_role("admin"))])

    Returns a *new* dependency per call, so each route gets its own role set.

    Raises:
        PermissionDeniedError: the caller is authenticated but its role is not
            listed — 403, deliberately distinct from the 401 above so the client
            knows whether to re-login or to show "not available for your role".

    Roles, per plan assumption 2: ``citizen``, ``crew``, ``admin``, ``authority``.

    TODO(S1-A08, Sagnik): the closure below is correct as written; it starts
    working the moment ``get_current_user`` returns a real user object.
    """

    def _guard(user=Depends(get_current_user)):
        if getattr(user, "role", None) not in roles:
            raise PermissionDeniedError(
                f"This action requires one of these roles: {', '.join(sorted(roles))}."
            )
        return user

    return _guard
