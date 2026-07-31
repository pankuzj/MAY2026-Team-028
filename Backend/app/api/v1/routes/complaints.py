"""Complaint API routes."""

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.complaint import Complaint
from app.models.user import User
from app.repositories.complaint_repository import ComplaintRepository
from app.schemas.common import Page
from app.schemas.complaint import (
    ComplaintRead,
    ComplaintStatus,
    ComplaintStatusHistoryRead,
    ComplaintSubmit,
    ComplaintUpdate,
)
from app.services.complaint_service import ComplaintService
from app.services.duplicate_detection_service import DuplicateDetectionService

router = APIRouter(prefix="/complaints", tags=["Complaints"])


def _to_read_model(complaint: Complaint) -> ComplaintRead:
    return ComplaintRead.model_validate(complaint)


@router.post("", response_model=ComplaintRead, status_code=status.HTTP_201_CREATED)
def create_complaint(
    complaint_in: ComplaintSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplaintRead:
    complaint = ComplaintService.create_complaint(db, current_user, complaint_in)
    return _to_read_model(complaint)


@router.get("", response_model=Page[ComplaintRead])
def list_complaints(
    db: Session = Depends(get_db),
    search: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    ward_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> Page[ComplaintRead]:
    items, total = ComplaintService.list_complaints(
        db,
        filters={
            "search": search,
            "status": status_filter,
            "ward_id": ward_id,
            "page": page,
            "page_size": page_size,
        },
    )
    return Page[ComplaintRead].build([_to_read_model(item) for item in items], page=page, page_size=page_size, total=total)


# NOTE: literal paths must stay above "/{complaint_id}". Starlette matches routes
# in registration order, so a "/high-risk" declared below the parameterised route
# would be swallowed by it and fail int coercion with a 422.


@router.get("/high-risk", response_model=Page[ComplaintRead])
def high_risk_complaints(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
) -> Page[ComplaintRead]:
    items, total = ComplaintService.list_complaints(
        db,
        filters={
            "page": 1,
            "page_size": 500,
        },
    )
    high_risk = [
        item
        for item in items
        if (item.category or "").lower() in {"biohazard", "risk to children", "medical waste", "mosquito breeding"}
        or (item.priority or "").lower() in {"high", "urgent", "critical"}
    ]
    start = (page - 1) * page_size
    end = start + page_size
    sliced = high_risk[start:end]
    return Page[ComplaintRead].build([_to_read_model(item) for item in sliced], page=page, page_size=page_size, total=len(high_risk))


@router.post("/upload-photo")
async def upload_complaint_photo(photo: UploadFile = File(...)) -> dict[str, object]:
    content_type = (photo.content_type or "").lower()
    if content_type not in settings.upload_allowed_mime_type_set:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported image type.")

    contents = await photo.read()
    if len(contents) > settings.upload_max_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image too large.")

    return {
        "filename": photo.filename,
        "content_type": content_type,
        "size_bytes": len(contents),
    }


@router.get("/{complaint_id}", response_model=ComplaintRead)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)) -> ComplaintRead:
    return _to_read_model(ComplaintService.get_complaint(db, complaint_id))


@router.patch("/{complaint_id}", response_model=ComplaintRead)
def update_complaint(
    complaint_id: int,
    complaint_in: ComplaintUpdate,
    db: Session = Depends(get_db),
) -> ComplaintRead:
    return _to_read_model(ComplaintService.update_complaint(db, complaint_id, complaint_in))


@router.patch("/{complaint_id}/status", response_model=ComplaintRead, status_code=status.HTTP_200_OK)
def change_complaint_status(
    complaint_id: int,
    status_value: ComplaintStatus = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplaintRead:
    return _to_read_model(
        ComplaintService.change_status(
            db,
            complaint_id,
            status_value,
            changed_by_user_id=current_user.id,
        )
    )


@router.post("/{complaint_id}/cancel", response_model=ComplaintRead, status_code=status.HTTP_200_OK)
def cancel_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplaintRead:
    return _to_read_model(
        ComplaintService.cancel_complaint(db, complaint_id, changed_by_user_id=current_user.id)
    )


@router.get("/{complaint_id}/history", response_model=list[ComplaintStatusHistoryRead])
def complaint_history(
    complaint_id: int,
    db: Session = Depends(get_db),
) -> list[ComplaintStatusHistoryRead]:
    ComplaintService.get_complaint(db, complaint_id)
    return [
        ComplaintStatusHistoryRead.model_validate(history)
        for history in ComplaintRepository.get_history(db, complaint_id)
    ]


@router.get("/{complaint_id}/duplicates")
def get_duplicates(complaint_id: int, db: Session = Depends(get_db)) -> list[dict]:
    complaint = ComplaintService.get_complaint(db, complaint_id)
    matches = DuplicateDetectionService.find_possible_duplicates(db, complaint)
    # The service hands back the matched ORM row under "complaint"; convert it to
    # the read DTO so the response is JSON-serialisable.
    return [
        {**match, "complaint": _to_read_model(match["complaint"]).model_dump(mode="json")}
        for match in matches
    ]
