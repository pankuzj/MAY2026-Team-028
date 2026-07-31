"""Pydantic v2 DTOs — the API contract for requests and responses."""

from app.schemas.auth import LoginRequest, RefreshTokenRequest, Token
from app.schemas.complaint import (
    ComplaintBase,
    ComplaintCreate,
    ComplaintFilter,
    ComplaintRead,
    ComplaintStatus,
    ComplaintStatusHistoryRead,
    ComplaintSubmit,
    ComplaintUpdate,
)
from app.schemas.common import (
    ErrorDetail,
    ErrorPayload,
    ErrorResponse,
    Page,
    PageMeta,
    error_response,
)
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.ward import WardBase, WardCreate, WardRead, WardUpdate

__all__ = [
    "ComplaintBase",
    "ComplaintCreate",
    "ComplaintFilter",
    "ComplaintRead",
    "ComplaintStatus",
    "ComplaintStatusHistoryRead",
    "ComplaintSubmit",
    "ComplaintUpdate",
    "ErrorDetail",
    "ErrorPayload",
    "ErrorResponse",
    "LoginRequest",
    "Page",
    "PageMeta",
    "RefreshTokenRequest",
    "Token",
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "WardBase",
    "WardCreate",
    "WardRead",
    "WardUpdate",
    "error_response",
]
