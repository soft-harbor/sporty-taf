from pydantic import BaseModel, ConfigDict, Field

from api.models.selection import Selection
from constants import MAX_STAKE, MIN_STAKE


class PlaceBetRequest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )
    matchId: str = Field(..., examples=["premier-league-manutd-chelsea"])
    selection: Selection = Field(..., examples=["HOME"])
    stake: float = Field(..., ge=MIN_STAKE, le=MAX_STAKE, examples=[10])


class PlaceBetResponse(BaseModel):
    message: str = Field(..., examples=["Bet placed successfully"])
    matchId: str = Field(..., examples=["premier-league-manutd-chelsea"])
    selection: Selection = Field(..., examples=["HOME"])
    stake: float = Field(..., examples=[10])
    odds: float = Field(..., examples=[2.45])
    payout: float = Field(..., examples=[24.5])
    balance: float = Field(..., examples=[115.5])
    currency: str = Field(..., examples=["EUR"])
