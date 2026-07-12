from typing import Any

import allure
import pytest
import pytest_check as check

from api.client import SportyAPIClient
from api.models import AuthError, AuthErrorType
from api.models.bets import PlaceBetRequest, Selection
from api.models.errors import Error, ErrorType
from api.models.matches import Match
from api.steps.account import AccountSteps
from constants import MAX_STAKE, MIN_STAKE
from utils.money import round_money

pytestmark = [pytest.mark.api, allure.feature("Single bet placement")]


def _place_bet_body(match: Match, *, drop: str | None = None, **overrides: Any) -> dict[str, Any]:
    """Valid place-bet JSON, optionally missing a field or with invalid overrides."""
    body = PlaceBetRequest(matchId=match.id, selection=Selection.HOME, stake=10.0).model_dump()
    body.update(overrides)
    if drop is not None:
        body.pop(drop)
    return body


class TestPlaceBet:
    """Required automation (TC-01b): place-bet contract and money math at the API layer.

    Chosen because POST /api/place-bet is the financial source of truth - faster and
    more stable than UI; isolates backend defects from frontend rendering issues.
    """

    @allure.story("Contract & money math")
    @pytest.mark.parametrize("selection", [Selection.HOME, Selection.DRAW, Selection.AWAY])
    @allure.title("Place bet succeeds for {selection}")
    def test_place_bet_success(
        self,
        reset_balance,
        selection: Selection,
        betting_match: Match,
        account_steps: AccountSteps,
        authenticated_client: SportyAPIClient,
    ) -> None:
        """TC-01b happy path: POST /api/place-bet contract + money math for each selection.

        For every outcome (HOME/DRAW/AWAY) verifies the echoed fields, that the odds
        match the value advertised for that selection, that payout == stake * odds,
        that the balance is reduced by exactly the stake, and that the returned
        balance is consistent with the persisted GET /api/balance value.
        """
        stake = 10.0
        expected_odds = betting_match.odds_for(selection)
        balance_before = account_steps.current_balance()

        payload = PlaceBetRequest(matchId=betting_match.id, selection=selection, stake=stake)
        result = authenticated_client.bets.post(payload).assert_status(200).value()

        # Echoed request fields (soft checks so all mismatches are reported at once)
        check.equal(result.message, "Bet placed successfully", "unexpected success message")
        check.equal(result.matchId, betting_match.id, "matchId not echoed back correctly")
        check.equal(result.selection, selection, "selection not echoed back correctly")
        check.equal(result.stake, stake, "stake not echoed back correctly")

        # Money math (odds mapping + payout + deduction).
        # Rounding rule is explicit per utils.money.round_money (SPEC-003: spec leaves
        # monetary rounding undefined, so we assume 2 dp, half-up).
        check.equal(result.odds, expected_odds, f"odds must match advertised odds for {selection.value}")
        check.equal(
            result.payout,
            round_money(stake * expected_odds),
            msg=f"payout must equal stake*odds ({stake}*{expected_odds})",
        )
        check.equal(
            result.balance,
            round_money(balance_before - stake),
            msg="balance must be reduced by exactly the stake",
        )

        # place-bet balance must match the persisted balance (both rounded to currency precision, SPEC-003)
        account_balance = account_steps.current_balance()
        check.equal(
            round_money(account_balance),
            round_money(result.balance),
            msg="persisted GET /api/balance must match the place-bet balance",
        )

    @allure.story("Insufficient balance")
    @allure.title("Reject stake greater than available balance")
    @allure.issue("API-005")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.xfail(
        reason="CRITICAL BUG (API-005): overdraft allowed - a stake exceeding the balance succeeds (200) "
        "instead of being rejected with 422 INSUFFICIENT_BALANCE, and the balance can go negative"
    )
    def test_place_bet_rejects_overdraft(
        self,
        drained_balance: float,
        betting_match: Match,
        account_steps: AccountSteps,
        authenticated_client: SportyAPIClient,
    ) -> None:
        """TC-02: a stake greater than the available balance must be rejected, never deduct, and never go negative."""
        remaining = drained_balance

        over_stake = min(MAX_STAKE, round(remaining + 1.0, 2))
        assert over_stake > remaining, "test setup: stake must exceed the remaining balance"
        assert over_stake >= MIN_STAKE, "test setup: stake must be within the valid range"

        over_bet = PlaceBetRequest(matchId=betting_match.id, selection=Selection.HOME, stake=over_stake)
        error = authenticated_client.bets.post(over_bet).validate(422, Error)
        check.equal(error.error, ErrorType.INSUFFICIENT_BALANCE, "overdraft must be rejected as insufficient_balance")

        # A rejected bet must not change the balance, and the balance must never go negative.
        after = account_steps.current_balance()
        check.equal(
            round_money(after),
            round_money(remaining),
            msg="a rejected bet must not change the balance",
        )
        assert after >= 0, f"Balance went negative: {after}"

    @allure.story("Contract & money math")
    @allure.title("Place-bet response currency is EUR")
    @allure.issue("API-006")
    @pytest.mark.xfail(
        reason="BUG (API-006): place-bet returns currency 'USD', while the spec and balance/reset return 'EUR'"
    )
    def test_place_bet_currency_is_eur(
        self, reset_balance, betting_match: Match, authenticated_client: SportyAPIClient
    ) -> None:
        payload = PlaceBetRequest(matchId=betting_match.id, selection=Selection.HOME, stake=10.0)
        result = authenticated_client.bets.post(payload).assert_status(200).value()
        assert result.currency == "EUR", f"currency must be EUR, got {result.currency!r}"

    @allure.story("Payload validation")
    @allure.title("Reject invalid place-bet payloads")
    @pytest.mark.parametrize(
        ("drop", "overrides", "expected_error"),
        [
            ("stake", {}, ErrorType.INVALID_STAKE_TYPE),
            ("selection", {}, ErrorType.INVALID_SELECTION),
            ("matchId", {}, ErrorType.INVALID_MATCH_ID),
            (None, {"matchId": "premier-league-manutd-chelsea' OR 1=1; --"}, ErrorType.INVALID_MATCH),
            (None, {"matchId": "premier-league-manutd-chelsea\u0000' OR '1'='1"}, ErrorType.INVALID_MATCH),
            (None, {"matchId": "premier-league-manutd-chelsea?status=all&limit=1"}, ErrorType.INVALID_MATCH),
            (None, {"matchId": None}, ErrorType.INVALID_MATCH_ID),
            (None, {"selection": "TOTALLY_WRONG_SELECTION"}, ErrorType.INVALID_SELECTION),
            (None, {"selection": "HOME' OR 1=1; --"}, ErrorType.INVALID_SELECTION),
            (None, {"selection": None}, ErrorType.INVALID_SELECTION),
            (None, {"stake": round(MIN_STAKE - 0.01, 2)}, ErrorType.INVALID_STAKE_MIN),
            (None, {"stake": round(MAX_STAKE + 0.01, 2)}, ErrorType.INVALID_STAKE_MAX),
            (None, {"stake": round(MIN_STAKE + 0.123, 3)}, ErrorType.INVALID_STAKE_PRECISION),
            (None, {"stake": True}, ErrorType.INVALID_STAKE_TYPE),
            (None, {"stake": None}, ErrorType.INVALID_STAKE_TYPE),
        ],
    )
    def test_place_bet_rejects_invalid_payload(
        self,
        drop: str | None,
        overrides: dict[str, Any],
        expected_error: ErrorType,
        betting_match: Match,
        authenticated_client: SportyAPIClient,
    ) -> None:
        payload = _place_bet_body(betting_match, drop=drop, **overrides)
        error = authenticated_client.bets.post(payload).validate(422, Error)
        assert error.error == expected_error, (
            f"expected error {expected_error} for payload {payload!r}, got {error.error!r}"
        )


@allure.story("Auth & HTTP")
class TestBetsPlaceProtocol:
    @allure.title("Reject request without x-user-id")
    @pytest.mark.parametrize(
        "user_id,expected_error",
        [
            (None, AuthErrorType.MISSING_USER_ID),
            ("invalid-user-id", AuthErrorType.INVALID_USER_ID),
        ],
    )
    def test_place_bet_requires_auth(
        self, user_id: str | None, expected_error: AuthErrorType, betting_match: Match
    ) -> None:
        with SportyAPIClient(user_id=user_id) as client:
            response = client.bets.post(PlaceBetRequest(matchId=betting_match.id, selection=Selection.HOME, stake=10.0))
            error = response.validate(401, AuthError)
            assert error.error == expected_error, f"expected auth error {expected_error}, got {error.error!r}"

    @allure.title("Unsupported HTTP methods return 405")
    @pytest.mark.parametrize(
        "method,expected_status",
        [
            ("PUT", 405),
            ("DELETE", 405),
            ("TRACE", 405),
        ],
    )
    def test_place_bet_method_not_allowed(
        self, method: str, expected_status: int, authenticated_client: SportyAPIClient
    ) -> None:
        response = authenticated_client.bets.request(method)
        response.assert_status(expected_status)

    @allure.title("GET on place-bet endpoint is not allowed")
    @allure.issue("API-004")
    @pytest.mark.xfail(reason="BUG (API-004): GET /api/place-bet returns 200 instead of 405; the method is not blocked")
    def test_place_bet_get_not_allowed(self, authenticated_client: SportyAPIClient) -> None:
        response = authenticated_client.bets.request("GET")
        response.assert_status(405)

    @allure.title("Reject malformed JSON and non-object bodies")
    @pytest.mark.parametrize(
        "payload,status_code,expected_error_type",
        [
            ([{"param": "value"}], 400, ErrorType.INVALID_REQUEST),
            ('{"key": NaN}', 400, ErrorType.INVALID_JSON),
        ],
    )
    def test_place_bet_rejects_broken_payload_schema(
        self, payload, status_code: int, expected_error_type: ErrorType, authenticated_client: SportyAPIClient
    ) -> None:
        response = authenticated_client.bets.request("POST", json=payload)
        error = response.validate(status_code, Error)
        assert error.error == expected_error_type, (
            f"expected error {expected_error_type} for payload {payload!r}, got {error.error!r}"
        )
