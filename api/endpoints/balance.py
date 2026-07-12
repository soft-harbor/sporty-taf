from api.endpoints.base import BaseEndpoint
from api.models.api_response import ApiResponse
from api.models.balance import Balance


class BalanceEndpoint(BaseEndpoint):
    base_path = "/api/balance"

    def get(self) -> ApiResponse[Balance]:
        return self.request("GET", self.base_path, response_model=Balance)


class ResetBalanceEndpoint(BaseEndpoint):
    base_path = "/api/reset-balance"

    def post(self) -> ApiResponse[Balance]:
        return self.request("POST", self.base_path, response_model=Balance)
