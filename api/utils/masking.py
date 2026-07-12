import re
from typing import Any

SENSITIVE_KEYS = {"authorization", "token", "password", "secret", "api_key", "cookie"}


def mask_sensitive_data(data: Any) -> Any:
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if str(key).lower() in SENSITIVE_KEYS:
                masked[key] = "[MASKED]"
            else:
                masked[key] = mask_sensitive_data(value)
        return masked
    if isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]

    if isinstance(data, str) and re.search(r"Bearer\s+\S+", data, re.IGNORECASE):
        return "Bearer [MASKED]"

    return data
