"""Pydantic v2 DTOs — the API contract for requests and responses."""

from app.schemas.auth import LoginRequest, RefreshTokenRequest, Token
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
