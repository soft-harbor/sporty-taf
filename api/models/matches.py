from datetime import date

from pydantic import BaseModel, Field

from api.models.selection import Selection


class Odds(BaseModel):
    home: float = Field(..., examples=[2.45])
    draw: float = Field(..., examples=[3.1])
    away: float = Field(..., examples=[2.8])


class Match(BaseModel):
    id: str = Field(..., examples=["premier-league-manutd-chelsea"])
    competition: str | None = Field(None, examples=["Premier League"])
    kickoffDate: date | None = Field(None, examples=["2026-01-30"])
    homeTeam: str = Field(..., examples=["Manchester Utd"])
    awayTeam: str = Field(..., examples=["Chelsea"])
    odds: Odds = Field(...)

    def odds_for(self, selection: Selection) -> float:
        match selection:
            case Selection.HOME:
                return self.odds.home
            case Selection.DRAW:
                return self.odds.draw
            case Selection.AWAY:
                return self.odds.away
