from api.client import SportyAPIClient
from api.models.balance import Balance


class AccountSteps:
    def __init__(self, client: SportyAPIClient) -> None:
        self._client = client

    def reset_balance(self) -> Balance:
        return self._client.reset_balance.post().value()

    def current_balance(self) -> float:
        return self._client.balance.get().assert_status(200).value().balance
