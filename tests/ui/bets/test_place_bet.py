import allure
import pytest
from allure import step
from pytest_check import check

from api.models.selection import Selection
from api.steps.account import AccountSteps
from ui.app import App
from utils.money import round_money


@pytest.mark.ui
@allure.feature("Single bet placement")
@allure.story("Place a valid single bet (E2E)")
class TestPlaceBet:
    """Required automation (TC-01): core revenue flow across UI and API balance.

    Chosen because stake deduction, payout display, and receipt checks are the
    highest business-risk checks - a single E2E run exercises money movement end-to-end.
    """

    @allure.title("Happy path: select odds → bet slip → place → receipt")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_happy_path_bet_to_receipt(self, app: App, account_steps: AccountSteps) -> None:
        page = app.betting_page
        initial_balance = account_steps.current_balance()

        with step("Open page and verify initial balance"):
            page.navigate()
            page.header.wait_balance(initial_balance)
            assert page.header.balance() == initial_balance, "Header balance should match API after page load"

        with step("Select upcoming match and HOME odds"):
            match_cards = page.match_cards
            assert len(match_cards) > 0, "At least one match card should be visible"

            past_cards = [card for card in match_cards if not card.is_upcoming()]
            with step("Assert match list has no past matches (UI-001)"):
                check.equal(
                    len(past_cards),
                    0,
                    f"UI-001: past matches must not appear in the list (found {len(past_cards)})",
                )

            upcoming_cards = [card for card in match_cards if card.is_upcoming()]
            check.greater(
                len(upcoming_cards),
                0,
                "UI-001: at least one upcoming match should be available for betting",
            )
            match_card = upcoming_cards[0]
            home_team, away_team, selection = match_card.home_team(), match_card.away_team(), Selection.HOME
            match_card.select_odds(selection)

        with step("Enter stake and verify bet slip"):
            bet_slip = page.bet_slip
            stake = min(10.00, initial_balance)
            bet_slip.enter_stake(stake)
            odds, expected_payout = bet_slip.verify_bet_details(
                teams=(home_team, away_team),
                selection=selection,
                expected_odds=match_card.odds_for(selection),
                stake=stake,
            )

        with step("Place bet and verify receipt"):
            bet_slip.place_bet()
            bet_slip.wait_placing_finished()

            receipt = page.receipt
            receipt.verify_bet_placement(
                teams=(home_team, away_team),
                selection=selection,
                stake=stake,
                odds=odds,
                expected_payout=expected_payout,
            )
            receipt.close()

        with step("Verify post-bet UI and API balance"):
            check.is_true(bet_slip.is_empty(), "Bet slip should be empty after closing receipt")
            check.is_false(page.has_selected_odds(), "Match list should have no active selection after closing receipt")

            expected_balance = round_money(initial_balance - stake)
            check.equal(
                account_steps.current_balance(),
                expected_balance,
                "API balance should be reduced by stake amount",
            )
            check.equal(
                page.header.balance(),
                expected_balance,
                "UI-011: header balance should refresh after successful bet placement",
            )
            check.equal(
                bet_slip.balance(),
                expected_balance,
                "UI-011: bet slip balance should refresh after successful bet placement",
            )
