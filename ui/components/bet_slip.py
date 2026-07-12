from pytest_check import check
from selenium.webdriver.common.by import By

from api.models.selection import Selection
from ui.core.base_component import BaseComponent
from ui.core.locators import loc
from ui.core.timeouts import DEFAULT_TIMEOUT
from ui.helpers import bet_slip_market_label, format_match_teams, parse_eur_amount
from utils.money import round_money

PLACING_TEXT = "Placing"


class BetSlip(BaseComponent):
    selection_teams = loc((By.CSS_SELECTOR, ".betSelectionTeams"))
    selection_market = loc((By.CSS_SELECTOR, ".betSelectionMarket"))
    selection_odds = loc((By.CSS_SELECTOR, ".betSelectionOdds"))
    balance_display = loc((By.ID, "bet-slip-balance"))
    stake_input = loc((By.ID, "bet-slip-stake-input"))
    potential_payout = loc((By.ID, "bet-slip-potential-payout"))
    place_bet_button = loc((By.ID, "bet-slip-place-bet"))
    empty_state = loc((By.CSS_SELECTOR, ".betSlipBodyEmpty"))

    def teams(self) -> str:
        return self.selection_teams.text()

    def selection_label(self) -> str:
        return self.selection_market.text()

    def odds_value(self) -> float | int:
        text = self.selection_odds.text()
        return float(text.split(":")[1].strip())

    def balance(self) -> float | int:
        return parse_eur_amount(self.balance_display.text())

    def wait_balance(self, expected: float | int, timeout: int = 15) -> None:
        self.balance_display.wait_until_text(
            lambda text: parse_eur_amount(text) == expected,
            timeout,
            description=f"bet slip balance to become {expected}",
        )

    def enter_stake(self, stake: float) -> None:
        self.stake_input.fill(f"{stake:.2f}")

    def payout(self) -> float | int:
        return parse_eur_amount(self.potential_payout.text())

    def place_bet(self) -> None:
        self.wait_place_bet_enabled()
        self.place_bet_button.click()

    def is_placing(self) -> bool:
        return self.place_bet_button.contains_text(PLACING_TEXT)

    def wait_placing_finished(self, timeout: int = 15) -> None:
        self.place_bet_button.wait_text_not_contains(PLACING_TEXT, timeout)

    def is_empty(self) -> bool:
        return self.empty_state.is_visible()

    def verify_bet_details(
        self,
        *,
        teams: tuple[str, str],
        selection: Selection,
        expected_odds: float,
        stake: float,
    ) -> tuple[float, float]:
        home_team, away_team = teams
        check.equal(
            self.teams(),
            format_match_teams(home_team, away_team),
            msg="Bet slip should show home and away teams in correct order",
        )
        check.equal(
            self.selection_label(),
            bet_slip_market_label(selection),
            msg=f"Bet slip should show {selection.value} selection",
        )
        odds = self.odds_value()
        check.equal(odds, expected_odds, msg="Bet slip odds should match selected odds button")
        expected_payout = round_money(stake * odds)
        check.equal(self.payout(), expected_payout, msg="Bet slip payout should equal stake × odds")
        return odds, expected_payout

    def wait_place_bet_enabled(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.place_bet_button.wait_clickable(timeout)
