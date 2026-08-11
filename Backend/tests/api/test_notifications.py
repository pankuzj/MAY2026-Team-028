"""API integration tests for notification routes (S2-F02, US-06/US-23)."""

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
    AuthService.register_user(
        db,
        UserCreate(email=email, password="password123", full_name="Test User", role=role),
    )
    tokens = AuthService.authenticate_user(db, LoginRequest(email=email, password="password123"))
    return tokens.access_token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_complaint(client: TestClient, token: str) -> int:
    resp = client.post(
        "/api/v1/complaints",
        json={
            "location": "Test Street",
            "description": "Garbage left on road.",
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


# ---------------------------------------------------------------------------
# GET /notifications, and the complaint_resolved auto-notify hook
# ---------------------------------------------------------------------------


def test_list_notifications_happy_path(client: TestClient, db_session: Session):
    """Happy Path: resolving a complaint auto-creates a notification the reporter can list."""
    citizen_token = _register_and_login(
        db_session, client, "notif_citizen@example.com", UserRole.CITIZEN
    )
    admin_token = _register_and_login(db_session, client, "notif_admin@example.com", UserRole.ADMIN)
    complaint_id = _create_complaint(client, citizen_token)
    _resolve_complaint(client, admin_token, complaint_id)

    resp = client.get("/api/v1/notifications", headers=_auth(citizen_token))
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["type"] == "complaint_resolved"
    assert data["items"][0]["related_complaint_id"] == complaint_id
    assert data["items"][0]["is_read"] is False


def test_list_notifications_requires_auth(client: TestClient):
    """Validation/Auth Failure: GET without a token returns 401."""
    resp = client.get("/api/v1/notifications")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_notifications_scoped_to_user(client: TestClient, db_session: Session):
    """Auth/RBAC: a user only sees their own notifications, never someone else's."""
    citizen_token = _register_and_login(
        db_session, client, "notif_owner@example.com", UserRole.CITIZEN
    )
    other_token = _register_and_login(
        db_session, client, "notif_other@example.com", UserRole.CITIZEN
    )
    admin_token = _register_and_login(
        db_session, client, "notif_admin2@example.com", UserRole.ADMIN
    )
    complaint_id = _create_complaint(client, citizen_token)
    _resolve_complaint(client, admin_token, complaint_id)

    resp = client.get("/api/v1/notifications", headers=_auth(other_token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["meta"]["total"] == 0


def test_list_notifications_edge_case_unread_only(client: TestClient, db_session: Session):
    """Edge Case: unread_only filter excludes a notification after it is marked read."""
    citizen_token = _register_and_login(
        db_session, client, "notif_unread@example.com", UserRole.CITIZEN
    )
    admin_token = _register_and_login(
        db_session, client, "notif_admin3@example.com", UserRole.ADMIN
    )
    complaint_id = _create_complaint(client, citizen_token)
    _resolve_complaint(client, admin_token, complaint_id)

    listed = client.get("/api/v1/notifications", headers=_auth(citizen_token)).json()
    notification_id = listed["items"][0]["id"]
    client.patch(f"/api/v1/notifications/{notification_id}/read", headers=_auth(citizen_token))

    resp = client.get("/api/v1/notifications?unread_only=true", headers=_auth(citizen_token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["meta"]["total"] == 0


# ---------------------------------------------------------------------------
# PATCH /notifications/{id}/read
# ---------------------------------------------------------------------------


def test_mark_notification_read_happy_path(client: TestClient, db_session: Session):
    """Happy Path: owner marks their notification read."""
    citizen_token = _register_and_login(
        db_session, client, "notif_read@example.com", UserRole.CITIZEN
    )
    admin_token = _register_and_login(
        db_session, client, "notif_admin4@example.com", UserRole.ADMIN
    )
    complaint_id = _create_complaint(client, citizen_token)
    _resolve_complaint(client, admin_token, complaint_id)
    notification_id = client.get("/api/v1/notifications", headers=_auth(citizen_token)).json()[
        "items"
    ][0]["id"]

    resp = client.patch(
        f"/api/v1/notifications/{notification_id}/read", headers=_auth(citizen_token)
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["is_read"] is True
    assert data["read_at"] is not None


def test_mark_notification_read_validation_failure(client: TestClient, db_session: Session):
    """Validation Failure: non-integer notification id returns 422."""
    citizen_token = _register_and_login(
        db_session, client, "notif_read_val@example.com", UserRole.CITIZEN
    )
    resp = client.patch("/api/v1/notifications/not-an-id/read", headers=_auth(citizen_token))
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_mark_notification_read_rbac_failure(client: TestClient, db_session: Session):
    """Auth/RBAC Failure: a different user cannot mark someone else's notification read."""
    citizen_token = _register_and_login(
        db_session, client, "notif_read_owner@example.com", UserRole.CITIZEN
    )
    other_token = _register_and_login(
        db_session, client, "notif_read_other@example.com", UserRole.CITIZEN
    )
    admin_token = _register_and_login(
        db_session, client, "notif_admin5@example.com", UserRole.ADMIN
    )
    complaint_id = _create_complaint(client, citizen_token)
    _resolve_complaint(client, admin_token, complaint_id)
    notification_id = client.get("/api/v1/notifications", headers=_auth(citizen_token)).json()[
        "items"
    ][0]["id"]

    resp = client.patch(f"/api/v1/notifications/{notification_id}/read", headers=_auth(other_token))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_mark_notification_read_edge_case_idempotent(client: TestClient, db_session: Session):
    """Edge Case: marking an already-read notification read again returns 200 idempotently."""
    citizen_token = _register_and_login(
        db_session, client, "notif_read_idem@example.com", UserRole.CITIZEN
    )
    admin_token = _register_and_login(
        db_session, client, "notif_admin6@example.com", UserRole.ADMIN
    )
    complaint_id = _create_complaint(client, citizen_token)
    _resolve_complaint(client, admin_token, complaint_id)
    notification_id = client.get("/api/v1/notifications", headers=_auth(citizen_token)).json()[
        "items"
    ][0]["id"]

    client.patch(f"/api/v1/notifications/{notification_id}/read", headers=_auth(citizen_token))
    resp = client.patch(
        f"/api/v1/notifications/{notification_id}/read", headers=_auth(citizen_token)
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["is_read"] is True


def test_mark_notification_read_edge_case_not_found(client: TestClient, db_session: Session):
    """Edge Case: marking a non-existent notification returns 404."""
    citizen_token = _register_and_login(
        db_session, client, "notif_read_404@example.com", UserRole.CITIZEN
    )
    resp = client.patch("/api/v1/notifications/999999/read", headers=_auth(citizen_token))
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# POST /notifications/read-all
# ---------------------------------------------------------------------------


def test_mark_all_notifications_read_happy_path(client: TestClient, db_session: Session):
    """Happy Path: mark-all-read flips every unread notification for the caller."""
    citizen_token = _register_and_login(
        db_session, client, "notif_all@example.com", UserRole.CITIZEN
    )
    admin_token = _register_and_login(
        db_session, client, "notif_admin7@example.com", UserRole.ADMIN
    )
    complaint_id_1 = _create_complaint(client, citizen_token)
    complaint_id_2 = _create_complaint(client, citizen_token)
    _resolve_complaint(client, admin_token, complaint_id_1)
    _resolve_complaint(client, admin_token, complaint_id_2)

    resp = client.post("/api/v1/notifications/read-all", headers=_auth(citizen_token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["marked"] == 2

    listed = client.get("/api/v1/notifications?unread_only=true", headers=_auth(citizen_token))
    assert listed.json()["meta"]["total"] == 0


def test_mark_all_notifications_read_requires_auth(client: TestClient):
    """Validation/Auth Failure: mark-all-read without a token returns 401."""
    resp = client.post("/api/v1/notifications/read-all")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_mark_all_notifications_read_edge_case_empty(client: TestClient, db_session: Session):
    """Edge Case: mark-all-read with zero notifications returns marked=0."""
    citizen_token = _register_and_login(
        db_session, client, "notif_all_empty@example.com", UserRole.CITIZEN
    )
    resp = client.post("/api/v1/notifications/read-all", headers=_auth(citizen_token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["marked"] == 0


def test_notify_duplicate_detected_emitter(client: TestClient, db_session: Session):
    """Notification emitter test: emitting duplicate detected notification creates inbox item."""
    citizen_token = _register_and_login(
        db_session, client, "notif_dup_emitter@example.com", UserRole.CITIZEN
    )
    complaint_id = _create_complaint(client, citizen_token)
    from app.services.complaint_service import ComplaintService
    from app.services.notification_service import NotificationService

    complaint = ComplaintService.get_complaint(db_session, complaint_id)
    notif = NotificationService.notify_duplicate_detected(db_session, complaint)

    assert notif.type == "duplicate_detected"
    assert notif.user_id == complaint.reported_by_user_id
    assert notif.related_complaint_id == complaint_id

    resp = client.get("/api/v1/notifications", headers=_auth(citizen_token))
    assert resp.status_code == status.HTTP_200_OK
    items = resp.json()["items"]
    assert any(
        item["type"] == "duplicate_detected" and item["related_complaint_id"] == complaint_id
        for item in items
    )


def test_notify_complaint_resolved_emitter(client: TestClient, db_session: Session):
    """Notification emitter test: resolving complaint emits complaint_resolved notification."""
    citizen_token = _register_and_login(
        db_session, client, "notif_res_emitter@example.com", UserRole.CITIZEN
    )
    admin_token = _register_and_login(
        db_session, client, "notif_admin_res@example.com", UserRole.ADMIN
    )
    complaint_id = _create_complaint(client, citizen_token)
    _resolve_complaint(client, admin_token, complaint_id)

    resp = client.get("/api/v1/notifications", headers=_auth(citizen_token))
    assert resp.status_code == status.HTTP_200_OK
    items = resp.json()["items"]
    assert any(
        item["type"] == "complaint_resolved" and item["related_complaint_id"] == complaint_id
        for item in items
    )

