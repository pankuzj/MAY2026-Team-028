"""Smoke tests for the application skeleton.

These cover the foundation tasks (S1-F02/F03/F05/F06/F07) rather than any user
story. They are what turns "CI is green" into a real statement: they prove the
app builds, middleware runs, the database is reachable, and every error path
returns the shared envelope.

They also keep CI honest for a second, less obvious reason: ``pytest`` exits with
code 5 when it collects zero tests, which fails the build. Until the first real
endpoint lands, these are the tests keeping the pipeline meaningful.
"""

from fastapi.testclient import TestClient


class TestLiveness:
    """GET /health/live — process is up."""

    def test_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health/live")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["env"] == "test"  # proves conftest's env override took effect

    def test_needs_no_authentication(self, client: TestClient) -> None:
        """A probe that required a token would be useless to Docker and CI."""
        assert "Authorization" not in client.headers
        assert client.get("/health/live").status_code == 200


class TestReadiness:
    """GET /health/ready — process is up *and* the database answers."""

    def test_reports_database_reachable(self, client: TestClient) -> None:
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready", "database": "ok"}


class TestRequestIdMiddleware:
    """S1-F06 — every response carries a correlation id."""

    def test_response_carries_a_generated_request_id(self, client: TestClient) -> None:
        request_id = client.get("/health/live").headers.get("X-Request-ID")
        assert request_id
        assert len(request_id) == 16

    def test_inbound_request_id_is_reused_not_replaced(self, client: TestClient) -> None:
        """Reuse is what lets one id span the frontend and the backend."""
        response = client.get("/health/live", headers={"X-Request-ID": "frontend-trace-001"})
        assert response.headers["X-Request-ID"] == "frontend-trace-001"

    def test_ids_differ_between_requests(self, client: TestClient) -> None:
        first = client.get("/health/live").headers["X-Request-ID"]
        second = client.get("/health/live").headers["X-Request-ID"]
        assert first != second


class TestErrorEnvelope:
    """S1-F05 — framework-raised errors use our envelope, not Starlette's.

    Without the registered handlers these would return ``{"detail": "Not Found"}``,
    and the frontend would need a second error-parsing branch.
    """

    def test_unknown_path_returns_enveloped_404(self, client: TestClient) -> None:
        response = client.get("/api/v1/there-is-no-such-endpoint")
        assert response.status_code == 404

        body = response.json()
        assert set(body) == {"error"}, "envelope must have exactly one top-level key"
        assert body["error"]["code"] == "NOT_FOUND"
        assert body["error"]["details"] == []
        assert body["error"]["request_id"] == response.headers["X-Request-ID"]

    def test_wrong_method_returns_enveloped_405(self, client: TestClient) -> None:
        response = client.post("/health/live")
        assert response.status_code == 405
        assert response.json()["error"]["code"] == "METHOD_NOT_ALLOWED"

    def test_request_id_in_body_matches_the_header(self, client: TestClient) -> None:
        """The whole point of the id: a user reads it off a toast, we grep logs."""
        response = client.get("/nope", headers={"X-Request-ID": "traceable-id-42"})
        assert response.json()["error"]["request_id"] == "traceable-id-42"


class TestOpenApiDocument:
    """FastAPI's generated spec — cross-checked against docs/sprint-1/openapi.yaml."""

    def test_docs_are_served_outside_production(self, client: TestClient) -> None:
        assert client.get("/docs").status_code == 200

    def test_spec_is_generated_and_titled(self, client: TestClient) -> None:
        spec = client.get("/openapi.json").json()
        assert spec["info"]["title"] == "SmartSweep API"
        assert "/health/live" in spec["paths"]

    def test_health_operations_have_stable_operation_ids(self, client: TestClient) -> None:
        """Explicit operationIds keep generated client method names readable."""
        spec = client.get("/openapi.json").json()
        assert spec["paths"]["/health/live"]["get"]["operationId"] == "healthLive"
        assert spec["paths"]["/health/ready"]["get"]["operationId"] == "healthReady"
