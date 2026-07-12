import re

from api.models.selection import Selection

BET_SLIP_SELECTION_LABELS: dict[Selection, str] = {
    Selection.HOME: "Home",
    Selection.DRAW: "Draw",
    Selection.AWAY: "Away",
}

SELECTION_UI_LABELS: dict[Selection, str] = {
    Selection.HOME: "1",
    Selection.DRAW: "X",
    Selection.AWAY: "2",
}


def format_match_teams(home_team: str, away_team: str) -> str:
    return f"{home_team} vs {away_team}"


def bet_slip_market_label(selection: Selection) -> str:
    return f"Match Winner: {BET_SLIP_SELECTION_LABELS[selection]}"


def ui_label_for(selection: Selection) -> str:
    return SELECTION_UI_LABELS[selection]


def parse_eur_amount(text: str) -> float | int:
    """Parse a monetary value from UI text such as 'Balance: €125.50' or '€10.00'."""
    match = re.search(r"[\d]+(?:\.\d+)?", text.replace(",", ""))
    if not match:
        raise ValueError(f"Could not parse EUR amount from: {text!r}")
    return float(match.group())
