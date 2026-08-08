"""Regression coverage for endpoints called out in the sprint plan."""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import UserRole
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


def _token(db: Session, email: str, role: UserRole) -> str:
    AuthService.register_user(
        db,
        UserCreate(email=email, password="password123", full_name="Gap Test User", role=role),
    )
    return AuthService.authenticate_user(
        db, LoginRequest(email=email, password="password123")
    ).access_token


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_duplicate_check_returns_advisory_match(client: TestClient, db_session: Session):
    token = _token(db_session, "gap_duplicate@example.com", UserRole.CITIZEN)
    client.post(
        "/api/v1/complaints",
        json={"location": "12 Main Street", "description": "Overflowing garbage bin"},
        headers=_auth(token),
    )

    response = client.post(
        "/api/v1/complaints/duplicate-check",
        json={"location": "12 Main Street", "description": "Overflowing garbage bin"},
        headers=_auth(token),
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["complaint"]["title"] == "12 Main Street"


def test_duplicate_check_requires_authentication(client: TestClient):
    response = client.post(
        "/api/v1/complaints/duplicate-check",
        json={"location": "12 Main Street", "description": "Overflowing garbage bin"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_complaint_photo_is_attached_to_existing_complaint(client: TestClient, db_session: Session):
    token = _token(db_session, "gap_photo@example.com", UserRole.CITIZEN)
    complaint = client.post(
        "/api/v1/complaints",
        json={"location": "Photo Street", "description": "Litter"},
        headers=_auth(token),
    ).json()

    response = client.post(
        f"/api/v1/complaints/{complaint['id']}/photo",
        files={"photo": ("evidence.jpg", b"jpeg-bytes", "image/jpeg")},
        headers=_auth(token),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["photo_url"] == "evidence.jpg"


def test_task_status_endpoint_advances_and_rejects_invalid_transition(
    client: TestClient, db_session: Session
):
    token = _token(db_session, "gap_status@example.com", UserRole.CREW)
    admin_token = _token(db_session, "gap_status_admin@example.com", UserRole.ADMIN)
    task = client.post(
        "/api/v1/tasks",
        json={"title": "Status task"},
        headers=_auth(admin_token),
    ).json()

    started = client.patch(
        f"/api/v1/tasks/{task['id']}/status",
        json={"status": "in_progress"},
        headers=_auth(token),
    )
    assert started.status_code == status.HTTP_200_OK
    assert started.json()["status"] == "in_progress"

    invalid = client.patch(
        f"/api/v1/tasks/{task['id']}/status",
        json={"status": "assigned"},
        headers=_auth(token),
    )
    assert invalid.status_code == status.HTTP_409_CONFLICT


def test_assistance_request_is_persisted_and_closed_tasks_reject_it(
    client: TestClient, db_session: Session
):
    admin_token = _token(db_session, "gap_assistance_admin@example.com", UserRole.ADMIN)
    crew_token = _token(db_session, "gap_assistance_crew@example.com", UserRole.CREW)
    task = client.post(
        "/api/v1/tasks",
        json={"title": "Assistance task"},
        headers=_auth(admin_token),
    ).json()

    response = client.post(
        f"/api/v1/tasks/{task['id']}/assistance",
        json={"notes": "Need one additional worker"},
        headers=_auth(crew_token),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["assistance_requested"] is True
    assert response.json()["assistance_notes"] == "Need one additional worker"

    client.post(f"/api/v1/tasks/{task['id']}/complete", headers=_auth(crew_token))
    closed = client.post(
        f"/api/v1/tasks/{task['id']}/assistance",
        json={"notes": "Too late"},
        headers=_auth(crew_token),
    )
    assert closed.status_code == status.HTTP_409_CONFLICT
