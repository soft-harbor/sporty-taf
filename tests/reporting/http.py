import json
import time
from collections.abc import Callable
from typing import Any

import allure
import requests

from api.endpoints.base import set_http_observer
from api.utils.masking import mask_sensitive_data

HttpObserver = Callable[[str, str, requests.Response, dict[str, Any]], None]


def _safe_json(data: Any) -> str:
    masked = mask_sensitive_data(data)
    return json.dumps(masked, indent=2, ensure_ascii=False, default=str)


def _request_body(kwargs: dict[str, Any]) -> Any:
    if "json" in kwargs:
        return kwargs["json"]
    if "data" in kwargs:
        return kwargs["data"]
    return None


def _short_url(url: str) -> str:
    return url.split("?")[0].rstrip("/")


def attach_http_exchange(method: str, url: str, response: requests.Response, **kwargs: Any) -> None:
    """Attach masked request/response details to the current Allure step."""
    started = kwargs.pop("_started_at", None)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1) if started is not None else None

    request_headers = dict(response.request.headers)
    body = _request_body(kwargs)

    lines = [
        f"{method.upper()} {url}",
        "",
        "=== Request ===",
        f"Headers:\n{_safe_json(dict(request_headers))}",
    ]
    if body is not None:
        lines.append(f"Body:\n{_safe_json(body)}")
    if kwargs.get("params"):
        lines.append(f"Query:\n{_safe_json(kwargs['params'])}")

    lines.extend(
        [
            "",
            "=== Response ===",
            f"Status: {response.status_code}",
            f"Headers:\n{_safe_json(dict(response.headers))}",
        ]
    )
    if elapsed_ms is not None:
        lines.append(f"Duration: {elapsed_ms} ms")

    try:
        payload = response.json()
        lines.append(f"Body:\n{_safe_json(payload)}")
    except ValueError:
        text = response.text.strip()
        if text:
            lines.append(f"Body:\n{text[:4000]}")

    attachment = "\n".join(lines)
    name = f"{method.upper()} {_short_url(url)} → {response.status_code}"
    allure.attach(attachment, name=name, attachment_type=allure.attachment_type.TEXT)


def register_http_logging(observer: HttpObserver | None = attach_http_exchange) -> None:
    set_http_observer(observer)
