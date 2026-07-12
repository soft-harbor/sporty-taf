from typing import Any

from api.endpoints.base import BaseEndpoint
from api.models.api_response import ApiResponse
from api.models.bets import PlaceBetRequest, PlaceBetResponse

# A place-bet request can be passed either as a validated model or as a raw dict
# (e.g. negative/validation tests that send intentionally malformed bodies).
Payload = PlaceBetRequest | dict[str, Any]


class BetsEndpoint(BaseEndpoint):
    base_path = "/api/place-bet"

    def post(self, payload: Payload) -> ApiResponse[PlaceBetResponse]:
        body = payload.model_dump() if isinstance(payload, PlaceBetRequest) else payload
        return self.request("POST", self.base_path, json=body, response_model=PlaceBetResponse)
