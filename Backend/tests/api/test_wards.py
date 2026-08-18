"""API tests for public ward lookup and authenticated /wards/me behavior."""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.ward import Ward
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


def _register_and_login(db: Session, email: str, role: UserRole) -> str:
    AuthService.register_user(
        db,
        UserCreate(email=email, password="password123", full_name="Ward User", role=role),
    )
    return AuthService.authenticate_user(
        db, LoginRequest(email=email, password="password123")
    ).access_token


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_ward(db: Session) -> Ward:
    ward = Ward(name="Ward 12", code="W12", zone="West")
    db.add(ward)
    db.commit()
    db.refresh(ward)
    return ward


def test_list_wards_returns_empty_list_for_empty_database(client: TestClient):
    response = client.get("/api/v1/wards")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_and_get_ward_return_serialized_ward(client: TestClient, db_session: Session):
    ward = _create_ward(db_session)

    listed = client.get("/api/v1/wards")
    fetched = client.get(f"/api/v1/wards/{ward.id}")

    assert listed.status_code == status.HTTP_200_OK
    assert listed.json()[0]["code"] == "W12"
    assert fetched.status_code == status.HTTP_200_OK
    assert fetched.json()["name"] == "Ward 12"


def test_get_ward_not_found_and_invalid_id(client: TestClient):
    missing = client.get("/api/v1/wards/999999")
    invalid = client.get("/api/v1/wards/not-an-id")

    assert missing.status_code == status.HTTP_404_NOT_FOUND
    assert missing.json()["error"]["code"] == "NOT_FOUND"
    assert invalid.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_my_ward_requires_authentication(client: TestClient):
    response = client.get("/api/v1/wards/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_my_ward_returns_users_ward(client: TestClient, db_session: Session):
    ward = _create_ward(db_session)
    token = _register_and_login(db_session, "ward_user@example.com", UserRole.CITIZEN)
    user = db_session.query(User).filter_by(email="ward_user@example.com").one()
    user.ward_id = ward.id
    db_session.commit()

    response = client.get("/api/v1/wards/me", headers=_auth(token))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == ward.id


def test_get_my_ward_returns_not_found_when_user_has_no_ward(
    client: TestClient, db_session: Session
):
    token = _register_and_login(db_session, "wardless_user@example.com", UserRole.CITIZEN)

    response = client.get("/api/v1/wards/me", headers=_auth(token))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_my_ward_returns_not_found_when_assigned_ward_is_missing(
    client: TestClient, db_session: Session
):
    token = _register_and_login(db_session, "stale_ward_user@example.com", UserRole.CITIZEN)
    user = db_session.query(User).filter_by(email="stale_ward_user@example.com").one()
    user.ward_id = 999999
    db_session.commit()

    response = client.get("/api/v1/wards/me", headers=_auth(token))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["error"]["code"] == "NOT_FOUND"
