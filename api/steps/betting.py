from api.client import SportyAPIClient
from api.models.bets import PlaceBetRequest
from api.models.selection import Selection
from api.steps.account import AccountSteps
from constants import MAX_STAKE


class BettingSteps:
    def __init__(self, client: SportyAPIClient) -> None:
        self._client = client
        self.account = AccountSteps(client)

    def drain_below_max_stake(self, match_id: str, max_stake: float = MAX_STAKE) -> float:
        """Place max-stake bets until the remaining balance drops below max_stake.

        Returns the remaining balance, guaranteed to be smaller than a max-stake bet,
        so a valid-range stake can still exceed it (used to exercise the
        insufficient-balance / overdraft path).
        """
        balance = self.account.current_balance()
        while balance >= max_stake:
            drain = PlaceBetRequest(matchId=match_id, selection=Selection.HOME, stake=max_stake)
            balance = self._client.bets.post(drain).assert_status(200).value().balance
        return balance

    def placed_at_for_bet(self, bet_id: str) -> str:
        """Return the canonical placement timestamp for a bet (backend source of truth)."""
        # TODO(API): GET /api/bets/{betId} - not in OpenAPI v1.0.0 yet.
        raise NotImplementedError(
            f"Bet lookup by id is not available yet (bet_id={bet_id!r}); add GET /api/bets/{{betId}} to the API contract"
        )
