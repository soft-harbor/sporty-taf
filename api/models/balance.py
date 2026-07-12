from pydantic import BaseModel, Field


class Balance(BaseModel):
    message: str | None = Field(None, examples=["Balance reset successfully"])
    balance: float = Field(..., examples=[125.5])
    currency: str = Field(..., examples=["EUR"])
