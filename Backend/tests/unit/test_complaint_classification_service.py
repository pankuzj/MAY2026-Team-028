"""Focused tests for Claude classification and deterministic fallback paths."""

import json
from unittest.mock import MagicMock, patch

from app.models.complaint import Complaint, ComplaintCategory
from app.models.user import User
from app.services.complaint_classification_service import ComplaintClassificationService


def _complaint(description: str, address: str = "Ward 1") -> Complaint:
    return Complaint(description=description, address=address, title="Test complaint")


def test_heuristic_classification_matches_keywords_and_persists(db_session):
    complaint = _complaint("There is stagnant water near the school playground.")
    user = User(email="classifier@example.com", hashed_password="hash", full_name="Classifier")
    db_session.add(user)
    db_session.flush()
    complaint.reported_by_user_id = user.id
    db_session.add(complaint)
    db_session.commit()

    with patch("app.core.config.settings.anthropic_api_key", None):
        result = ComplaintClassificationService.classify(db_session, complaint)

    assert result.category is ComplaintCategory.MOSQUITO_BREEDING
    assert result.source == "heuristic"
    assert complaint.category == ComplaintCategory.MOSQUITO_BREEDING.value


def test_heuristic_classification_returns_none_for_unknown_text():
    complaint = _complaint("A damaged public bench needs repair.")

    with patch("app.core.config.settings.anthropic_api_key", None):
        result = ComplaintClassificationService._classify_with_claude(complaint)
        assert result is None
        result = ComplaintClassificationService._classify_with_heuristic(complaint)

    assert result.category is ComplaintCategory.NONE
    assert result.reasoning == "no hazard keywords matched"


def test_claude_success_returns_llm_result():
    complaint = _complaint("Waste is overflowing beside the market.")
    block = MagicMock(type="text", text=json.dumps({"category": "Foul Smell", "confidence": 0.91}))
    response = MagicMock(stop_reason="end_turn", content=[block])

    with patch("app.core.config.settings.anthropic_api_key", "test-key"):
        with patch("anthropic.Anthropic") as anthropic_cls:
            anthropic_cls.return_value.messages.create.return_value = response
            result = ComplaintClassificationService._classify_with_claude(complaint)

    assert result is not None
    assert result.category is ComplaintCategory.FOUL_SMELL
    assert result.source == "llm"
    assert result.confidence == 0.91


def test_claude_refusal_falls_back_to_heuristic():
    complaint = _complaint("The bin is overflowing onto the sidewalk.")
    response = MagicMock(stop_reason="refusal", content=[])

    with patch("app.core.config.settings.anthropic_api_key", "test-key"):
        with patch("anthropic.Anthropic") as anthropic_cls:
            anthropic_cls.return_value.messages.create.return_value = response
            result = ComplaintClassificationService._classify_with_claude(complaint)

    assert result is None
    assert (
        ComplaintClassificationService._classify_with_heuristic(complaint).category
        is ComplaintCategory.OVERFLOWING_BIN
    )


def test_claude_request_exception_falls_back():
    complaint = _complaint("There is a strong odor near the school.")

    with patch("app.core.config.settings.anthropic_api_key", "test-key"):
        with patch("anthropic.Anthropic", side_effect=RuntimeError("network unavailable")):
            result = ComplaintClassificationService._classify_with_claude(complaint)

    assert result is None
    assert (
        ComplaintClassificationService._classify_with_heuristic(complaint).category
        is ComplaintCategory.RISK_TO_CHILDREN
    )


def test_claude_invalid_json_falls_back():
    complaint = _complaint("There is a bad smell near the drain.")
    block = MagicMock(type="text", text="not-json")
    response = MagicMock(stop_reason="end_turn", content=[block])

    with patch("app.core.config.settings.anthropic_api_key", "test-key"):
        with patch("anthropic.Anthropic") as anthropic_cls:
            anthropic_cls.return_value.messages.create.return_value = response
            result = ComplaintClassificationService._classify_with_claude(complaint)

    assert result is None
