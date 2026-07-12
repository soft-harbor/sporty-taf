from functools import cached_property
from typing import Self

import requests

from api.endpoints.balance import BalanceEndpoint, ResetBalanceEndpoint
from api.endpoints.bets import BetsEndpoint
from api.endpoints.matches import MatchesEndpoint

REQUESTS_TIMEOUT = 10.0


def _create_client(user_id: str | None) -> requests.Session:
    session = requests.Session()
    if user_id is not None:
        session.headers["x-user-id"] = user_id
    session.timeout = REQUESTS_TIMEOUT
    return session


class SportyAPIClient:
    def __init__(self, user_id: str | None = None, *, client: requests.Session | None = None):
        self._client = client or _create_client(user_id)

    @cached_property
    def matches(self) -> MatchesEndpoint:
        return MatchesEndpoint(self._client)

    @cached_property
    def bets(self) -> BetsEndpoint:
        return BetsEndpoint(self._client)

    @cached_property
    def balance(self) -> BalanceEndpoint:
        return BalanceEndpoint(self._client)

    @cached_property
    def reset_balance(self) -> ResetBalanceEndpoint:
        return ResetBalanceEndpoint(self._client)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc) -> None:
        self.close()
