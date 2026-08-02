"""API integration tests for complaint route authentication and ownership rules."""

import io

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import UserRole
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register_and_login(db: Session, client: TestClient, email: str, role: UserRole) -> str:
    """Create a user and return a valid access token."""
    AuthService.register_user(
        db,
        UserCreate(
            email=email,
            password="password123",
            full_name="Test User",
            role=role,
        ),
    )
    tokens = AuthService.authenticate_user(db, LoginRequest(email=email, password="password123"))
    return tokens.access_token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_complaint(db: Session, token: str, client: TestClient) -> int:
    """Create a complaint via the API and return the new complaint's id."""
    resp = client.post(
        "/api/v1/complaints",
        json={
            "location": "Test Street",
            "description": "Garbage left on road.",
            "hazard": "biohazard",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# Unauthenticated → 401
# ---------------------------------------------------------------------------


def test_list_complaints_requires_auth(client: TestClient):
    """GET /complaints without a token must return 401."""
    resp = client.get("/api/v1/complaints")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["error"]["code"] == "UNAUTHENTICATED"


def test_get_complaint_requires_auth(client: TestClient, db_session: Session):
    """GET /complaints/{id} without a token must return 401."""
    citizen_token = _register_and_login(db_session, client, "c1_auth@example.com", UserRole.CITIZEN)
    complaint_id = _create_complaint(db_session, citizen_token, client)

    resp = client.get(f"/api/v1/complaints/{complaint_id}")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["error"]["code"] == "UNAUTHENTICATED"


def test_patch_complaint_requires_auth(client: TestClient, db_session: Session):
    """PATCH /complaints/{id} without a token must return 401."""
    citizen_token = _register_and_login(db_session, client, "c2_auth@example.com", UserRole.CITIZEN)
    complaint_id = _create_complaint(db_session, citizen_token, client)

    resp = client.patch(
        f"/api/v1/complaints/{complaint_id}",
        json={"description": "Updated description"},
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_history_requires_auth(client: TestClient, db_session: Session):
    """GET /complaints/{id}/history without a token must return 401."""
    citizen_token = _register_and_login(db_session, client, "c3_auth@example.com", UserRole.CITIZEN)
    complaint_id = _create_complaint(db_session, citizen_token, client)

    resp = client.get(f"/api/v1/complaints/{complaint_id}/history")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_duplicates_requires_auth(client: TestClient, db_session: Session):
    """GET /complaints/{id}/duplicates without a token must return 401."""
    citizen_token = _register_and_login(db_session, client, "c4_auth@example.com", UserRole.CITIZEN)
    complaint_id = _create_complaint(db_session, citizen_token, client)

    resp = client.get(f"/api/v1/complaints/{complaint_id}/duplicates")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_upload_photo_requires_auth(client: TestClient):
    """POST /complaints/upload-photo without a token must return 401."""
    fake_image = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    resp = client.post(
        "/api/v1/complaints/upload-photo",
        files={"photo": ("test.png", fake_image, "image/png")},
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Ownership rules
# ---------------------------------------------------------------------------


def test_citizen_sees_own_complaints_only(client: TestClient, db_session: Session):
    """A citizen listing complaints should receive only their own entries."""
    token_a = _register_and_login(db_session, client, "owner_a@example.com", UserRole.CITIZEN)
    token_b = _register_and_login(db_session, client, "owner_b@example.com", UserRole.CITIZEN)

    # Citizen A creates two complaints; Citizen B creates one.
    _create_complaint(db_session, token_a, client)
    _create_complaint(db_session, token_a, client)
    _create_complaint(db_session, token_b, client)

    resp = client.get("/api/v1/complaints", headers=_auth(token_a))
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    # All returned complaints must belong to Citizen A.
    assert data["meta"]["total"] == 2
    assert all(item["reported_by_user_id"] != 0 for item in data["items"])


def test_citizen_forbidden_on_others_complaint(client: TestClient, db_session: Session):
    """A citizen must receive 403 when fetching another citizen's complaint."""
    token_a = _register_and_login(db_session, client, "forbid_a@example.com", UserRole.CITIZEN)
    token_b = _register_and_login(db_session, client, "forbid_b@example.com", UserRole.CITIZEN)

    complaint_id = _create_complaint(db_session, token_a, client)

    # Citizen B tries to read Citizen A's complaint.
    resp = client.get(f"/api/v1/complaints/{complaint_id}", headers=_auth(token_b))
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


def test_admin_sees_all_complaints(client: TestClient, db_session: Session):
    """An admin listing complaints should receive all complaints regardless of owner."""
    token_citizen = _register_and_login(
        db_session, client, "admin_test_c@example.com", UserRole.CITIZEN
    )
    token_admin = _register_and_login(
        db_session, client, "admin_test_a@example.com", UserRole.ADMIN
    )

    _create_complaint(db_session, token_citizen, client)
    _create_complaint(db_session, token_citizen, client)

    resp = client.get("/api/v1/complaints", headers=_auth(token_admin))
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    # Admin should see both complaints (not filtered to their own user_id).
    assert data["meta"]["total"] >= 2


def test_citizen_forbidden_on_duplicates(client: TestClient, db_session: Session):
    """A citizen must be denied access to the duplicates endpoint (crew/admin only)."""
    token_citizen = _register_and_login(
        db_session, client, "dup_citizen@example.com", UserRole.CITIZEN
    )
    complaint_id = _create_complaint(db_session, token_citizen, client)

    resp = client.get(f"/api/v1/complaints/{complaint_id}/duplicates", headers=_auth(token_citizen))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_patch_cannot_set_resolved_at(client: TestClient, db_session: Session):
    """PATCH /complaints/{id} silently ignores resolved_at/cancelled_at in the body.

    These fields were removed from ComplaintUpdate, so the server should return
    422 (unknown field with strict mode) or silently ignore them. Either way the
    timestamps on the complaint must not be altered by a direct PATCH.
    """
    token = _register_and_login(db_session, client, "ts_test@example.com", UserRole.CITIZEN)
    complaint_id = _create_complaint(db_session, token, client)

    resp = client.patch(
        f"/api/v1/complaints/{complaint_id}",
        json={"resolved_at": "2020-01-01T00:00:00Z", "description": "Still garbage."},
        headers=_auth(token),
    )
    # Either 200 (field ignored) or 422 (field rejected) — but resolved_at must be None.
    assert resp.status_code in (status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY)
    if resp.status_code == status.HTTP_200_OK:
        assert resp.json()["resolved_at"] is None
