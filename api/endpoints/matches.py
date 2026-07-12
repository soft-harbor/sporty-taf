from api.endpoints.base import BaseEndpoint
from api.models.api_response import ApiResponse
from api.models.matches import Match


class MatchesEndpoint(BaseEndpoint):
    base_path = "/api/matches"

    def get(self) -> ApiResponse[list[Match]]:
        return self.request("GET", self.base_path, response_model=list[Match])
