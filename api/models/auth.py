from enum import StrEnum

from pydantic import BaseModel, Field


class AuthErrorType(StrEnum):
    MISSING_USER_ID = "missing_user_id"
    INVALID_USER_ID = "invalid_user_id"


class AuthError(BaseModel):
    error: AuthErrorType | None = Field(None, examples=["missing_user_id"])
