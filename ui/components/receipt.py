from typing import Self

from pytest_check import check
from selenium.webdriver.common.by import By

from api.models.selection import Selection
from ui.core.base_component import BaseComponent
from ui.core.locators import loc
from ui.core.timeouts import DEFAULT_TIMEOUT
from ui.helpers import format_match_teams, parse_eur_amount


class Receipt(BaseComponent):
    # UI-010: receipt does not render the placed selection; no locator to assert against yet.
    modal_root = loc((By.CSS_SELECTOR, ".modalRoot"))
    bet_id_value = loc((By.ID, "modal-success-bet-id"))
    match_value = loc((By.ID, "modal-success-match"))
    stake_value = loc((By.ID, "modal-success-stake"))
    odds_value = loc((By.ID, "modal-success-odds"))
    payout_value = loc((By.ID, "modal-success-payout"))
    placed_at_value = loc((By.ID, "modal-success-placed-at"))
    close_button = loc((By.ID, "modal-success-close"))

    def bet_id(self) -> str:
        return self.bet_id_value.text()

    def teams(self) -> str:
        return self.match_value.text()

    def stake(self) -> float:
        return parse_eur_amount(self.stake_value.text())

    def odds(self) -> float:
        return float(self.odds_value.text())

    def payout(self) -> float:
        return parse_eur_amount(self.payout_value.text())

    def placed_at(self) -> str:
        return self.placed_at_value.text()

    def wait_open(self, timeout: int = DEFAULT_TIMEOUT) -> Self:
        self.modal_root.wait_visible(timeout)
        return self

    def verify_bet_placement(
        self,
        *,
        teams: tuple[str, str],
        selection: Selection,
        stake: float,
        odds: float,
        expected_payout: float,
    ) -> None:
        """Assert receipt fields match the placed bet (soft checks via pytest-check).

        :param teams: Home and away team names.
        :param selection: Placed outcome (HOME / DRAW / AWAY).
        :param stake: Stake amount entered in the bet slip.
        :param odds: Odds locked in at placement.
        :param expected_payout: stake × odds, rounded per app rules.
        """
        home_team, away_team = teams
        receipt_shown = False
        try:
            self.wait_open()
            receipt_shown = True
        except Exception:
            pass
        check.is_true(receipt_shown, msg="Success receipt should be displayed")
        check.is_true(self.bet_id(), msg="Receipt should contain bet id")
        check.equal(
            self.teams(),
            format_match_teams(home_team, away_team),
            msg="UI-010: receipt should show home and away teams in correct order",
        )
        check.fail(
            f"UI-010: receipt has no selector for placed selection ({selection.value}); outcome cannot be verified on receipt"
        )
        check.equal(self.stake(), stake, msg="Receipt stake should match entered stake")
        check.equal(self.odds(), odds, msg="Receipt odds should match odds at placement")
        check.equal(
            self.payout(),
            expected_payout,
            msg="UI-012: receipt payout should equal stake × odds, not a hardcoded multiplier",
        )
        bet_id = self.bet_id()
        # TODO(API): GET /api/bets/{betId} - fetch placedAt from backend and compare with self.placed_at().
        check.fail(
            f"UI-010: placedAt cannot be verified without API lookup by bet id ({bet_id}); "
            "waiting for GET /api/bets/{{betId}} contract"
        )

    def close(self) -> None:
        self.close_button.click()
