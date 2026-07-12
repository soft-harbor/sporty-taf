from collections.abc import Generator, Iterator
from datetime import date

import pytest

from api.client import SportyAPIClient
from api.models.matches import Match
from api.steps.account import AccountSteps
from api.steps.betting import BettingSteps
from base_settings import settings


class MatchCatalog:
    """Rotates through live matches from GET /api/matches (furthest kickoff first).

    Re-fetches when the pool runs out so tests can share one user without hardcoded match ids.
    """

    def __init__(self, client: SportyAPIClient) -> None:
        self._client = client
        self._iterator: Iterator[Match] | None = None

    def _fetch_pool(self) -> list[Match]:
        matches = self._client.matches.get().value()
        if not matches:
            pytest.fail("GET /api/matches returned no matches - cannot run bet tests")
        upcoming = [m for m in matches if m.kickoffDate is None or m.kickoffDate >= date.today()]
        return list(reversed(upcoming or matches))

    def _stream(self) -> Iterator[Match]:
        while True:
            yield from self._fetch_pool()

    def next_match(self) -> Match:
        if self._iterator is None:
            self._iterator = self._stream()
        return next(self._iterator)


@pytest.fixture(scope="session")
def match_catalog() -> Generator[MatchCatalog]:
    with SportyAPIClient(user_id=settings.sporty_test_user_id) as client:
        yield MatchCatalog(client)


@pytest.fixture
def betting_match(match_catalog: MatchCatalog) -> Match:
    """A real match from the API (furthest kickoff first), one per test."""
    return match_catalog.next_match()


@pytest.fixture
def authenticated_client() -> Generator[SportyAPIClient]:
    with SportyAPIClient(user_id=settings.sporty_test_user_id) as client:
        yield client


@pytest.fixture
def account_steps(authenticated_client: SportyAPIClient) -> AccountSteps:
    return AccountSteps(authenticated_client)


@pytest.fixture
def betting_steps(authenticated_client: SportyAPIClient) -> BettingSteps:
    return BettingSteps(authenticated_client)


@pytest.fixture
def reset_balance(account_steps: AccountSteps) -> None:
    account_steps.reset_balance()


@pytest.fixture
def drained_balance(reset_balance, betting_steps: BettingSteps, match_catalog: MatchCatalog) -> float:
    """Remaining balance after draining it below the max stake, so a valid-range stake can exceed it.

    NOTE: In a real-world scenario the balance would be provisioned explicitly via a
    dedicated test/seeding API (e.g. set a known low balance for a freshly created
    user). The app under test only exposes `reset-balance` (a fixed value), so here we
    simulate a low balance by placing max-stake bets until the remainder drops below it.
    """
    match_id = match_catalog.next_match().id
    return betting_steps.drain_below_max_stake(match_id)
