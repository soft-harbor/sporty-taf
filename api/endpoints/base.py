import time
from collections.abc import Callable
from typing import Any
from urllib.parse import urljoin

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from api.models.api_response import ApiResponse
from base_settings import settings

RETRYABLE = (requests.exceptions.Timeout, requests.exceptions.ConnectionError)

HttpObserver = Callable[[str, str, requests.Response, dict[str, Any]], None]
_http_observer: HttpObserver | None = None


def set_http_observer(observer: HttpObserver | None) -> None:
    global _http_observer
    _http_observer = observer


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
    retry=retry_if_exception_type(RETRYABLE),
)
def _send(client: requests.Session, method: str, url: str, **kwargs: Any) -> requests.Response:
    return client.request(method, url, **kwargs)


class BaseEndpoint:
    base_path: str = ""
    base_url: str = settings.backend_base_url

    def __init__(self, client: requests.Session):
        self._client = client

    def request[T](
        self, method: str, path: str = "", *, response_model: type[T] | None = None, **kwargs: Any
    ) -> ApiResponse[T]:
        url = path or self.base_path
        full_url = urljoin(self.base_url, url)
        started_at = time.perf_counter()
        response = _send(self._client, method, full_url, **kwargs)
        if _http_observer is not None:
            observer_kwargs = {**kwargs, "_started_at": started_at}
            _http_observer(method, full_url, response, **observer_kwargs)
        return ApiResponse(response, response_model)
