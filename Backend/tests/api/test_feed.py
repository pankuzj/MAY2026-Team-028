"""API integration tests for public feed routes (/feed)."""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import UserRole
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


def _register_and_login(db: Session, client: TestClient, email: str, role: UserRole) -> str:
    AuthService.register_user(
        db,
        UserCreate(email=email, password="password123", full_name="Feed User", role=role),
    )
    tokens = AuthService.authenticate_user(db, LoginRequest(email=email, password="password123"))
    return tokens.access_token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_complaint(client: TestClient, token: str) -> int:
    resp = client.post(
        "/api/v1/complaints",
        json={
            "location": "Feed Street",
            "description": "Garbage issue",
            "hazard": "biohazard",
        },
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    return resp.json()["id"]


def _resolve_complaint(client: TestClient, admin_token: str, complaint_id: int) -> None:
    for target in ("in_progress", "resolved"):
        resp = client.patch(
            f"/api/v1/complaints/{complaint_id}/status",
            json={"status_value": target},
            headers=_auth(admin_token),
        )
        assert resp.status_code == status.HTTP_200_OK, resp.text


def _create_post(client: TestClient, admin_token: str, complaint_id: int) -> int:
    resp = client.post(
        "/api/v1/transparency",
        json={"complaint_id": complaint_id, "title": "Cleanup completed"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# GET /feed
# ---------------------------------------------------------------------------


def test_get_feed_happy_path(client: TestClient, db_session: Session):
    """Happy Path: GET /feed returns paginated public feed posts without requiring auth."""
    citizen_token = _register_and_login(db_session, client, "feed_cit@example.com", UserRole.CITIZEN)
    admin_token = _register_and_login(db_session, client, "feed_adm@example.com", UserRole.ADMIN)
    cid = _create_complaint(client, citizen_token)
    _resolve_complaint(client, admin_token, cid)
    post_id = _create_post(client, admin_token, cid)

    resp = client.get("/api/v1/feed")
    assert resp.status_code == status.HTTP_200_OK, resp.text
    data = resp.json()
    assert "items" in data
    assert "meta" in data
    assert data["meta"]["total"] >= 1
    assert any(p["id"] == post_id for p in data["items"])


def test_get_feed_with_ward_filter(client: TestClient, db_session: Session):
    """Happy Path: GET /feed?ward_id=999 returns empty list when no posts in that ward."""
    resp = client.get("/api/v1/feed?ward_id=999")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["meta"]["total"] == 0
