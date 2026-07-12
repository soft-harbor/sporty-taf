from enum import StrEnum

from pydantic import BaseModel, Field


class ErrorType(StrEnum):
    INVALID_REQUEST = "invalid_request"
    INVALID_JSON = "invalid_json"
    INVALID_MATCH_ID = "invalid_match_id"
    INVALID_SELECTION = "invalid_selection"
    INVALID_STAKE_TYPE = "invalid_stake_type"
    INVALID_STAKE_PRECISION = "invalid_stake_precision"
    INVALID_STAKE_MIN = "invalid_stake_min"
    INVALID_STAKE_MAX = "invalid_stake_max"
    INVALID_MATCH = "invalid_match"
    INSUFFICIENT_BALANCE = "insufficient_balance"


class Error(BaseModel):
    error: ErrorType | str | None = Field(None, examples=["insufficient_balance"])
    message: str | None = Field(None, examples=["Insufficient balance"])
