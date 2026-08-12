"""Claude-powered hazard classification for complaints, with a heuristic fallback (US-28/29/30).

Calling the Claude API is inherently unreliable from this service's point of
view: the key may be unset, the network may be down, the model may refuse, or
it may return something that doesn't parse. None of those are bugs in this
code, so none of them should raise — every path degrades to a deterministic
keyword-based classification instead. This mirrors the "must degrade
gracefully when unset" rule already documented on ``settings.anthropic_api_key``.
"""

from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.complaint import Complaint, ComplaintCategory
from app.repositories.complaint_repository import ComplaintRepository

__all__ = ["ClassificationResult", "ComplaintClassificationService"]

logger = logging.getLogger(__name__)

_CLAUDE_MODEL = "claude-opus-5"

# Ordered so the first match wins; checked against "description + address" in
# lowercase. Intentionally simple — this is the fallback path, not the feature.
_KEYWORD_RULES: list[tuple[str, ComplaintCategory]] = [
    ("mosquito", ComplaintCategory.MOSQUITO_BREEDING),
    ("stagnant water", ComplaintCategory.MOSQUITO_BREEDING),
    ("standing water", ComplaintCategory.MOSQUITO_BREEDING),
    ("child", ComplaintCategory.RISK_TO_CHILDREN),
    ("school", ComplaintCategory.RISK_TO_CHILDREN),
    ("playground", ComplaintCategory.RISK_TO_CHILDREN),
    ("smell", ComplaintCategory.FOUL_SMELL),
    ("odor", ComplaintCategory.FOUL_SMELL),
    ("odour", ComplaintCategory.FOUL_SMELL),
    ("stench", ComplaintCategory.FOUL_SMELL),
    ("overflow", ComplaintCategory.OVERFLOWING_BIN),
    ("bin full", ComplaintCategory.OVERFLOWING_BIN),
    ("spilling", ComplaintCategory.OVERFLOWING_BIN),
]


class ClassificationResult:
    """Outcome of a classification attempt, regardless of which path produced it."""

    __slots__ = ("category", "source", "confidence", "reasoning")

    def __init__(
        self,
        category: ComplaintCategory,
        source: str,
        confidence: float | None = None,
        reasoning: str | None = None,
    ) -> None:
        self.category = category
        self.source = source
        self.confidence = confidence
        self.reasoning = reasoning


class ComplaintClassificationService:
    @staticmethod
    def classify(db: Session, complaint: Complaint) -> ClassificationResult:
        """Classify ``complaint`` and persist the resulting category."""
        result = ComplaintClassificationService._classify_with_claude(complaint)
        if result is None:
            result = ComplaintClassificationService._classify_with_heuristic(complaint)

        ComplaintRepository.update(db, complaint, {"category": result.category.value})
        return result

    @staticmethod
    def _classify_with_claude(complaint: Complaint) -> ClassificationResult | None:
        if not settings.anthropic_api_key:
            return None

        try:
            import anthropic
        except ImportError:
            logger.warning("anthropic package not installed; using heuristic classification.")
            return None

        allowed = [category.value for category in ComplaintCategory]
        try:
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model=_CLAUDE_MODEL,
                max_tokens=256,
                thinking={"type": "disabled"},
                output_config={
                    "effort": "low",
                    "format": {
                        "type": "json_schema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string", "enum": allowed},
                                "confidence": {"type": "number"},
                            },
                            "required": ["category", "confidence"],
                            "additionalProperties": False,
                        },
                    },
                },
                system=(
                    "You classify municipal waste-complaint reports into a hazard "
                    "category so cleanup crews can prioritize correctly. Choose the "
                    "single best-fitting category from the fixed set provided."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Complaint description: {complaint.description}\n"
                            f"Location: {complaint.address or 'unknown'}\n"
                            "Classify the hazard category for this complaint."
                        ),
                    }
                ],
            )
        except Exception:  # noqa: BLE001 - any failure here degrades to the heuristic
            logger.exception("Claude classification request failed; using heuristic fallback.")
            return None

        if response.stop_reason == "refusal":
            logger.warning("Claude declined the classification request; using heuristic fallback.")
            return None

        text = next((block.text for block in response.content if block.type == "text"), "")
        try:
            data = json.loads(text)
            category = ComplaintCategory(data["category"])
            confidence = float(data["confidence"])
        except (json.JSONDecodeError, KeyError, ValueError):
            logger.warning("Claude returned an unparseable classification %r; using heuristic.", text)
            return None

        return ClassificationResult(category=category, source="llm", confidence=confidence)

    @staticmethod
    def _classify_with_heuristic(complaint: Complaint) -> ClassificationResult:
        haystack = f"{complaint.description} {complaint.address or ''}".lower()
        for keyword, category in _KEYWORD_RULES:
            if keyword in haystack:
                return ClassificationResult(
                    category=category,
                    source="heuristic",
                    reasoning=f"matched keyword '{keyword}'",
                )
        return ClassificationResult(
            category=ComplaintCategory.NONE,
            source="heuristic",
            reasoning="no hazard keywords matched",
        )
